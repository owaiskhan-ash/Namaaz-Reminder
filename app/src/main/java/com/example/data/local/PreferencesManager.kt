package com.example.data.local

import android.content.Context
import android.content.SharedPreferences
import com.example.data.model.AzaanSoundIds
import com.example.data.model.UserSettings
import org.json.JSONObject

class PreferencesManager(context: Context) {
    private val prefs: SharedPreferences =
        context.getSharedPreferences("namaz_times_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_CITY = "key_selected_city"
        private const val KEY_METHOD_ID = "key_method_id"
        private const val KEY_THEME_MODE = "key_theme_mode"
        private const val KEY_NOTIFS_ENABLED = "key_notifs_enabled"
        private const val KEY_OFFSET_MINUTES = "key_offset_minutes"
        private const val KEY_SOUND_ENABLED = "key_sound_enabled"
        private const val KEY_VIBE_ENABLED = "key_vibe_enabled"
        private const val KEY_24H_FORMAT = "key_24h_format"
        private const val KEY_MUTED_PRAYERS = "key_muted_prayers"
        private const val KEY_CUSTOM_PRAYER_TIMES = "key_custom_prayer_times"
        private const val KEY_AZAAN_SOUND_ID = "key_azaan_sound_id"
        private const val KEY_CUSTOM_AZAAN_NAME = "key_custom_azaan_name"
        private const val KEY_CUSTOM_AZAAN_URI = "key_custom_azaan_uri"
        private const val KEY_MADINAH_AZAAN_URI = "key_madinah_azaan_uri"
        private const val KEY_DELIVERED_REMINDERS = "key_delivered_reminders"
        private const val KEY_CACHED_PAYLOAD = "key_cached_payload_"
        private const val KEY_LAST_CACHED_TIME = "key_last_cached_time_"

        // A prayer reminder is a one-time event. Persisting recently delivered
        // IDs protects against an AlarmManager/OEM re-delivery after the app
        // process has been restarted, not only duplicate broadcasts in memory.
        private const val DELIVERED_REMINDER_RETENTION_MILLIS = 3L * 24L * 60L * 60L * 1000L
        private val deliveredReminderLock = Any()
    }

    fun loadSettings(): UserSettings {
        val city = prefs.getString(KEY_CITY, "Delhi") ?: "Delhi"
        val methodId = prefs.getInt(KEY_METHOD_ID, 1)
        val themeMode = prefs.getString(KEY_THEME_MODE, "DARK") ?: "DARK"
        val notifsEnabled = prefs.getBoolean(KEY_NOTIFS_ENABLED, true)
        val offset = prefs.getInt(KEY_OFFSET_MINUTES, 5)
        val sound = prefs.getBoolean(KEY_SOUND_ENABLED, true)
        val vibe = prefs.getBoolean(KEY_VIBE_ENABLED, true)
        val is24h = prefs.getBoolean(KEY_24H_FORMAT, false)
        val muted = prefs.getStringSet(KEY_MUTED_PRAYERS, emptySet())?.toSet() ?: emptySet()
        val customTimes = loadCustomPrayerTimes()
        val azaanSoundId = prefs.getString(KEY_AZAAN_SOUND_ID, AzaanSoundIds.MADINAH)
            ?: AzaanSoundIds.MADINAH

        return UserSettings(
            selectedCity = city,
            methodId = methodId,
            themeMode = themeMode,
            notificationsEnabled = notifsEnabled,
            reminderOffsetMinutes = offset,
            soundEnabled = sound,
            vibrationEnabled = vibe,
            is24HourFormat = is24h,
            mutedPrayerNames = muted,
            customPrayerTimes = customTimes,
            azaanSoundId = azaanSoundId,
            customAzaanName = prefs.getString(KEY_CUSTOM_AZAAN_NAME, null),
            customAzaanUri = prefs.getString(KEY_CUSTOM_AZAAN_URI, null)
        )
    }

    fun saveSettings(settings: UserSettings) {
        val editor = prefs.edit()
            .putString(KEY_CITY, settings.selectedCity)
            .putInt(KEY_METHOD_ID, settings.methodId)
            .putString(KEY_THEME_MODE, settings.themeMode)
            .putBoolean(KEY_NOTIFS_ENABLED, settings.notificationsEnabled)
            .putInt(KEY_OFFSET_MINUTES, settings.reminderOffsetMinutes)
            .putBoolean(KEY_SOUND_ENABLED, settings.soundEnabled)
            .putBoolean(KEY_VIBE_ENABLED, settings.vibrationEnabled)
            .putBoolean(KEY_24H_FORMAT, settings.is24HourFormat)
            .putStringSet(KEY_MUTED_PRAYERS, settings.mutedPrayerNames.toSet())
            .putString(KEY_CUSTOM_PRAYER_TIMES, JSONObject(settings.customPrayerTimes).toString())
            .putString(KEY_AZAAN_SOUND_ID, settings.azaanSoundId)

        if (settings.customAzaanName == null) {
            editor.remove(KEY_CUSTOM_AZAAN_NAME)
        } else {
            editor.putString(KEY_CUSTOM_AZAAN_NAME, settings.customAzaanName)
        }
        if (settings.customAzaanUri == null) {
            editor.remove(KEY_CUSTOM_AZAAN_URI)
        } else {
            editor.putString(KEY_CUSTOM_AZAAN_URI, settings.customAzaanUri)
        }
        editor.apply()
    }

    fun getMadinahAzaanUri(): String? = prefs.getString(KEY_MADINAH_AZAAN_URI, null)

    fun saveMadinahAzaanUri(uri: String) {
        prefs.edit().putString(KEY_MADINAH_AZAAN_URI, uri).apply()
    }

    fun clearMadinahAzaanUri() {
        prefs.edit().remove(KEY_MADINAH_AZAAN_URI).apply()
    }

    /**
     * Claims a scheduled reminder before its notification/audio is started.
     *
     * Alarm broadcasts can occasionally be redelivered by Android or device
     * vendors. The claim is synchronous and shared by all [PreferencesManager]
     * instances in this process, so exactly one delivery of a prayer event may
     * start the Azaan. Old entries are kept only long enough to cover a delayed
     * re-delivery and are then pruned.
     */
    fun claimReminderDelivery(reminderId: String, deliveredAtMillis: Long = System.currentTimeMillis()): Boolean {
        if (reminderId.isBlank()) return true

        synchronized(deliveredReminderLock) {
            val delivered = runCatching {
                JSONObject(prefs.getString(KEY_DELIVERED_REMINDERS, "{}") ?: "{}")
            }.getOrElse { JSONObject() }

            val existingDelivery = delivered.optLong(reminderId, 0L)
            if (existingDelivery > 0L &&
                deliveredAtMillis >= existingDelivery &&
                deliveredAtMillis - existingDelivery < DELIVERED_REMINDER_RETENTION_MILLIS
            ) {
                return false
            }

            val keys = delivered.keys()
            val expiredKeys = mutableListOf<String>()
            while (keys.hasNext()) {
                val key = keys.next()
                val deliveredAt = delivered.optLong(key, 0L)
                if (deliveredAt <= 0L ||
                    deliveredAtMillis - deliveredAt >= DELIVERED_REMINDER_RETENTION_MILLIS
                ) {
                    expiredKeys += key
                }
            }
            expiredKeys.forEach { delivered.remove(it) }
            delivered.put(reminderId, deliveredAtMillis)

            // `commit` makes the claim visible before this receiver can return
            // and another copy of the broadcast is dispatched.
            return prefs.edit()
                .putString(KEY_DELIVERED_REMINDERS, delivered.toString())
                .commit()
        }
    }

    private fun loadCustomPrayerTimes(): Map<String, String> {
        val json = prefs.getString(KEY_CUSTOM_PRAYER_TIMES, null) ?: return emptyMap()
        return runCatching {
            val objectValue = JSONObject(json)
            buildMap {
                val keys = objectValue.keys()
                while (keys.hasNext()) {
                    val key = keys.next()
                    val value = objectValue.optString(key, "")
                    if (value.isNotBlank()) put(key, value)
                }
            }
        }.getOrDefault(emptyMap())
    }

    fun saveCachedScheduleJson(city: String, methodId: Int, json: String) {
        val cacheKey = "$city-$methodId".lowercase()
        prefs.edit()
            .putString(KEY_CACHED_PAYLOAD + cacheKey, json)
            .putLong(KEY_LAST_CACHED_TIME + cacheKey, System.currentTimeMillis())
            .apply()
    }

    fun getCachedScheduleJson(city: String, methodId: Int): Pair<String?, Long> {
        val cacheKey = "$city-$methodId".lowercase()
        val json = prefs.getString(KEY_CACHED_PAYLOAD + cacheKey, null)
        val timestamp = prefs.getLong(KEY_LAST_CACHED_TIME + cacheKey, 0L)
        return Pair(json, timestamp)
    }

    fun clearCache() {
        val allKeys = prefs.all.keys
        val editor = prefs.edit()
        for (k in allKeys) {
            if (k.startsWith(KEY_CACHED_PAYLOAD) || k.startsWith(KEY_LAST_CACHED_TIME)) {
                editor.remove(k)
            }
        }
        editor.apply()
    }
}
