package com.example.notification

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import com.example.MainActivity
import com.example.R
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.UserSettings

object PrayerNotificationManager {
    /**
     * Every channel the app creates is named `<prefix>_<sound>_<vibration>`.
     * The sound and vibration toggles are baked into the channel, so changing
     * either creates a new channel; the old ones are deleted on creation.
     */
    private const val CHANNEL_ID_PREFIX = "namaz_prayer_alarms_v2"
    const val ACTION_PRAYER_REMINDER = "com.example.namaztimes.ACTION_PRAYER_REMINDER"

    const val EXTRA_PRAYER_NAME = "extra_prayer_name"
    const val EXTRA_PRAYER_TIME = "extra_prayer_time"
    const val EXTRA_CITY = "extra_city"
    const val EXTRA_OFFSET = "extra_offset"

    fun createNotificationChannel(context: Context, settings: UserSettings) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val soundUri = AzaanSoundStore.selectedSoundUri(context, settings)
        val channelId = channelIdFor(settings, soundUri)
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return
        if (notificationManager.getNotificationChannel(channelId) != null) return

        val channelTitle = when {
            !settings.soundEnabled -> "Prayer Reminders (Silent)"
            else -> "Prayer Reminders — ${AzaanSoundStore.soundName(settings)}"
        }
        val audioAttributes = AudioAttributes.Builder()
            .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
            // Prayer reminders are scheduled alarms, not ordinary messages. The alarm
            // audio stream remains audible when the phone's ringer is set to silent.
            .setUsage(AudioAttributes.USAGE_ALARM)
            .build()
        val channel = NotificationChannel(
            channelId,
            channelTitle,
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = context.getString(R.string.channel_description)
            enableVibration(settings.vibrationEnabled)
            vibrationPattern = longArrayOf(0, 400, 200, 400)
            setSound(soundUri, audioAttributes)
            // If the user has granted notification-policy access, also permit the
            // prayer alarm through Do Not Disturb. Silent/vibrate mode itself does
            // not require this access because USAGE_ALARM uses alarm volume.
            if (notificationManager.isNotificationPolicyAccessGranted) {
                setBypassDnd(true)
            }
        }
        notificationManager.createNotificationChannel(channel)

        // Deleting a channel's settings is not possible, so when the sound or
        // vibration preference changes a new channel is needed. Remove the
        // channels those earlier choices created, otherwise the app's entry in
        // the system notification settings fills up with stale duplicates.
        notificationManager.notificationChannels
            .map { it.id }
            .filter {
                (it.startsWith("${CHANNEL_ID_PREFIX}_") || it.startsWith("namaz_prayer_reminders_")) &&
                    it != channelId
            }
            .forEach(notificationManager::deleteNotificationChannel)
    }

    private fun channelIdFor(settings: UserSettings, soundUri: Uri?): String {
        val soundKey = if (!settings.soundEnabled) {
            "silent"
        } else {
            val sourceKey = when (settings.azaanSoundId) {
                "madinah" -> "madinah"
                "custom" -> "custom"
                else -> "device"
            }
            "$sourceKey-${Integer.toHexString(soundUri?.toString()?.hashCode() ?: 0)}"
        }
        val vibrationKey = if (settings.vibrationEnabled) "vibrate" else "no-vibrate"
        return "${CHANNEL_ID_PREFIX}_${soundKey}_$vibrationKey"
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
                    val intent = Intent(context, com.example.receiver.PrayerAlarmReceiver::class.java).apply {
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
                            // Fall back to an inexact reminder when exact-alarm access is unavailable.
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
        val intent = Intent(context, com.example.receiver.PrayerAlarmReceiver::class.java).apply {
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

    fun showPrayerNotification(
        context: Context,
        prayerName: String,
        prayerTime: String,
        city: String,
        offsetMinutes: Int,
        settings: UserSettings,
        isTest: Boolean = false
    ) {
        createNotificationChannel(context, settings)

        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return

        val launchIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentPendingIntent = PendingIntent.getActivity(
            context,
            0,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val title = if (isTest) {
            "Test Reminder: $prayerName Prayer"
        } else if (offsetMinutes > 0) {
            "$prayerName Reminder ($offsetMinutes min after)"
        } else {
            "Time for $prayerName Prayer"
        }

        val message = if (isTest) {
            "Notification & sound are working properly. Scheduled time: $prayerTime in $city."
        } else if (offsetMinutes > 0) {
            "$prayerName prayer in $city started $offsetMinutes minutes ago ($prayerTime). It is time for your Salah."
        } else {
            "It is now time for $prayerName prayer in $city ($prayerTime)."
        }

        val channelId = channelIdFor(
            settings,
            AzaanSoundStore.selectedSoundUri(context, settings)
        )
        val builder = NotificationCompat.Builder(context, channelId)
            // Small icons are rendered using only their alpha channel; use the dedicated
            // monochrome mosque vector rather than the full app-logo bitmap.
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(contentPendingIntent)
            .setAutoCancel(true)

        // On Android 8+ the channel owns sound and vibration; older releases use the
        // per-notification fields because notification channels do not exist there.
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            builder.setSound(AzaanSoundStore.selectedSoundUri(context, settings))
            if (settings.vibrationEnabled) {
                builder.setVibrate(longArrayOf(0, 400, 200, 400))
            }
        }

        val notifId = if (isTest) 9999 else prayerName.hashCode()
        notificationManager.notify(notifId, builder.build())
    }
}
