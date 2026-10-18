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
        mutedPrayers: Set<String> = emptySet(),
        customTimes: Map<String, String> = emptyMap()
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
                            cacheTime = System.currentTimeMillis(),
                            customTimes = customTimes
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
                    cacheTime = timestamp,
                    customTimes = customTimes
                )
                return@withContext Result.success(cachedSchedule)
            } catch (e: Exception) {
                // If cache corrupted, continue to error
            }
        }

        // If no cache for this city, try finding any cached city as a fallback
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
        cacheTime: Long,
        customTimes: Map<String, String> = emptyMap()
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

        val readableDate = dateObj.optString("readable", "")
        val gregorianWeekday = gregorianObj?.optJSONObject("weekday")?.optString("en", "") ?: ""
        val gregorianDay = gregorianObj?.optString("day", "") ?: ""
        val gregorianMonth = gregorianObj?.optJSONObject("month")?.optString("en", "") ?: ""
        val gregorianYear = gregorianObj?.optString("year", "") ?: ""
        val formattedGregorian = if (gregorianWeekday.isNotEmpty()) {
            "$gregorianWeekday, $gregorianDay $gregorianMonth $gregorianYear"
        } else {
            readableDate
        }

        val hijriDay = hijriObj?.optString("day", "") ?: ""
        val hijriMonth = hijriObj?.optJSONObject("month")?.optString("en", "") ?: ""
        val hijriYear = hijriObj?.optString("year", "") ?: ""
        val formattedHijri = if (hijriDay.isNotEmpty()) {
            "$hijriDay $hijriMonth $hijriYear AH"
        } else {
            ""
        }

        val methodName = metaObj?.optJSONObject("method")?.optString("name")
            ?: "Karachi (Univ. of Islamic Sciences)"

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

        val prayerItems = withTomorrowFajrIfNeeded(
            buildPrayerItems(
                timeZone = tz,
                entries = prayerEntries,
                mutedPrayers = mutedPrayers,
                customTimes = customTimes,
                nowMillis = nowMillis
            ).toMutableList(),
            timeZone = tz
        )

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

    /**
     * Re-applies the times the user set by hand to an already loaded schedule,
     * so the countdown and the reminders pick them up immediately.
     */
    fun applyCustomTimes(
        schedule: PrayerScheduleData,
        customTimes: Map<String, String>
    ): PrayerScheduleData {
        val timeZone = TimeZone.getTimeZone(schedule.timezone)
        val entries = schedule.prayers.map { it.type to it.rawTime }
        val muted = schedule.prayers.filter { !it.notificationEnabled }.map { it.type.name }.toSet()
        val items = withTomorrowFajrIfNeeded(
            buildPrayerItems(
                timeZone = timeZone,
                entries = entries,
                mutedPrayers = muted,
                customTimes = customTimes,
                nowMillis = System.currentTimeMillis()
            ).toMutableList(),
            timeZone = timeZone
        )
        return schedule.copy(prayers = items)
    }

    /**
     * Builds the prayer items. A time the user set by hand overrides the
     * calculated one and is used for the countdown and the reminders.
     */
    private fun buildPrayerItems(
        timeZone: TimeZone,
        entries: List<Pair<PrayerType, String>>,
        mutedPrayers: Set<String>,
        customTimes: Map<String, String>,
        nowMillis: Long
    ): List<PrayerItem> {
        var foundNext = false
        val items = mutableListOf<PrayerItem>()

        for ((type, rawValue) in entries) {
            val cleaned = cleanTime(rawValue)
            val (hour, minute) = parseHoursMinutes(cleaned)
            val targetMillis = epochFor(timeZone, hour, minute)

            val customRaw = customTimes[type.name]?.trim()
            var customMillis: Long? = null
            var custom12: String? = null
            var custom24: String? = null
            if (!customRaw.isNullOrEmpty()) {
                val (customHour, customMinute) = parseHoursMinutes(customRaw)
                customMillis = epochFor(timeZone, customHour, customMinute)
                custom12 = format12Hour(customHour, customMinute)
                custom24 = String.format(Locale.US, "%02d:%02d", customHour, customMinute)
            }

            val effectiveMillis = customMillis ?: targetMillis
            val isPassed = nowMillis > effectiveMillis
            val isNext = if (type.isPrimaryPrayer && !isPassed && !foundNext) {
                foundNext = true
                true
            } else {
                false
            }

            items.add(
                PrayerItem(
                    type = type,
                    rawTime = cleaned,
                    formattedTime12 = format12Hour(hour, minute),
                    formattedTime24 = String.format(Locale.US, "%02d:%02d", hour, minute),
                    targetEpochMillis = targetMillis,
                    isNext = isNext,
                    isPassed = isPassed,
                    notificationEnabled = !mutedPrayers.contains(type.name),
                    customRawTime = customRaw,
                    customFormattedTime12 = custom12,
                    customFormattedTime24 = custom24,
                    customEpochMillis = customMillis
                )
            )
        }
        return items
    }

    /** When every prayer of today has passed, tomorrow's Fajr is the next one. */
    private fun withTomorrowFajrIfNeeded(
        items: MutableList<PrayerItem>,
        timeZone: TimeZone
    ): List<PrayerItem> {
        if (items.any { it.isNext }) return items
        val fajrIndex = items.indexOfFirst { it.type == PrayerType.FAJR }
        if (fajrIndex == -1) return items

        val oldFajr = items[fajrIndex]
        val (hour, minute) = parseHoursMinutes(oldFajr.customRawTime ?: oldFajr.rawTime)
        val tomorrowCal = Calendar.getInstance(timeZone).apply {
            add(Calendar.DAY_OF_YEAR, 1)
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }
        val tomorrowMillis = tomorrowCal.timeInMillis
        items[fajrIndex] = oldFajr.copy(
            targetEpochMillis = tomorrowMillis,
            customEpochMillis = if (oldFajr.hasCustomTime) tomorrowMillis else null,
            isNext = true,
            isPassed = false
        )
        return items
    }

    /** Cleans time strings (e.g. "05:05 (IST)" -> "05:05"). */
    private fun cleanTime(raw: String): String {
        val parts = raw.trim().split(" ")
        return parts.firstOrNull() ?: raw
    }

    /** The epoch of the given wall clock time in the given time zone. */
    private fun epochFor(timeZone: TimeZone, hour: Int, minute: Int): Long =
        Calendar.getInstance(timeZone).apply {
            set(Calendar.HOUR_OF_DAY, hour)
            set(Calendar.MINUTE, minute)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }.timeInMillis

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
