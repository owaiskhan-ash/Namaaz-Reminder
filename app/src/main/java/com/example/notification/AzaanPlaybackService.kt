package com.example.notification

import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.net.Uri
import android.os.Build
import android.os.IBinder
import androidx.core.app.ServiceCompat

/**
 * Foreground media-playback service that hosts [AzaanAlarmPlayer] while a prayer
 * reminder is sounding. Running as a foreground service prevents Doze/OEM task
 * killers from truncating the Madinah Azaan and lets Android play on STREAM_ALARM
 * even when the ringer is on Silent or Vibrate mode.
 */
class AzaanPlaybackService : Service() {

    private var activeReminderId: String? = null

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == PrayerNotificationManager.ACTION_STOP_AZAAN) {
            val cancelId = intent.getIntExtra(EXTRA_NOTIFICATION_ID, 0)
            activeReminderId = null
            AzaanAlarmPlayer.stop(applicationContext)
            ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
            if (cancelId != 0) {
                (getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager)
                    ?.cancel(cancelId)
            }
            stopSelf()
            return START_NOT_STICKY
        }

        val notifId = intent?.getIntExtra(EXTRA_NOTIFICATION_ID, DEFAULT_NOTIF_ID) ?: DEFAULT_NOTIF_ID
        val title = intent?.getStringExtra(EXTRA_TITLE) ?: "Prayer Reminder"
        val message = intent?.getStringExtra(EXTRA_MESSAGE) ?: "It is time for prayer."
        val channelId = intent?.getStringExtra(EXTRA_CHANNEL_ID)
            ?: PrayerNotificationManager.ensureDefaultChannel(applicationContext)
        val soundUri = intent?.getStringExtra(EXTRA_SOUND_URI)?.let { runCatching { Uri.parse(it) }.getOrNull() }
        val vibrate = intent?.getBooleanExtra(EXTRA_VIBRATE, true) ?: true
        val reminderId = intent?.getStringExtra(EXTRA_REMINDER_ID)

        // The receiver has a persistent delivery gate, but keep a second guard
        // here in case Android starts this service twice before a duplicate
        // broadcast has been observed. Restarting MediaPlayer would make the
        // Azaan sound as though it played twice.
        if (reminderId != null && reminderId == activeReminderId && AzaanAlarmPlayer.isPlaying) {
            return START_NOT_STICKY
        }
        activeReminderId = reminderId

        val activeNotification = PrayerNotificationManager.buildNotification(
            context = applicationContext,
            channelId = channelId,
            notifId = notifId,
            title = title,
            message = message,
            includeStopAction = true
        )

        try {
            ServiceCompat.startForeground(
                this,
                notifId,
                activeNotification,
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                    ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
                } else {
                    0
                }
            )
        } catch (e: Exception) {
            // If a platform policy ever blocks FGS promotion, still post the notification.
            (getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager)
                ?.notify(notifId, activeNotification)
        }

        AzaanAlarmPlayer.play(
            context = applicationContext,
            soundUri = soundUri,
            vibrate = vibrate
        ) {
            if (activeReminderId == reminderId) {
                activeReminderId = null
            }
            // Detach the reminder notification without removing it so the user still
            // sees which prayer fired if they return to their phone after the Azaan ends.
            val completedNotification = PrayerNotificationManager.buildNotification(
                context = applicationContext,
                channelId = channelId,
                notifId = notifId,
                title = title,
                message = message,
                includeStopAction = false
            )
            ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_DETACH)
            (getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager)
                ?.notify(notifId, completedNotification)
            stopSelf()
        }

        return START_NOT_STICKY
    }

    override fun onDestroy() {
        activeReminderId = null
        AzaanAlarmPlayer.stop(applicationContext)
        super.onDestroy()
    }

    companion object {
        private const val DEFAULT_NOTIF_ID = 9001
        const val EXTRA_NOTIFICATION_ID = "extra_notification_id"
        const val EXTRA_TITLE = "extra_title"
        const val EXTRA_MESSAGE = "extra_message"
        const val EXTRA_CHANNEL_ID = "extra_channel_id"
        const val EXTRA_SOUND_URI = "extra_sound_uri"
        const val EXTRA_VIBRATE = "extra_vibrate"
        const val EXTRA_REMINDER_ID = "extra_reminder_id"
    }
}
