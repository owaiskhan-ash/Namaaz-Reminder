package com.example.notification

import com.example.data.model.PrayerType
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.util.Calendar

/**
 * Unit tests for the identity / grouping rules of the prayer reminders.
 *
 * These are the rules that stop the daily reminders from being merged into a
 * single bundled notification by the system.
 */
class PrayerNotificationManagerTest {

    @Test
    fun `every prayer gets its own notification id`() {
        val ids = PrayerType.entries.map { PrayerNotificationManager.notificationIdFor(it.englishName) }

        assertEquals(ids.size, ids.distinct().size)
    }

    @Test
    fun `notification ids are stable for the same prayer`() {
        assertEquals(
            PrayerNotificationManager.notificationIdFor("Fajr"),
            PrayerNotificationManager.notificationIdFor("Fajr")
        )
        // The lookup is case insensitive so a differently cased name still maps
        // onto the same notification instead of creating a second one.
        assertEquals(
            PrayerNotificationManager.notificationIdFor("Fajr"),
            PrayerNotificationManager.notificationIdFor("fajr")
        )
    }

    @Test
    fun `every prayer gets its own group so reminders are not merged`() {
        val groups = PrayerType.entries.map { PrayerNotificationManager.groupKeyFor(it.englishName) }

        assertEquals(groups.size, groups.distinct().size)
        assertTrue(groups.all { it.isNotBlank() })
    }

    @Test
    fun `sound and vibration preferences map to distinct channels`() {
        val channels = listOf(
            PrayerNotificationManager.channelIdFor(soundEnabled = true, vibrateEnabled = true),
            PrayerNotificationManager.channelIdFor(soundEnabled = true, vibrateEnabled = false),
            PrayerNotificationManager.channelIdFor(soundEnabled = false, vibrateEnabled = true),
            PrayerNotificationManager.channelIdFor(soundEnabled = false, vibrateEnabled = false)
        )

        assertEquals(channels.size, channels.distinct().size)
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID,
            PrayerNotificationManager.channelIdFor(soundEnabled = true, vibrateEnabled = true)
        )
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_SOUND_ONLY,
            PrayerNotificationManager.channelIdFor(soundEnabled = true, vibrateEnabled = false)
        )
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_VIBRATE_ONLY,
            PrayerNotificationManager.channelIdFor(soundEnabled = false, vibrateEnabled = true)
        )
        assertEquals(
            PrayerNotificationManager.CHANNEL_ID_SILENT,
            PrayerNotificationManager.channelIdFor(soundEnabled = false, vibrateEnabled = false)
        )
    }

    @Test
    fun `only reminders posted before today are pruned`() {
        val dayStart = PrayerNotificationManager.startOfTodayMillis()
        val reminderId = PrayerNotificationManager.notificationIdFor("Fajr")
        val yesterday = dayStart - 60_000L

        assertTrue(
            PrayerNotificationManager.shouldPruneNotification(reminderId, yesterday, dayStart)
        )
        assertFalse(
            PrayerNotificationManager.shouldPruneNotification(reminderId, dayStart, dayStart)
        )
        assertFalse(
            PrayerNotificationManager.shouldPruneNotification(reminderId, dayStart + 60_000L, dayStart)
        )
    }

    @Test
    fun `the test notification is never pruned`() {
        val dayStart = PrayerNotificationManager.startOfTodayMillis()

        assertFalse(
            PrayerNotificationManager.shouldPruneNotification(
                PrayerNotificationManager.TEST_NOTIFICATION_ID,
                dayStart - 60_000L,
                dayStart
            )
        )
    }

    @Test
    fun `start of today is midnight`() {
        val calendar = Calendar.getInstance().apply {
            set(Calendar.HOUR_OF_DAY, 12)
            set(Calendar.MINUTE, 30)
            set(Calendar.SECOND, 15)
            set(Calendar.MILLISECOND, 250)
        }

        val start = PrayerNotificationManager.startOfTodayMillis(calendar.timeInMillis)
        val startCalendar = Calendar.getInstance().apply { timeInMillis = start }

        assertEquals(0, startCalendar.get(Calendar.HOUR_OF_DAY))
        assertEquals(0, startCalendar.get(Calendar.MINUTE))
        assertEquals(0, startCalendar.get(Calendar.SECOND))
        assertEquals(0, startCalendar.get(Calendar.MILLISECOND))
    }
}
