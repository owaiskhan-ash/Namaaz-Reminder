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
 * Fires a prayer reminder notification (and handles the "Stop Azaan" action),
 * then re-arms the remaining and next-day alarms.
 */
class PrayerAlarmReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return
        val appContext = context.applicationContext

        if (intent.action == PrayerNotificationManager.ACTION_STOP_AZAAN) {
            val cancelId = intent.getIntExtra(
                PrayerNotificationManager.EXTRA_CANCEL_NOTIFICATION_ID,
                0
            )
            PrayerNotificationManager.stopAzaan(appContext, cancelId)
            return
        }

        if (intent.action != PrayerNotificationManager.ACTION_PRAYER_REMINDER) return

        val settings = PreferencesManager(appContext).loadSettings()
        val prayerName = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_NAME) ?: "Prayer"
        val prayerTime = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_TIME) ?: ""
        val city = intent.getStringExtra(PrayerNotificationManager.EXTRA_CITY) ?: "India"
        val offset = intent.getIntExtra(PrayerNotificationManager.EXTRA_OFFSET, settings.reminderOffsetMinutes)

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
