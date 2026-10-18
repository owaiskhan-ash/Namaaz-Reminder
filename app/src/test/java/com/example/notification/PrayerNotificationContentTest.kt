package com.example.notification

import android.content.Context
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Tests for the content of the prayer reminder notifications.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class PrayerNotificationContentTest {

    private val context: Context
        get() = ApplicationProvider.getApplicationContext()

    @Test
    fun `reminders of different prayers are built as separate groups`() {
        val fajr = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:05 AM",
            city = "Mumbai",
            offsetMinutes = 0
        )
        val dhuhr = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Dhuhr",
            prayerTime = "1:35 PM",
            city = "Mumbai",
            offsetMinutes = 0
        )

        assertNotNull(fajr.group)
        assertNotNull(dhuhr.group)
        assertNotEquals(fajr.group, dhuhr.group)
    }

    @Test
    fun `the notification shows the prayer time as its timestamp`() {
        val prayerEpoch = 1_760_000_000_000L

        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Asr",
            prayerTime = "3:23 PM",
            city = "Delhi",
            offsetMinutes = 0,
            prayerEpochMillis = prayerEpoch
        )

        assertEquals(prayerEpoch, notification.`when`)
    }

    @Test
    fun `the notification mentions the prayer and the next one`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Maghrib",
            prayerTime = "6:02 PM",
            city = "Delhi",
            offsetMinutes = 0,
            nextPrayerLabel = "Isha at 7:20 PM"
        )

        val text = notification.extras?.getCharSequence(androidx.core.app.NotificationCompat.EXTRA_TEXT)?.toString()

        assertTrue(notification.extras?.getCharSequence(androidx.core.app.NotificationCompat.EXTRA_TITLE)?.toString()
            ?.contains("Maghrib") == true)
        assertTrue(text?.contains("Maghrib") == true)
        assertTrue(text?.contains("Next: Isha at 7:20 PM") == true)
    }

    @Test
    fun `the reminder offset is reflected in the title`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:05 AM",
            city = "Delhi",
            offsetMinutes = 10
        )

        val title = notification.extras
            ?.getCharSequence(androidx.core.app.NotificationCompat.EXTRA_TITLE)
            ?.toString()

        assertTrue(title?.contains("10m after adhan") == true)
    }

    @Test
    fun `the channel follows the sound and vibration preferences`() {
        val loud = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:05 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = true,
            vibrateEnabled = true
        )
        val silent = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:05 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = false,
            vibrateEnabled = false
        )

        assertEquals(PrayerNotificationManager.CHANNEL_ID, loud.channel)
        assertEquals(PrayerNotificationManager.CHANNEL_ID_SILENT, silent.channel)
    }
}
