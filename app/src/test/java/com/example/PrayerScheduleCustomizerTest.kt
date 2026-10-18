package com.example

import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import com.example.data.repository.PrayerScheduleCustomizer
import java.util.Calendar
import java.util.TimeZone
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PrayerScheduleCustomizerTest {

    @Test
    fun `today custom time updates next prayer and target epoch`() {
        val timezone = TimeZone.getTimeZone("Asia/Kolkata")
        val now = Calendar.getInstance(timezone).apply {
            set(2026, Calendar.OCTOBER, 18, 4, 0, 0)
            set(Calendar.MILLISECOND, 0)
        }.timeInMillis
        val settings = UserSettings(
            customPrayerTimes = mapOf("2026-10-18|mumbai|FAJR" to "05:25")
        )

        val customized = PrayerScheduleCustomizer.apply(sampleSchedule(), settings, now)
        val fajr = customized.prayers.first { it.type == PrayerType.FAJR }

        assertEquals("05:25", fajr.customTime)
        assertTrue(fajr.isNext)
        assertFalse(fajr.isPassed)
        assertEquals(5, Calendar.getInstance(timezone).apply {
            timeInMillis = fajr.targetEpochMillis
        }.get(Calendar.HOUR_OF_DAY))
        assertEquals(25, Calendar.getInstance(timezone).apply {
            timeInMillis = fajr.targetEpochMillis
        }.get(Calendar.MINUTE))
    }

    @Test
    fun `passed custom Fajr does not remain next`() {
        val timezone = TimeZone.getTimeZone("Asia/Kolkata")
        val now = Calendar.getInstance(timezone).apply {
            set(2026, Calendar.OCTOBER, 18, 6, 0, 0)
            set(Calendar.MILLISECOND, 0)
        }.timeInMillis
        val settings = UserSettings(
            customPrayerTimes = mapOf("2026-10-18|mumbai|FAJR" to "05:25")
        )

        val customized = PrayerScheduleCustomizer.apply(sampleSchedule(), settings, now)
        val fajr = customized.prayers.first { it.type == PrayerType.FAJR }
        val dhuhr = customized.prayers.first { it.type == PrayerType.DHUHR }

        assertTrue(fajr.isPassed)
        assertFalse(fajr.isNext)
        assertTrue(dhuhr.isNext)
    }

    private fun sampleSchedule() = PrayerScheduleData(
        city = "Mumbai",
        methodId = 1,
        methodName = "Karachi",
        dateGregorian = "Sunday, 18 October 2026",
        dateHijri = "",
        timezone = "Asia/Kolkata",
        prayers = listOf(
            prayer(PrayerType.FAJR, "05:00"),
            prayer(PrayerType.SUNRISE, "06:00"),
            prayer(PrayerType.DHUHR, "12:00"),
            prayer(PrayerType.ASR, "15:00"),
            prayer(PrayerType.SUNSET, "17:45"),
            prayer(PrayerType.MAGHRIB, "18:00"),
            prayer(PrayerType.ISHA, "20:00")
        )
    )

    private fun prayer(type: PrayerType, time: String) = PrayerItem(
        type = type,
        rawTime = time,
        formattedTime12 = time,
        formattedTime24 = time,
        targetEpochMillis = 0L
    )
}
