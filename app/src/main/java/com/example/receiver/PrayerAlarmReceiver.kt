package com.example.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.example.data.local.PreferencesManager
import com.example.notification.AlarmRescheduler
import com.example.notification.PrayerNotificationManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Fires a prayer reminder notification, then re-arms the remaining and
 * next-day alarms. The re-arm step keeps reminders going day after day.
 */
class PrayerAlarmReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return

        val appContext = context.applicationContext
        val settings = PreferencesManager(appContext).loadSettings()
        val prayerName = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_NAME) ?: "Prayer"
        val prayerTime = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_TIME) ?: ""
        val city = intent.getStringExtra(PrayerNotificationManager.EXTRA_CITY) ?: "India"
        val offset = intent.getIntExtra(PrayerNotificationManager.EXTRA_OFFSET, settings.reminderOffsetMinutes)

        // Settings are read at delivery time so a changed Azaan or sound preference is
        // applied even if an older one-shot PendingIntent happened to be in flight.
        if (settings.notificationsEnabled) {
            PrayerNotificationManager.showPrayerNotification(
                context = appContext,
                prayerName = prayerName,
                prayerTime = prayerTime,
                city = city,
                offsetMinutes = offset,
                settings = settings,
                isTest = false
            )
        }

        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                AlarmRescheduler.rescheduleAlarms(appContext)
            } catch (e: Exception) {
                // Best effort; the app reschedules again when opened.
            } finally {
                pendingResult.finish()
            }
        }
    }
}
