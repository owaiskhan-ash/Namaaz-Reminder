package com.example.notification

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.os.Build
import androidx.core.app.NotificationCompat
import com.example.MainActivity
import com.example.R
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.UserSettings

object PrayerNotificationManager {
    const val CHANNEL_ID = "namaz_prayer_reminders_channel"
    const val ACTION_PRAYER_REMINDER = "com.example.namaztimes.ACTION_PRAYER_REMINDER"

    const val EXTRA_PRAYER_NAME = "extra_prayer_name"
    const val EXTRA_PRAYER_TIME = "extra_prayer_time"
    const val EXTRA_CITY = "extra_city"
    const val EXTRA_OFFSET = "extra_offset"
    const val EXTRA_SOUND = "extra_sound"
    const val EXTRA_VIBRATE = "extra_vibrate"

    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val name = context.getString(R.string.channel_name)
            val descriptionText = context.getString(R.string.channel_description)
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(CHANNEL_ID, name, importance).apply {
                description = descriptionText
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 400, 200, 400)
                val defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
                val audioAttributes = AudioAttributes.Builder()
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .setUsage(AudioAttributes.USAGE_NOTIFICATION)
                    .build()
                setSound(defaultSoundUri, audioAttributes)
            }
            val notificationManager: NotificationManager =
                context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            notificationManager.createNotificationChannel(channel)
        }
    }

    /**
     * Whether the app is currently allowed to schedule exact alarms.
     * Android 12+ (API 31+) requires SCHEDULE_EXACT_ALARM to be granted by the user
     * (denied by default on Android 14+ for fresh installs of apps targeting 33+).
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
        if (!settings.notificationsEnabled) {
            cancelAllAlarms(context, schedule.prayers)
            return
        }

        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val now = System.currentTimeMillis()
        val offsetMillis = settings.reminderOffsetMinutes * 60 * 1000L
        val canExact = canScheduleExactAlarms(context)

        createNotificationChannel(context)

        schedule.prayers.filter { it.type.isPrimaryPrayer }.forEachIndexed { index, prayer ->
            if (!settings.mutedPrayerNames.contains(prayer.type.name)) {
                val triggerAt = prayer.targetEpochMillis + offsetMillis

                if (triggerAt > now) {
                    val intent = Intent(context, com.example.receiver.PrayerAlarmReceiver::class.java).apply {
                        action = ACTION_PRAYER_REMINDER
                        putExtra(EXTRA_PRAYER_NAME, prayer.type.englishName)
                        putExtra(EXTRA_PRAYER_TIME, prayer.displayTime(settings.is24HourFormat))
                        putExtra(EXTRA_CITY, schedule.city)
                        putExtra(EXTRA_OFFSET, settings.reminderOffsetMinutes)
                        putExtra(EXTRA_SOUND, settings.soundEnabled)
                        putExtra(EXTRA_VIBRATE, settings.vibrationEnabled)
                    }

                    val pendingIntent = PendingIntent.getBroadcast(
                        context,
                        prayer.type.ordinal,
                        intent,
                        PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                    )

                    try {
                        if (canExact && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                            alarmManager.setExactAndAllowWhileIdle(
                                AlarmManager.RTC_WAKEUP,
                                triggerAt,
                                pendingIntent
                            )
                        } else {
                            // SCHEDULE_EXACT_ALARM not granted (or pre-M device):
                            // fall back to an inexact alarm so a reminder still fires,
                            // albeit possibly delayed by system batching/Doze.
                            alarmManager.set(
                                AlarmManager.RTC_WAKEUP,
                                triggerAt,
                                pendingIntent
                            )
                        }
                    } catch (e: SecurityException) {
                        // Defensive: some OEM builds throw even when the check above passed.
                        alarmManager.set(
                            AlarmManager.RTC_WAKEUP,
                            triggerAt,
                            pendingIntent
                        )
                    }
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
        soundEnabled: Boolean = true,
        vibrateEnabled: Boolean = true,
        isTest: Boolean = false
    ) {
        createNotificationChannel(context)

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

        val builder = NotificationCompat.Builder(context, CHANNEL_ID)
            // Small icons are rendered using only the alpha channel; the app logo PNG
            // (opaque RGB) would show as a solid white square, so use the dedicated
            // monochrome mosque silhouette vector instead.
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setContentIntent(contentPendingIntent)
            .setAutoCancel(true)

        if (soundEnabled) {
            val defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
            builder.setSound(defaultSoundUri)
        } else {
            builder.setSilent(true)
        }

        if (vibrateEnabled) {
            builder.setVibrate(longArrayOf(0, 400, 200, 400))
        }

        val notifId = if (isTest) 9999 else prayerName.hashCode()
        notificationManager.notify(notifId, builder.build())
    }
}
