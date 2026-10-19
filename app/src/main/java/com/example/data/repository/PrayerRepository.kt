package com.example.data.repository

import com.example.data.local.PreferencesManager
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.PrayerType
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale
import java.util.TimeZone
import java.util.concurrent.TimeUnit

class PrayerRepository(
    private val preferencesManager: PreferencesManager,
    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .followRedirects(true)
        .followSslRedirects(true)
        .build()
) {

    /**
     * Fetches today's prayer schedule, always trying the network first and
     * falling back to the locally cached payload when offline.
     *
     * Note on cache staleness: cached payloads are re-anchored to the current
     * day when parsed (see [parseJsonResponse]), so timings can be off by a
     * minute or two if the cache is several days old. [PrayerScheduleData]
     * carries `isOfflineCache`/`cachedAtMillis` so the UI can surface the
     * cache age to the user.
     */
    suspend fun getPrayerSchedule(
        city: String,
        methodId: Int,
        mutedPrayers: Set<String> = emptySet()
    ): Result<PrayerScheduleData> = withContext(Dispatchers.IO) {
        val cleanCity = city.trim().ifEmpty { "Delhi" }

        // Try network request first
        var networkException: Exception? = null
        try {
            val encodedCity = java.net.URLEncoder.encode(cleanCity, "UTF-8")
            val url = "https://api.aladhan.com/v1/timingsByCity?city=$encodedCity&country=India&method=$methodId"

            val request = Request.Builder()
                .url(url)
                .header("User-Agent", "NamazTimesAndroidApp/1.0")
                .build()

            client.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    val bodyString = response.body?.string()
                    if (!bodyString.isNullOrBlank()) {
                        val schedule = parseJsonResponse(
                            jsonStr = bodyString,
                            city = cleanCity,
                            methodId = methodId,
                            mutedPrayers = mutedPrayers,
                            isOffline = false,
                            cacheTime = System.currentTimeMillis()
                        )
                        // Save to cache
                        preferencesManager.saveCachedScheduleJson(cleanCity, methodId, bodyString)
                        return@withContext Result.success(schedule)
                    }
                }
            }
        } catch (e: Exception) {
            networkException = e
        }

        // Network failed or returned invalid response -> Fallback to local cache
        val (cachedJson, timestamp) = preferencesManager.getCachedScheduleJson(cleanCity, methodId)
        if (!cachedJson.isNullOrBlank()) {
            try {
                val cachedSchedule = parseJsonResponse(
                    jsonStr = cachedJson,
                    city = cleanCity,
                    methodId = methodId,
                    mutedPrayers = mutedPrayers,
                    isOffline = true,
                    cacheTime = timestamp
                )
                return@withContext Result.success(cachedSchedule)
            } catch (e: Exception) {
                // If cache corrupted, continue to error
            }
        }

        // No cache for this city and the network failed.
        Result.failure(
            networkException ?: IllegalStateException("Unable to fetch prayer times for $cleanCity. Check internet connection.")
        )
    }

    fun parseJsonResponse(
        jsonStr: String,
        city: String,
        methodId: Int,
        mutedPrayers: Set<String>,
        isOffline: Boolean,
        cacheTime: Long
    ): PrayerScheduleData {
        val root = JSONObject(jsonStr)
        val dataObj = root.getJSONObject("data")
        val timingsObj = dataObj.getJSONObject("timings")
        val dateObj = dataObj.getJSONObject("date")
        val metaObj = dataObj.optJSONObject("meta")

        val timezoneStr = metaObj?.optString("timezone") ?: "Asia/Kolkata"
        val tz = TimeZone.getTimeZone(timezoneStr)

        val gregorianObj = dateObj.optJSONObject("gregorian")
        val hijriObj = dateObj.optJSONObject("hijri")

        // The payload describes the day it was fetched, while the timings below
        // are re-anchored to today. Deriving the date line from the device clock
        // keeps a cached schedule from showing an old date above today's times.
        val todayCal = Calendar.getInstance(tz)
        val formattedGregorian = SimpleDateFormat("EEEE, d MMMM yyyy", Locale.ENGLISH)
            .apply { timeZone = tz }
            .format(todayCal.time)

        // A Hijri date cannot be derived from java.util.Calendar, so it is shown
        // only when the payload really describes today - a stale Hijri date
        // would be worse than none.
        val hijriDay = hijriObj?.optString("day", "") ?: ""
        val hijriMonth = hijriObj?.optJSONObject("month")?.optString("en", "") ?: ""
        val hijriYear = hijriObj?.optString("year", "") ?: ""
        val todayMonthName = SimpleDateFormat("MMMM", Locale.ENGLISH)
            .apply { timeZone = tz }
            .format(todayCal.time)
        val payloadIsToday = gregorianObj != null &&
            gregorianObj.optString("day", "").toIntOrNull() == todayCal.get(Calendar.DAY_OF_MONTH) &&
            gregorianObj.optString("year", "").toIntOrNull() == todayCal.get(Calendar.YEAR) &&
            gregorianObj.optJSONObject("month")?.optString("en", "")
                ?.equals(todayMonthName, ignoreCase = true) == true
        val formattedHijri = if (payloadIsToday && hijriDay.isNotEmpty()) {
            "$hijriDay $hijriMonth $hijriYear AH"
        } else {
            ""
        }

        val methodName = metaObj?.optJSONObject("method")?.optString("name")
            ?: "Karachi (Univ. of Islamic Sciences)"

        // Clean time strings (e.g. "05:05 (IST)" -> "05:05")
        fun cleanTime(raw: String): String {
            val parts = raw.trim().split(" ")
            return parts.firstOrNull() ?: raw
        }

        val nowMillis = System.currentTimeMillis()

        // Create prayer items
        val prayerEntries = listOf(
            PrayerType.FAJR to timingsObj.optString("Fajr", "05:00"),
            PrayerType.SUNRISE to timingsObj.optString("Sunrise", "06:15"),
            PrayerType.DHUHR to timingsObj.optString("Dhuhr", "12:15"),
            PrayerType.ASR to timingsObj.optString("Asr", "15:30"),
            PrayerType.SUNSET to timingsObj.optString("Sunset", "17:50"),
            PrayerType.MAGHRIB to timingsObj.optString("Maghrib", "17:50"),
            PrayerType.ISHA to timingsObj.optString("Isha", "19:15")
        )

        var foundNext = false
        val prayerItems = mutableListOf<PrayerItem>()

        for ((type, rawVal) in prayerEntries) {
            val cleaned = cleanTime(rawVal)
            val (h, m) = parseHoursMinutes(cleaned)

            val pCal = Calendar.getInstance(tz).apply {
                set(Calendar.HOUR_OF_DAY, h)
                set(Calendar.MINUTE, m)
                set(Calendar.SECOND, 0)
                set(Calendar.MILLISECOND, 0)
            }
            val targetMillis = pCal.timeInMillis
            val isPassed = nowMillis > targetMillis

            val isNext = if (type.isPrimaryPrayer && !isPassed && !foundNext) {
                foundNext = true
                true
            } else {
                false
            }

            val formatted12 = format12Hour(h, m)
            val formatted24 = String.format(Locale.US, "%02d:%02d", h, m)

            prayerItems.add(
                PrayerItem(
                    type = type,
                    rawTime = cleaned,
                    formattedTime12 = formatted12,
                    formattedTime24 = formatted24,
                    targetEpochMillis = targetMillis,
                    isNext = isNext,
                    isPassed = isPassed,
                    notificationEnabled = !mutedPrayers.contains(type.name)
                )
            )
        }

        // If all prayers today passed, Fajr tomorrow is next!
        if (!foundNext) {
            val fajrIndex = prayerItems.indexOfFirst { it.type == PrayerType.FAJR }
            if (fajrIndex != -1) {
                val oldFajr = prayerItems[fajrIndex]
                val (fh, fm) = parseHoursMinutes(oldFajr.rawTime)
                val tomorrowCal = Calendar.getInstance(tz).apply {
                    add(Calendar.DAY_OF_YEAR, 1)
                    set(Calendar.HOUR_OF_DAY, fh)
                    set(Calendar.MINUTE, fm)
                    set(Calendar.SECOND, 0)
                    set(Calendar.MILLISECOND, 0)
                }
                prayerItems[fajrIndex] = oldFajr.copy(
                    targetEpochMillis = tomorrowCal.timeInMillis,
                    isNext = true,
                    isPassed = false
                )
            }
        }

        return PrayerScheduleData(
            city = city,
            country = "India",
            methodId = methodId,
            methodName = methodName,
            dateGregorian = formattedGregorian,
            dateHijri = formattedHijri,
            timezone = timezoneStr,
            prayers = prayerItems,
            isOfflineCache = isOffline,
            cachedAtMillis = cacheTime
        )
    }

    private fun parseHoursMinutes(timeStr: String): Pair<Int, Int> {
        return try {
            val parts = timeStr.split(":")
            Pair(parts[0].trim().toInt(), parts[1].trim().toInt())
        } catch (e: Exception) {
            Pair(12, 0)
        }
    }

    private fun format12Hour(hour24: Int, minutes: Int): String {
        val amPm = if (hour24 >= 12) "PM" else "AM"
        val hour12 = when (hour24 % 12) {
            0 -> 12
            else -> hour24 % 12
        }
        return String.format(Locale.US, "%d:%02d %s", hour12, minutes, amPm)
    }
}
