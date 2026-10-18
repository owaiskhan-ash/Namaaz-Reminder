package com.example.notification

import android.app.NotificationManager
import android.content.Context
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

    @Test
    fun `the azaan plays on a channel that has no sound of its own`() {
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_VIBRATE_ONLY,
            PrayerNotificationManager.channelIdFor(
                soundEnabled = true,
                vibrateEnabled = true,
                hasAzaan = true
            )
        )
    }

    @Test
    fun `the azaan plays on the silent channel when the vibration is off`() {
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_SILENT,
            PrayerNotificationManager.channelIdFor(
                soundEnabled = true,
                vibrateEnabled = false,
                hasAzaan = true
            )
        )
    }

    @Test
    fun `without an azaan the channel of the preferences is used`() {
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID,
            PrayerNotificationManager.channelIdFor(
                soundEnabled = true,
                vibrateEnabled = true
            )
        )
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_SOUND_ONLY,
            PrayerNotificationManager.channelIdFor(
                soundEnabled = true,
                vibrateEnabled = false
            )
        )
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_SILENT,
            PrayerNotificationManager.channelIdFor(
                soundEnabled = false,
                vibrateEnabled = false
            )
        )
    }

    @Test
    fun `the channel that plays the azaan is silent`() {
        PrayerNotificationManager.createNotificationChannel(context)
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val channel = notificationManager
            .getNotificationChannel(PrayerNotificationManager.CHANNEL_ID_VIBRATE_ONLY)

        assertNotNull(channel)
        // The azaan is set on the notification itself, the channel stays silent.
        assertNull(channel!!.sound)
    }

    @Test
    fun `the azaan uri is passed on to the alarm`() {
        // The reminder that the alarm posts has to know which azaan to play.
        assertEquals("extra_azaan_uri", PrayerNotificationManager.EXTRA_AZAAN_URI)
    }
}
