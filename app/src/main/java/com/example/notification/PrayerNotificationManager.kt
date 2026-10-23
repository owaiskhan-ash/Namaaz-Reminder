package com.example.notification

import android.app.AlarmManager
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Build
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.example.MainActivity
import com.example.R
import com.example.data.local.PreferencesManager
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.UserSettings
import com.example.receiver.PrayerAlarmReceiver

object PrayerNotificationManager {
    /**
     * Channel v3 delegates audio + alarm vibration directly to [AzaanAlarmPlayer]
     * on [android.media.AudioAttributes.USAGE_ALARM] ([android.media.AudioManager.STREAM_ALARM])
     * so the full Madinah Azaan plays even when the phone is on Silent or Vibrate mode,
     * without Android's notification service muting or truncating it.
     */
    private const val CHANNEL_ID_PREFIX = "namaz_prayer_alarms_v3"
    const val ACTION_PRAYER_REMINDER = "com.example.namaztimes.ACTION_PRAYER_REMINDER"
    const val ACTION_STOP_AZAAN = "com.example.namaztimes.ACTION_STOP_AZAAN"

    const val EXTRA_PRAYER_NAME = "extra_prayer_name"
    const val EXTRA_PRAYER_TIME = "extra_prayer_time"
    const val EXTRA_CITY = "extra_city"
    const val EXTRA_OFFSET = "extra_offset"
    const val EXTRA_CANCEL_NOTIFICATION_ID = "extra_cancel_notification_id"
    const val EXTRA_STOP_AZAAN_ON_OPEN = "extra_stop_azaan_on_open"

    fun createNotificationChannel(context: Context, settings: UserSettings): String {
        val channelId = channelIdFor(settings)
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return channelId

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
                ?: return channelId

        val channelTitle = when {
            !settings.soundEnabled -> "Prayer Reminders (Silent)"
            else -> "Prayer Reminders — ${AzaanSoundStore.soundName(settings)}"
        }

        val existing = notificationManager.getNotificationChannel(channelId)
        if (existing == null) {
            val channel = NotificationChannel(
                channelId,
                channelTitle,
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = context.getString(R.string.channel_description)
                lockscreenVisibility = Notification.VISIBILITY_PUBLIC
                // AzaanAlarmPlayer handles sound + alarm-stream vibration directly so
                // Silent/Vibrate mode never silences the Azaan and Normal mode never echoes.
                setSound(null, null)
                enableVibration(false)
                if (notificationManager.isNotificationPolicyAccessGranted) {
                    setBypassDnd(true)
                }
            }
            notificationManager.createNotificationChannel(channel)
        } else if (notificationManager.isNotificationPolicyAccessGranted && !existing.canBypassDnd()) {
            existing.setBypassDnd(true)
            notificationManager.createNotificationChannel(existing)
        }

        notificationManager.notificationChannels
            .map { it.id }
            .filter {
                (it.startsWith("${CHANNEL_ID_PREFIX}_") ||
                    it.startsWith("namaz_prayer_alarms_v2_") ||
                    it.startsWith("namaz_prayer_reminders_")) &&
                    it != channelId
            }
            .forEach(notificationManager::deleteNotificationChannel)

        return channelId
    }

    fun ensureDefaultChannel(context: Context): String {
        val settings = PreferencesManager(context.applicationContext).loadSettings()
        return createNotificationChannel(context, settings)
    }

    private fun channelIdFor(settings: UserSettings): String {
        val soundKey = if (!settings.soundEnabled) {
            "silent"
        } else {
            when (settings.azaanSoundId) {
                "madinah" -> "madinah"
                "custom" -> "custom"
                else -> "device"
            }
        }
        return "${CHANNEL_ID_PREFIX}_$soundKey"
    }

    /**
     * Whether the app is currently allowed to schedule exact alarms.
     * Android 12+ (API 31+) requires SCHEDULE_EXACT_ALARM to be granted by the user.
     */
    fun canScheduleExactAlarms(context: Context): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return true
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager
            ?: return false
        return alarmManager.canScheduleExactAlarms()
    }

    fun schedulePrayerAlarms(
        context: Context,
        schedule: PrayerScheduleData,
        settings: UserSettings
    ) {
        createNotificationChannel(context, settings)
        if (!settings.notificationsEnabled) {
            stopAzaan(context)
            cancelAllAlarms(context, schedule.prayers)
            return
        }

        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val now = System.currentTimeMillis()
        val offsetMillis = settings.reminderOffsetMinutes * 60 * 1000L
        val canExact = canScheduleExactAlarms(context)

        schedule.prayers.filter { it.type.isPrimaryPrayer }.forEach { prayer ->
            if (!settings.mutedPrayerNames.contains(prayer.type.name)) {
                val triggerAt = prayer.targetEpochMillis + offsetMillis

                if (triggerAt > now) {
                    val intent = Intent(context, PrayerAlarmReceiver::class.java).apply {
                        action = ACTION_PRAYER_REMINDER
                        putExtra(EXTRA_PRAYER_NAME, prayer.type.englishName)
                        putExtra(EXTRA_PRAYER_TIME, prayer.displayTime(settings.is24HourFormat))
                        putExtra(EXTRA_CITY, schedule.city)
                        putExtra(EXTRA_OFFSET, settings.reminderOffsetMinutes)
                    }

                    val pendingIntent = PendingIntent.getBroadcast(
                        context,
                        prayer.type.ordinal,
                        intent,
                        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                    )

                    try {
                        if (canExact) {
                            alarmManager.setExactAndAllowWhileIdle(
                                AlarmManager.RTC_WAKEUP,
                                triggerAt,
                                pendingIntent
                            )
                        } else {
                            alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent)
                        }
                    } catch (e: SecurityException) {
                        alarmManager.set(AlarmManager.RTC_WAKEUP, triggerAt, pendingIntent)
                    }
                } else {
                    cancelAlarm(context, prayer.type.ordinal)
                }
            } else {
                cancelAlarm(context, prayer.type.ordinal)
            }
        }
    }

    fun cancelAllAlarms(context: Context, prayers: List<PrayerItem>) {
        prayers.forEach { prayer ->
            cancelAlarm(context, prayer.type.ordinal)
        }
    }

    private fun cancelAlarm(context: Context, requestCode: Int) {
        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val intent = Intent(context, PrayerAlarmReceiver::class.java).apply {
            action = ACTION_PRAYER_REMINDER
        }
        val pendingIntent = PendingIntent.getBroadcast(
            context,
            requestCode,
            intent,
            PendingIntent.FLAG_NO_CREATE or PendingIntent.FLAG_IMMUTABLE
        )
        if (pendingIntent != null) {
            alarmManager.cancel(pendingIntent)
            pendingIntent.cancel()
        }
    }

    fun buildNotification(
        context: Context,
        channelId: String,
        notifId: Int,
        title: String,
        message: String,
        includeStopAction: Boolean
    ): Notification {
        val launchIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra(EXTRA_STOP_AZAAN_ON_OPEN, true)
        }
        val contentPendingIntent = PendingIntent.getActivity(
            context,
            notifId,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val dismissStopIntent = Intent(context, PrayerAlarmReceiver::class.java).apply {
            action = ACTION_STOP_AZAAN
            putExtra(EXTRA_CANCEL_NOTIFICATION_ID, 0)
        }
        val dismissPendingIntent = PendingIntent.getBroadcast(
            context,
            notifId + 10_000,
            dismissStopIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val largeIcon = runCatching {
            BitmapFactory.decodeResource(context.resources, R.drawable.ic_app_icon)
        }.getOrNull()

        val builder = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setLargeIcon(largeIcon)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .setContentIntent(contentPendingIntent)
            .setDeleteIntent(dismissPendingIntent)
            .setAutoCancel(true)

        if (includeStopAction) {
            val stopButtonIntent = Intent(context, PrayerAlarmReceiver::class.java).apply {
                action = ACTION_STOP_AZAAN
                putExtra(EXTRA_CANCEL_NOTIFICATION_ID, notifId)
            }
            val stopButtonPendingIntent = PendingIntent.getBroadcast(
                context,
                notifId + 20_000,
                stopButtonIntent,
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            builder.addAction(0, "Stop Azaan", stopButtonPendingIntent)
        }

        return builder.build()
    }

    fun showPrayerNotification(
        context: Context,
        prayerName: String,
        prayerTime: String,
        city: String,
        offsetMinutes: Int,
        settings: UserSettings,
        isTest: Boolean = false
    ) {
        val appContext = context.applicationContext
        val channelId = createNotificationChannel(appContext, settings)
        val notificationManager =
            appContext.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return

        val title = if (isTest) {
            "Test Reminder: $prayerName Prayer"
        } else if (offsetMinutes > 0) {
            "$prayerName Reminder ($offsetMinutes min after)"
        } else {
            "Time for $prayerName Prayer"
        }

        val message = if (isTest) {
            "Notification & Madinah Azaan alarm stream are active. Scheduled time: $prayerTime in $city."
        } else if (offsetMinutes > 0) {
            "$prayerName prayer in $city started $offsetMinutes minutes ago ($prayerTime). It is time for your Salah."
        } else {
            "It is now time for $prayerName prayer in $city ($prayerTime)."
        }

        val notifId = if (isTest) 9999 else (prayerName.hashCode() and 0x7FFFFFFF).coerceAtLeast(1001)
        val soundUri = AzaanSoundStore.selectedSoundUri(appContext, settings)

        if (settings.soundEnabled && soundUri != null) {
            val serviceIntent = Intent(appContext, AzaanPlaybackService::class.java).apply {
                putExtra(AzaanPlaybackService.EXTRA_NOTIFICATION_ID, notifId)
                putExtra(AzaanPlaybackService.EXTRA_TITLE, title)
                putExtra(AzaanPlaybackService.EXTRA_MESSAGE, message)
                putExtra(AzaanPlaybackService.EXTRA_CHANNEL_ID, channelId)
                putExtra(AzaanPlaybackService.EXTRA_SOUND_URI, soundUri.toString())
                putExtra(AzaanPlaybackService.EXTRA_VIBRATE, settings.vibrationEnabled)
            }
            val startedService = runCatching {
                ContextCompat.startForegroundService(appContext, serviceIntent)
                true
            }.getOrDefault(false)

            if (!startedService) {
                // Fallback if background FGS start is ever disallowed (e.g. inexact alarm):
                // post the alarm notification and play directly on STREAM_ALARM.
                val notification = buildNotification(
                    context = appContext,
                    channelId = channelId,
                    notifId = notifId,
                    title = title,
                    message = message,
                    includeStopAction = true
                )
                notificationManager.notify(notifId, notification)
                AzaanAlarmPlayer.play(appContext, soundUri, settings.vibrationEnabled)
            }
        } else {
            stopAzaan(appContext)
            if (settings.vibrationEnabled) {
                AzaanAlarmPlayer.vibrateOnly(appContext)
            }
            val notification = buildNotification(
                context = appContext,
                channelId = channelId,
                notifId = notifId,
                title = title,
                message = message,
                includeStopAction = false
            )
            notificationManager.notify(notifId, notification)
        }
    }

    fun stopAzaan(context: Context, cancelNotificationId: Int = 0) {
        val appContext = context.applicationContext
        AzaanAlarmPlayer.stop(appContext)
        runCatching {
            appContext.stopService(Intent(appContext, AzaanPlaybackService::class.java))
        }
        if (cancelNotificationId != 0) {
            (appContext.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager)
                ?.cancel(cancelNotificationId)
        }
    }
}
