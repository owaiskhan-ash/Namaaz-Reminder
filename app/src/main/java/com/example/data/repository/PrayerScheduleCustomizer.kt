package com.example.data.repository

import com.example.data.model.PrayerScheduleData
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale
import java.util.TimeZone

/** Applies date-specific user prayer-time overrides to fetched and cached schedules. */
object PrayerScheduleCustomizer {

    fun dateKey(schedule: PrayerScheduleData, nowMillis: Long = System.currentTimeMillis()): String =
        SimpleDateFormat("yyyy-MM-dd", Locale.US).apply {
            timeZone = TimeZone.getTimeZone(schedule.timezone)
        }.format(Date(nowMillis))

    fun customTimeKey(
        schedule: PrayerScheduleData,
        type: PrayerType,
        nowMillis: Long = System.currentTimeMillis()
    ): String = "${dateKey(schedule, nowMillis)}|${schedule.city.trim().lowercase(Locale.ROOT)}|${type.name}"

    fun apply(
        schedule: PrayerScheduleData,
        settings: UserSettings,
        nowMillis: Long = System.currentTimeMillis()
    ): PrayerScheduleData {
        val timeZone = TimeZone.getTimeZone(schedule.timezone)
        val todayPrayers = schedule.prayers.map { prayer ->
            val customTime = if (prayer.type.isPrimaryPrayer) {
                settings.customPrayerTimes[customTimeKey(schedule, prayer.type, nowMillis)]
            } else {
                null
            }
            val (hour, minute) = parseClockTime(customTime ?: prayer.rawTime)
            val target = Calendar.getInstance(timeZone).apply {
                timeInMillis = nowMillis
                set(Calendar.HOUR_OF_DAY, hour)
                set(Calendar.MINUTE, minute)
                set(Calendar.SECOND, 0)
                set(Calendar.MILLISECOND, 0)
            }.timeInMillis

            prayer.copy(
                targetEpochMillis = target,
                customTime = customTime,
                isPassed = target <= nowMillis,
                isNext = false,
                notificationEnabled = !settings.mutedPrayerNames.contains(prayer.type.name)
            )
        }

        val nextPrayerIndex = todayPrayers.indexOfFirst {
            it.type.isPrimaryPrayer && it.targetEpochMillis > nowMillis
        }
        val resolvedPrayers = if (nextPrayerIndex >= 0) {
            todayPrayers.mapIndexed { index, prayer ->
                prayer.copy(isNext = index == nextPrayerIndex)
            }
        } else {
            val fajrIndex = todayPrayers.indexOfFirst { it.type == PrayerType.FAJR }
            if (fajrIndex < 0) {
                todayPrayers
            } else {
                val fajr = todayPrayers[fajrIndex]
                val (fajrHour, fajrMinute) = parseClockTime(fajr.rawTime)
                val tomorrowFajr = Calendar.getInstance(timeZone).apply {
                    timeInMillis = nowMillis
                    add(Calendar.DAY_OF_YEAR, 1)
                    set(Calendar.HOUR_OF_DAY, fajrHour)
                    set(Calendar.MINUTE, fajrMinute)
                    set(Calendar.SECOND, 0)
                    set(Calendar.MILLISECOND, 0)
                }.timeInMillis
                todayPrayers.mapIndexed { index, prayer ->
                    if (index == fajrIndex) {
                        prayer.copy(
                            targetEpochMillis = tomorrowFajr,
                            isNext = true,
                            isPassed = false,
                            customTime = null
                        )
                    } else {
                        prayer.copy(isNext = false)
                    }
                }
            }
        }

        return schedule.copy(prayers = resolvedPrayers)
    }

    private fun parseClockTime(value: String): Pair<Int, Int> {
        val parts = value.split(":")
        val hour = parts.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: 12
        val minute = parts.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: 0
        return hour to minute
    }
}
