package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.data.local.PreferencesManager
import com.example.data.model.CALCULATION_METHODS
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import com.example.data.repository.PrayerRepository
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class ExampleRobolectricTest {

    @Test
    fun `read string from context`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val appName = context.getString(R.string.app_name)
        assertEquals("Namaz Times", appName)
    }

    @Test
    fun `test settings persistence in PreferencesManager`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val prefs = PreferencesManager(context)

        val testSettings = UserSettings(
            selectedCity = "Mumbai",
            methodId = 2,
            themeMode = "DARK",
            notificationsEnabled = true,
            reminderOffsetMinutes = 10,
            soundEnabled = false,
            vibrationEnabled = true,
            is24HourFormat = true,
            mutedPrayerNames = setOf("ASR")
        )

        prefs.saveSettings(testSettings)
        val loaded = prefs.loadSettings()

        assertEquals("Mumbai", loaded.selectedCity)
        assertEquals(2, loaded.methodId)
        assertEquals("DARK", loaded.themeMode)
        assertEquals(10, loaded.reminderOffsetMinutes)
        assertEquals(false, loaded.soundEnabled)
        assertEquals(true, loaded.is24HourFormat)
        assertTrue(loaded.mutedPrayerNames.contains("ASR"))
    }

    @Test
    fun `test Aladhan JSON parsing in PrayerRepository`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val prefs = PreferencesManager(context)
        val repository = PrayerRepository(prefs)

        val sampleJson = """
        {
            "code": 200,
            "status": "OK",
            "data": {
                "timings": {
                    "Fajr": "05:05",
                    "Sunrise": "06:24",
                    "Dhuhr": "12:06",
                    "Asr": "15:23",
                    "Sunset": "17:49",
                    "Maghrib": "17:49",
                    "Isha": "19:07"
                },
                "date": {
                    "readable": "18 Oct 2026",
                    "gregorian": {
                        "day": "18",
                        "weekday": {"en": "Sunday"},
                        "month": {"en": "October"},
                        "year": "2026"
                    },
                    "hijri": {
                        "day": "07",
                        "month": {"en": "Jumada al-Ula"},
                        "year": "1448"
                    }
                },
                "meta": {
                    "timezone": "Asia/Kolkata",
                    "method": {
                        "id": 1,
                        "name": "University of Islamic Sciences, Karachi"
                    }
                }
            }
        }
        """.trimIndent()

        val parsed = repository.parseJsonResponse(
            jsonStr = sampleJson,
            city = "Delhi",
            methodId = 1,
            mutedPrayers = emptySet(),
            isOffline = false,
            cacheTime = System.currentTimeMillis()
        )

        assertEquals("Delhi", parsed.city)
        assertEquals(1, parsed.methodId)
        assertEquals(7, parsed.prayers.size)

        val fajr = parsed.prayers.first { it.type == PrayerType.FAJR }
        assertEquals("05:05", fajr.rawTime)
        assertEquals("5:05 AM", fajr.formattedTime12)
        assertEquals("05:05", fajr.formattedTime24)

        val asr = parsed.prayers.first { it.type == PrayerType.ASR }
        assertEquals("15:23", asr.rawTime)
        assertEquals("3:23 PM", asr.formattedTime12)

        assertNotNull(parsed.nextPrayer)
    }

    @Test
    fun `test calculation methods exist`() {
        assertTrue(CALCULATION_METHODS.any { it.id == 1 && it.name.contains("Karachi") })
        assertTrue(CALCULATION_METHODS.any { it.id == 2 && it.name.contains("ISNA") })
        assertTrue(CALCULATION_METHODS.any { it.id == 3 && it.name.contains("MWL") })
    }
}
