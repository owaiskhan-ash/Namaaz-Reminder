package com.example

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import com.example.data.local.PreferencesManager
import com.example.data.model.CALCULATION_METHODS
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import com.example.data.repository.PrayerRepository
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class CoreBehaviorTest {

    @Test
    fun `read string from context`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val appName = context.getString(R.string.app_name)
        assertEquals("Namaaz Reminder", appName)
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
            mutedPrayerNames = setOf("ASR"),
            customPrayerTimes = mapOf("2026-10-18|mumbai|FAJR" to "05:20"),
            azaanSoundId = "custom",
            customAzaanName = "My Azaan",
            customAzaanUri = "content://media/audio/42"
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
        assertEquals(mapOf("2026-10-18|mumbai|FAJR" to "05:20"), loaded.customPrayerTimes)
        assertEquals("custom", loaded.azaanSoundId)
        assertEquals("My Azaan", loaded.customAzaanName)
        assertEquals("content://media/audio/42", loaded.customAzaanUri)
    }

    @Test
    fun `reminder delivery claim prevents a duplicate broadcast from playing twice`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val prefs = PreferencesManager(context)
        val eventId = "mumbai|fajr|delivery-gate-${System.nanoTime()}"
        val deliveredAt = 1_000L

        assertTrue(prefs.claimReminderDelivery(eventId, deliveredAt))
        assertFalse(prefs.claimReminderDelivery(eventId, deliveredAt + 1L))
        assertTrue(prefs.claimReminderDelivery("$eventId-next", deliveredAt + 1L))
        // The same prayer may be delivered again after the short retention
        // window has elapsed; in normal use its id includes a new date.
        assertTrue(prefs.claimReminderDelivery(eventId, deliveredAt + 3L * 24L * 60L * 60L * 1000L))
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

    @Test
    fun `prayer notification channel and stop action work for alarm stream playback`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val settings = UserSettings(
            selectedCity = "Mumbai",
            soundEnabled = true,
            vibrationEnabled = true,
            azaanSoundId = "madinah"
        )
        val channelId = com.example.notification.PrayerNotificationManager.createNotificationChannel(
            context,
            settings
        )
        assertTrue(channelId.contains("v4_madinah"))

        val notif = com.example.notification.PrayerNotificationManager.buildNotification(
            context = context,
            channelId = channelId,
            notifId = 1001,
            title = "Time for Fajr Prayer",
            message = "It is now time for Fajr prayer in Mumbai.",
            includeStopAction = true
        )
        assertEquals(android.app.Notification.CATEGORY_ALARM, notif.category)
        assertTrue(notif.actions?.any { it.title == "Stop Azaan" } == true)

        com.example.notification.PrayerNotificationManager.stopAzaan(context, 1001)
    }

    @Test
    fun `default theme opens in subtle black leather dark mode and texture resource exists`() {
        val context = ApplicationProvider.getApplicationContext<Context>()
        val freshSettings = PreferencesManager(context).loadSettings()
        assertEquals("DARK", freshSettings.themeMode)
        val bmp = android.graphics.BitmapFactory.decodeResource(
            context.resources,
            R.drawable.leather_black_tile
        )
        assertNotNull(bmp)
    }
}
