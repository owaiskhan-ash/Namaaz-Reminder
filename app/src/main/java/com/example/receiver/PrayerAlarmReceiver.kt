package com.example.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.example.notification.PrayerNotificationManager

class PrayerAlarmReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent == null) return

        val prayerName = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_NAME) ?: "Prayer"
        val prayerTime = intent.getStringExtra(PrayerNotificationManager.EXTRA_PRAYER_TIME) ?: ""
        val city = intent.getStringExtra(PrayerNotificationManager.EXTRA_CITY) ?: "India"
        val offset = intent.getIntExtra(PrayerNotificationManager.EXTRA_OFFSET, 5)
        val sound = intent.getBooleanExtra(PrayerNotificationManager.EXTRA_SOUND, true)
        val vibrate = intent.getBooleanExtra(PrayerNotificationManager.EXTRA_VIBRATE, true)

        PrayerNotificationManager.showPrayerNotification(
            context = context,
            prayerName = prayerName,
            prayerTime = prayerTime,
            city = city,
            offsetMinutes = offset,
            soundEnabled = sound,
            vibrateEnabled = vibrate,
            isTest = false
        )
    }
}
