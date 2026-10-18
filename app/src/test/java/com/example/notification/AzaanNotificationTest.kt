package com.example.notification

import android.content.Context
import android.net.Uri
import androidx.test.core.app.ApplicationProvider
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config

/**
 * Tests for the azaan that plays with the prayer reminders.
 */
@RunWith(RobolectricTestRunner::class)
@Config(sdk = [34])
class AzaanNotificationTest {

    private val context: Context
        get() = ApplicationProvider.getApplicationContext()

    private val azaanUri: Uri = Uri.parse("content://media/external/audio/media/42")

    @Test
    fun `the azaan is the sound of the reminder`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:30 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = true,
            vibrateEnabled = true,
            azaanUri = azaanUri
        )

        assertEquals(azaanUri, notification.sound)
    }

    @Test
    fun `the azaan is played on a channel that has no sound of its own`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:30 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = true,
            vibrateEnabled = true,
            azaanUri = azaanUri
        )

        // The system only plays the sound of the notification when the channel
        // itself is silent.
        assertEquals(PrayerNotificationManager.CHANNEL_ID_VIBRATE_ONLY, notification.channelId)
    }

    @Test
    fun `without an azaan the channel of the preferences is used`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:05 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = true,
            vibrateEnabled = true
        )

        assertEquals(PrayerNotificationManager.CHANNEL_ID, notification.channelId)
        assertNull(notification.sound)
    }

    @Test
    fun `without a sound the azaan is not played`() {
        val notification = PrayerNotificationManager.buildPrayerNotification(
            context = context,
            prayerName = "Fajr",
            prayerTime = "5:30 AM",
            city = "Delhi",
            offsetMinutes = 0,
            soundEnabled = false,
            vibrateEnabled = true,
            azaanUri = azaanUri
        )

        assertNull(notification.sound)
        assertEquals(PrayerNotificationManager.CHANNEL_ID_VIBRATE_ONLY, notification.channelId)
    }

    @Test
    fun `the azaan uri is passed on to the alarm`() {
        // The reminder that the alarm posts has to know which azaan to play.
        assertNotNull(PrayerNotificationManager.EXTRA_AZAAN_URI)
        assertEquals(
            "extra_azaan_uri",
            PrayerNotificationManager.EXTRA_AZAAN_URI
        )
    }
}
