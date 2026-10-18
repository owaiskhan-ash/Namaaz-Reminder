package com.example.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.example.data.local.PreferencesManager
import com.example.data.repository.PrayerRepository
import com.example.notification.PrayerNotificationManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent?) {
        if (intent?.action == Intent.ACTION_BOOT_COMPLETED) {
            val prefs = PreferencesManager(context)
            val settings = prefs.loadSettings()
            if (settings.notificationsEnabled) {
                val repository = PrayerRepository(prefs)
                CoroutineScope(Dispatchers.IO).launch {
                    val result = repository.getPrayerSchedule(
                        city = settings.selectedCity,
                        methodId = settings.methodId,
                        mutedPrayers = settings.mutedPrayerNames
                    )
                    result.onSuccess { schedule ->
                        PrayerNotificationManager.schedulePrayerAlarms(context, schedule, settings)
                    }
                }
            }
        }
    }
}
