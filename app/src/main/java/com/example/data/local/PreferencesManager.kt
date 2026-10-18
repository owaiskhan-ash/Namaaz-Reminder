package com.example.data.local

import android.content.Context
import android.content.SharedPreferences
import com.example.data.model.UserSettings

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
        private const val KEY_CACHED_PAYLOAD = "key_cached_payload_"
        private const val KEY_LAST_CACHED_TIME = "key_last_cached_time_"
    }

    fun loadSettings(): UserSettings {
        val city = prefs.getString(KEY_CITY, "Delhi") ?: "Delhi"
        val methodId = prefs.getInt(KEY_METHOD_ID, 1)
        val themeMode = prefs.getString(KEY_THEME_MODE, "SYSTEM") ?: "SYSTEM"
        val notifsEnabled = prefs.getBoolean(KEY_NOTIFS_ENABLED, true)
        val offset = prefs.getInt(KEY_OFFSET_MINUTES, 5)
        val sound = prefs.getBoolean(KEY_SOUND_ENABLED, true)
        val vibe = prefs.getBoolean(KEY_VIBE_ENABLED, true)
        val is24h = prefs.getBoolean(KEY_24H_FORMAT, false)
        val muted = prefs.getStringSet(KEY_MUTED_PRAYERS, emptySet()) ?: emptySet()

        return UserSettings(
            selectedCity = city,
            methodId = methodId,
            themeMode = themeMode,
            notificationsEnabled = notifsEnabled,
            reminderOffsetMinutes = offset,
            soundEnabled = sound,
            vibrationEnabled = vibe,
            is24HourFormat = is24h,
            mutedPrayerNames = muted
        )
    }

    fun saveSettings(settings: UserSettings) {
        prefs.edit()
            .putString(KEY_CITY, settings.selectedCity)
            .putInt(KEY_METHOD_ID, settings.methodId)
            .putString(KEY_THEME_MODE, settings.themeMode)
            .putBoolean(KEY_NOTIFS_ENABLED, settings.notificationsEnabled)
            .putInt(KEY_OFFSET_MINUTES, settings.reminderOffsetMinutes)
            .putBoolean(KEY_SOUND_ENABLED, settings.soundEnabled)
            .putBoolean(KEY_VIBE_ENABLED, settings.vibrationEnabled)
            .putBoolean(KEY_24H_FORMAT, settings.is24HourFormat)
            .putStringSet(KEY_MUTED_PRAYERS, settings.mutedPrayerNames)
            .apply()
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
