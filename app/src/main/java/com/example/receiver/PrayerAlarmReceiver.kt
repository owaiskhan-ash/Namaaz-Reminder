package com.example.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.example.notification.AlarmRescheduler
import com.example.notification.PrayerNotificationManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Fires the prayer reminder notification, then re-arms the remaining and
 * next-day alarms. The re-arm step is what keeps reminders going daily:
 * the scheduled alarms are one-shot, so without it reminders would stop
 * after the last alarm of the day unless the user reopened the app.
 */
class PrayerAlarmReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return

        val appContext = context.applicationContext

        val prayerName = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_NAME) ?: "Prayer"
        val prayerTime = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_TIME) ?: ""
        val city = intent.getStringExtra(PrayerNotificationManager.EXTRA_CITY) ?: "India"
        val offset = intent.getIntExtra(PrayerNotificationManager.EXTRA_OFFSET, 5)
        val sound = intent.getBooleanExtra(PrayerNotificationManager.EXTRA_SOUND, true)
        val vibrate = intent.getBooleanExtra(PrayerNotificationManager.EXTRA_VIBRATE, true)
        val prayerEpoch = intent.getLongExtra(PrayerNotificationManager.EXTRA_PRAYER_EPOCH, 0L)
        val nextPrayer = intent.getStringExtra(PrayerNotificationManager.EXTRA_NEXT_PRAYER)
        val nextPrayerTime = intent.getStringExtra(PrayerNotificationManager.EXTRA_NEXT_PRAYER_TIME)
        val nextPrayerLabel = when {
            nextPrayer.isNullOrBlank() -> null
            nextPrayerTime.isNullOrBlank() -> nextPrayer
            else -> "$nextPrayer at $nextPrayerTime"
        }
        // The azaan that was saved on the device when the alarm was armed.
        val azaanUri = intent.getStringExtra(PrayerNotificationManager.EXTRA_AZAAN_URI)
            ?.takeIf { it.isNotBlank() }
            ?.let { runCatching { Uri.parse(it) }.getOrNull() }

        // 1) Show the reminder immediately (fast, synchronous).
        PrayerNotificationManager.showPrayerNotification(
            context = appContext,
            prayerName = prayerName,
            prayerTime = prayerTime,
            city = city,
            offsetMinutes = offset,
            soundEnabled = sound,
            vibrateEnabled = vibrate,
            isTest = false,
            prayerEpochMillis = prayerEpoch,
            nextPrayerLabel = nextPrayerLabel,
            azaanUri = azaanUri
        )

        // 2) Re-arm upcoming alarms (kept alive via goAsync while this runs).
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
