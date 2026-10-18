package com.example.notification

import android.app.AlarmManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioAttributes
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import androidx.core.app.NotificationCompat
import com.example.MainActivity
import com.example.R
import com.example.data.model.AzaanCatalogue
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import java.util.Calendar

/**
 * Owns the prayer reminders: the notification channels, the exact alarms and
 * the notification content.
 *
 * Design notes:
 *  * **Every prayer gets its own notification id and its own group key.**
 *    Android auto-bundles notifications of the same app as soon as four of
 *    them are active (Android 7.0+), which made the daily reminders collapse
 *    into one merged, indistinguishable group. An explicit group per prayer
 *    keeps each reminder on its own.
 *  * **Stale reminders are pruned.** Reminders posted on an earlier day are
 *    removed, so the shade does not fill up with old, identical looking
 *    reminders (which is also what triggered the auto-bundling above).
 *  * **Sound and vibration are channel properties** from Android 8.0 onwards —
 *    a per-notification `setSound()`/`setVibrate()` is ignored there. Separate
 *    channels are therefore the only way to honour the sound / vibration
 *    toggles in the settings sheet.
 */
object PrayerNotificationManager {
    const val CHANNEL_ID = "namaz_prayer_reminders_channel"
    const val CHANNEL_ID_SOUND_ONLY = "namaz_prayer_reminders_sound_only_channel"
    const val CHANNEL_ID_VIBRATE_ONLY = "namaz_prayer_reminders_vibrate_only_channel"
    const val CHANNEL_ID_SILENT = "namaz_prayer_reminders_silent_channel"

    const val ACTION_PRAYER_REMINDER = "com.example.namaztimes.ACTION_PRAYER_REMINDER"

    const val EXTRA_PRAYER_NAME = "extra_prayer_name"
    const val EXTRA_PRAYER_TIME = "extra_prayer_time"
    const val EXTRA_CITY = "extra_city"
    const val EXTRA_OFFSET = "extra_offset"
    const val EXTRA_SOUND = "extra_sound"
    const val EXTRA_VIBRATE = "extra_vibrate"
    const val EXTRA_PRAYER_EPOCH = "extra_prayer_epoch"
    const val EXTRA_NEXT_PRAYER = "extra_next_prayer"
    const val EXTRA_NEXT_PRAYER_TIME = "extra_next_prayer_time"
    const val EXTRA_AZAAN_URI = "extra_azaan_uri"

    /** First id used by the per-prayer reminder notifications. */
    private const val NOTIFICATION_ID_BASE = 2100

    /**
     * Number of id slots reserved for prayer reminders. A reminder is
     * identified by its prayer (not by the day), so the same prayer always
     * updates the same notification instead of stacking up a new one per day.
     */
    private const val PRAYER_ID_SLOTS = 32

    /** Id of the notification posted by the "Send test notification" action. */
    const val TEST_NOTIFICATION_ID = 9999

    private const val REQUEST_CODE_CONTENT = 0

    /** Ids reserved for prayer reminders. */
    private val PRAYER_NOTIFICATION_IDS = NOTIFICATION_ID_BASE until (NOTIFICATION_ID_BASE + PRAYER_ID_SLOTS)

    fun createNotificationChannel(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return

        val notificationManager: NotificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val defaultSoundUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        val audioAttributes = AudioAttributes.Builder()
            .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
            .setUsage(AudioAttributes.USAGE_NOTIFICATION)
            .build()

        // One channel per sound/vibration combination: the system reads both
        // from the channel, so a single channel cannot honour the toggles.
        createChannel(
            context = context,
            notificationManager = notificationManager,
            channelId = CHANNEL_ID,
            nameRes = R.string.channel_name,
            descriptionRes = R.string.channel_description,
            soundUri = defaultSoundUri,
            audioAttributes = audioAttributes,
            vibrate = true
        )
        createChannel(
            context = context,
            notificationManager = notificationManager,
            channelId = CHANNEL_ID_SOUND_ONLY,
            nameRes = R.string.channel_name_sound_only,
            descriptionRes = R.string.channel_description_sound_only,
            soundUri = defaultSoundUri,
            audioAttributes = audioAttributes,
            vibrate = false
        )
        createChannel(
            context = context,
            notificationManager = notificationManager,
            channelId = CHANNEL_ID_VIBRATE_ONLY,
            nameRes = R.string.channel_name_vibrate_only,
            descriptionRes = R.string.channel_description_vibrate_only,
            soundUri = null,
            audioAttributes = null,
            vibrate = true
        )
        createChannel(
            context = context,
            notificationManager = notificationManager,
            channelId = CHANNEL_ID_SILENT,
            nameRes = R.string.channel_name_silent,
            descriptionRes = R.string.channel_description_silent,
            soundUri = null,
            audioAttributes = null,
            vibrate = false
        )
    }

    private fun createChannel(
        context: Context,
        notificationManager: NotificationManager,
        channelId: String,
        nameRes: Int,
        descriptionRes: Int,
        soundUri: android.net.Uri?,
        audioAttributes: AudioAttributes?,
        vibrate: Boolean
    ) {
        val channel = NotificationChannel(
            channelId,
            context.getString(nameRes),
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = context.getString(descriptionRes)
            enableVibration(vibrate)
            if (vibrate) {
                vibrationPattern = longArrayOf(0, 400, 200, 400)
            }
            if (soundUri != null && audioAttributes != null) {
                setSound(soundUri, audioAttributes)
            } else {
                setSound(null, null)
                enableVibration(vibrate)
            }
        }
        notificationManager.createNotificationChannel(channel)
    }

    /**
     * The channel that matches the user's sound / vibration preferences.
     */
    fun channelIdFor(soundEnabled: Boolean, vibrateEnabled: Boolean): String = when {
        soundEnabled && vibrateEnabled -> CHANNEL_ID
        soundEnabled -> CHANNEL_ID_SOUND_ONLY
        vibrateEnabled -> CHANNEL_ID_VIBRATE_ONLY
        else -> CHANNEL_ID_SILENT
    }

    /**
     * A stable notification id per prayer, so a reminder updates the previous
     * reminder for the same prayer instead of piling up duplicates.
     */
    fun notificationIdFor(prayerName: String): Int {
        val index = PrayerType.entries.indexOfFirst { it.englishName.equals(prayerName, ignoreCase = true) }
        return if (index >= 0) {
            NOTIFICATION_ID_BASE + index
        } else {
            // Unknown prayer name: keep it inside the reserved id range so it is
            // still pruned and cancelled with the other reminders.
            NOTIFICATION_ID_BASE + PRAYER_ID_SLOTS - 1
        }
    }

    /**
     * A group key that is unique per prayer. Notifications that carry an
     * explicit group are never auto-bundled by the system, so each prayer
     * reminder stays a separate notification instead of being merged into one.
     */
    fun groupKeyFor(prayerName: String): String = "namaz_prayer_${notificationIdFor(prayerName)}"

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
            // Reminders that are already in the shade would otherwise stay
            // there even after the user turns reminders off.
            cancelAllPrayerNotifications(context)
            return
        }

        val alarmManager = context.getSystemService(Context.ALARM_SERVICE) as? AlarmManager ?: return
        val now = System.currentTimeMillis()
        val offsetMillis = settings.reminderOffsetMinutes * 60 * 1000L
        val canExact = canScheduleExactAlarms(context)

        createNotificationChannel(context)

        // Reminders from earlier days are removed whenever the schedule is
        // (re)armed, so only the current day's reminders remain in the shade.
        pruneStaleNotifications(context)

        // The azaan that should play with the reminder, if one is selected and
        // it is already saved on the device.
        val azaanUri = settings.selectedAzaanId
            ?.let { AzaanCatalogue.byId(it) }
            ?.let { AzaanManager.notificationUri(context, it) }

        val primaryPrayers = schedule.prayers.filter { it.type.isPrimaryPrayer }
        primaryPrayers.forEachIndexed { index, prayer ->
            if (!settings.mutedPrayerNames.contains(prayer.type.name)) {
                // A time the user set by hand is the one the reminder follows.
                val triggerAt = prayer.effectiveEpochMillis + offsetMillis
                val nextPrayer = primaryPrayers.getOrNull(index + 1)

                if (triggerAt > now) {
                    val intent = Intent(context, com.example.receiver.PrayerAlarmReceiver::class.java).apply {
                        action = ACTION_PRAYER_REMINDER
                        putExtra(EXTRA_PRAYER_NAME, prayer.type.englishName)
                        putExtra(EXTRA_PRAYER_TIME, prayer.effectiveTime(settings.is24HourFormat))
                        putExtra(EXTRA_CITY, schedule.city)
                        putExtra(EXTRA_OFFSET, settings.reminderOffsetMinutes)
                        putExtra(EXTRA_SOUND, settings.soundEnabled)
                        putExtra(EXTRA_VIBRATE, settings.vibrationEnabled)
                        putExtra(EXTRA_PRAYER_EPOCH, prayer.effectiveEpochMillis)
                        putExtra(EXTRA_NEXT_PRAYER, nextPrayer?.type?.englishName)
                        putExtra(
                            EXTRA_NEXT_PRAYER_TIME,
                            nextPrayer?.effectiveTime(settings.is24HourFormat)
                        )
                        putExtra(EXTRA_AZAAN_URI, azaanUri?.toString())
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

    /**
     * Removes every prayer reminder (and the test notification) from the shade.
     */
    fun cancelAllPrayerNotifications(context: Context) {
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return
        PRAYER_NOTIFICATION_IDS.forEach { notificationManager.cancel(it) }
        notificationManager.cancel(TEST_NOTIFICATION_ID)
    }

    /**
     * Removes reminders that were posted on an earlier day. The current day's
     * reminders are kept — they still carry useful information — but the pile
     * of yesterday's reminders is what made the shade look merged.
     */
    fun pruneStaleNotifications(context: Context) {
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.M) return

        val activeNotifications = runCatching { notificationManager.activeNotifications }.getOrNull()
            ?: return
        val dayStart = startOfTodayMillis()
        activeNotifications
            .filter { shouldPruneNotification(it.id, it.postTime, dayStart) }
            .forEach { notificationManager.cancel(it.id) }
    }

    /**
     * Pure helper so the pruning rule can be unit tested: only reminder ids
     * that were posted before the start of today are stale.
     */
    internal fun shouldPruneNotification(id: Int, postTime: Long, dayStart: Long): Boolean =
        id in PRAYER_NOTIFICATION_IDS && postTime < dayStart

    /**
     * Midnight of the current day, used as the cut-off for stale reminders.
     */
    fun startOfTodayMillis(now: Long = System.currentTimeMillis()): Long {
        val calendar = Calendar.getInstance()
        calendar.timeInMillis = now
        calendar.set(Calendar.HOUR_OF_DAY, 0)
        calendar.set(Calendar.MINUTE, 0)
        calendar.set(Calendar.SECOND, 0)
        calendar.set(Calendar.MILLISECOND, 0)
        return calendar.timeInMillis
    }

    fun showPrayerNotification(
        context: Context,
        prayerName: String,
        prayerTime: String,
        city: String,
        offsetMinutes: Int,
        soundEnabled: Boolean = true,
        vibrateEnabled: Boolean = true,
        isTest: Boolean = false,
        prayerEpochMillis: Long = 0L,
        nextPrayerLabel: String? = null,
        azaanUri: Uri? = null
    ) {
        val notificationManager =
            context.getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager ?: return

        val notification = buildPrayerNotification(
            context = context,
            prayerName = prayerName,
            prayerTime = prayerTime,
            city = city,
            offsetMinutes = offsetMinutes,
            soundEnabled = soundEnabled,
            vibrateEnabled = vibrateEnabled,
            isTest = isTest,
            prayerEpochMillis = prayerEpochMillis,
            nextPrayerLabel = nextPrayerLabel,
            azaanUri = azaanUri
        )

        val notificationId = if (isTest) TEST_NOTIFICATION_ID else notificationIdFor(prayerName)
        notificationManager.notify(notificationId, notification)

        if (!isTest) {
            pruneStaleNotifications(context)
        }
    }

    /**
     * Builds the prayer reminder notification.
     *
     * Every reminder gets its own group, its own id and a timestamp that points
     * at the prayer time rather than at the moment the reminder was posted, so
     * the daily reminders stay separate, identifiable notifications instead of
     * being merged into one bundle.
     */
    fun buildPrayerNotification(
        context: Context,
        prayerName: String,
        prayerTime: String,
        city: String,
        offsetMinutes: Int,
        soundEnabled: Boolean = true,
        vibrateEnabled: Boolean = true,
        isTest: Boolean = false,
        prayerEpochMillis: Long = 0L,
        nextPrayerLabel: String? = null,
        azaanUri: Uri? = null
    ): android.app.Notification {
        createNotificationChannel(context)

        val launchIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val contentPendingIntent = PendingIntent.getActivity(
            context,
            REQUEST_CODE_CONTENT,
            launchIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val title = when {
            isTest -> "Test reminder - $prayerName"
            offsetMinutes > 0 -> "$prayerName prayer - ${offsetMinutes}m after adhan"
            else -> "Time for $prayerName prayer"
        }

        val message = buildString {
            if (isTest) {
                append("Notification and sound are working properly. ")
                append("$prayerName is scheduled for $prayerTime in $city.")
            } else if (offsetMinutes > 0) {
                append("$prayerName prayer started $offsetMinutes minute(s) ago in $city ($prayerTime).")
            } else {
                append("It is now time for $prayerName prayer in $city ($prayerTime).")
            }
            if (!isTest && !nextPrayerLabel.isNullOrBlank()) {
                append("\nNext: $nextPrayerLabel")
            }
        }

        // When an azaan is used it is set on the notification itself, so the
        // channel has to stay silent - the system only plays the sound of a
        // notification when its channel does not define one.
        val useAzaan = azaanUri != null && soundEnabled
        val channelId = if (useAzaan) {
            if (vibrateEnabled) CHANNEL_ID_VIBRATE_ONLY else CHANNEL_ID_SILENT
        } else {
            channelIdFor(soundEnabled = soundEnabled, vibrateEnabled = vibrateEnabled)
        }

        val builder = NotificationCompat.Builder(context, channelId)
            // Small icons are rendered using only the alpha channel; the app logo PNG
            // (opaque RGB) would show as a solid white square, so use the dedicated
            // monochrome mosque silhouette vector instead.
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(message)
            .setSubText(city)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setContentIntent(contentPendingIntent)
            .setAutoCancel(true)
            // Its own group, so the system never merges the daily reminders into
            // a single bundled notification.
            .setGroup(groupKeyFor(prayerName))
            .setGroupAlertBehavior(NotificationCompat.GROUP_ALERT_ALL)
            .setVisibility(NotificationCompat.VISIBILITY_PRIVATE)

        if (prayerEpochMillis > 0L) {
            // Show the prayer time as the notification timestamp instead of the
            // moment the reminder happened to be posted.
            builder.setWhen(prayerEpochMillis).setShowWhen(true)
        }

        if (useAzaan) {
            builder.setSound(azaanUri)
        } else if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) {
            // From Android 8.0 onwards the channel decides; see createNotificationChannel.
            if (soundEnabled) {
                builder.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
            } else {
                builder.setSilent(true)
            }
            if (vibrateEnabled) {
                builder.setVibrate(longArrayOf(0, 400, 200, 400))
            }
        }

        return builder.build()
    }
}
