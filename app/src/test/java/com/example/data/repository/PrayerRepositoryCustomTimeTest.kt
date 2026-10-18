package com.example.data.repository

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.data.local.PreferencesManager
import com.example.data.model.PrayerType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import java.util.Calendar
import java.util.TimeZone

/**
 * Tests for the times the user sets by hand (long press on a prayer card).
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class PrayerRepositoryCustomTimeTest {

    private val context: Context
        get() = ApplicationProvider.getApplicationContext()

    private fun repository() = PrayerRepository(PreferencesManager(context))

    private fun parse(customTimes: Map<String, String> = emptyMap()) =
        repository().parseJsonResponse(
            jsonStr = SAMPLE_JSON,
            city = "Delhi",
            methodId = 1,
            mutedPrayers = emptySet(),
            isOffline = false,
            cacheTime = 0L,
            customTimes = customTimes
        )

    @Test
    fun `a custom time replaces the calculated one`() {
        val schedule = parse(mapOf("FAJR" to "05:30"))
        val fajr = schedule.prayers.first { it.type == PrayerType.FAJR }

        assertTrue(fajr.hasCustomTime)
        assertEquals("5:30 AM", fajr.effectiveTime(false))
        assertEquals("05:30", fajr.effectiveTime(true))
        // The calculated time is still there, the card shows it dimmed.
        assertEquals("5:05 AM", fajr.defaultTime(false))
    }

    @Test
    fun `the countdown follows the custom time`() {
        val schedule = parse(mapOf("FAJR" to "05:30"))
        val fajr = schedule.prayers.first { it.type == PrayerType.FAJR }

        val expected = Calendar.getInstance(TimeZone.getTimeZone("Asia/Kolkata")).apply {
            set(Calendar.HOUR_OF_DAY, 5)
            set(Calendar.MINUTE, 30)
            set(Calendar.SECOND, 0)
            set(Calendar.MILLISECOND, 0)
        }.timeInMillis

        assertEquals(expected, fajr.effectiveEpochMillis)
    }

    @Test
    fun `a prayer is passed when its custom time has passed`() {
        val schedule = parse(mapOf("ISHA" to "23:58"))
        val isha = schedule.prayers.first { it.type == PrayerType.ISHA }

        val now = System.currentTimeMillis()
        assertEquals(now > isha.effectiveEpochMillis, isha.isPassed)
    }

    @Test
    fun `the next prayer is the first one that has not passed`() {
        val schedule = parse(mapOf("FAJR" to "23:58"))

        val next = schedule.nextPrayer
        assertNotNull(next)
        assertEquals(PrayerType.FAJR, next!!.type)
        assertEquals(1, schedule.prayers.count { it.isNext })
    }

    @Test
    fun `custom times can be applied to a schedule that is already loaded`() {
        val schedule = parse()
        val fajrBefore = schedule.prayers.first { it.type == PrayerType.FAJR }
        assertFalse(fajrBefore.hasCustomTime)

        val updated = repository().applyCustomTimes(schedule, mapOf("FAJR" to "05:30"))
        val fajrAfter = updated.prayers.first { it.type == PrayerType.FAJR }

        assertTrue(fajrAfter.hasCustomTime)
        assertEquals("5:30 AM", fajrAfter.effectiveTime(false))
    }

    @Test
    fun `removing the custom time brings the calculated one back`() {
        val schedule = parse(mapOf("FAJR" to "05:30"))

        val updated = repository().applyCustomTimes(schedule, emptyMap())
        val fajr = updated.prayers.first { it.type == PrayerType.FAJR }

        assertFalse(fajr.hasCustomTime)
        assertEquals("5:05 AM", fajr.effectiveTime(false))
    }

    @Test
    fun `the muted prayers are kept when the custom times are applied`() {
        val schedule = repository().parseJsonResponse(
            jsonStr = SAMPLE_JSON,
            city = "Delhi",
            methodId = 1,
            mutedPrayers = setOf("ASR"),
            isOffline = false,
            cacheTime = 0L
        )

        val updated = repository().applyCustomTimes(schedule, mapOf("FAJR" to "05:30"))
        val asr = updated.prayers.first { it.type == PrayerType.ASR }

        assertFalse(asr.notificationEnabled)
    }

    companion object {
        private val SAMPLE_JSON = """
            {
              "code": 200,
              "status": "OK",
              "data": {
                "timings": {
                  "Fajr": "05:05 (IST)",
                  "Sunrise": "06:15 (IST)",
                  "Dhuhr": "12:15 (IST)",
                  "Asr": "15:30 (IST)",
                  "Sunset": "17:50 (IST)",
                  "Maghrib": "17:50 (IST)",
                  "Isha": "19:15 (IST)"
                },
                "date": {
                  "readable": "Friday, 1 January 2027",
                  "gregorian": {
                    "day": "01",
                    "month": { "en": "January" },
                    "year": "2027",
                    "weekday": { "en": "Friday" }
                  },
                  "hijri": {
                    "day": "01",
                    "month": { "en": "Muharram" },
                    "year": "1448"
                  }
                },
                "meta": {
                  "timezone": "Asia/Kolkata",
                  "method": { "name": "Karachi" }
                }
              }
            }
        """.trimIndent()
    }
}
