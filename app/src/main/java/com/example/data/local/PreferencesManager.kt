package com.example.data.local

import android.content.Context
import android.content.SharedPreferences
import com.example.data.model.AzaanCatalogue
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
        private const val KEY_CUSTOM_PRAYER_TIMES = "key_custom_prayer_times"
        private const val KEY_SELECTED_AZAAN = "key_selected_azaan"
        private const val KEY_AZAAN_URIS = "key_azaan_uris"
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
        val customTimes = decodeMap(prefs.getString(KEY_CUSTOM_PRAYER_TIMES, null))
        // "none" means the user picked the system sound, a missing value means
        // nothing was picked yet, so the azaan is used by default.
        val selectedAzaan = when (val stored = prefs.getString(KEY_SELECTED_AZAAN, null)) {
            null -> AzaanCatalogue.DEFAULT_AZAAN_ID
            "none" -> null
            else -> stored
        }

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
            selectedAzaanId = selectedAzaan
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
            .putString(KEY_CUSTOM_PRAYER_TIMES, encodeMap(settings.customPrayerTimes))
            .putString(KEY_SELECTED_AZAAN, settings.selectedAzaanId ?: "none")
            .apply()
    }

    /**
     * The uri the notification plays for an azaan, once it was copied to the
     * device. Stored per azaan id.
     */
    fun saveAzaanUri(azaanId: String, uri: String) {
        val uris = decodeMap(prefs.getString(KEY_AZAAN_URIS, null)).toMutableMap()
        uris[azaanId] = uri
        prefs.edit().putString(KEY_AZAAN_URIS, encodeMap(uris)).apply()
    }

    fun getAzaanUri(azaanId: String): String? = decodeMap(prefs.getString(KEY_AZAAN_URIS, null))[azaanId]

    fun removeAzaanUri(azaanId: String) {
        val uris = decodeMap(prefs.getString(KEY_AZAAN_URIS, null)).toMutableMap()
        uris.remove(azaanId)
        prefs.edit().putString(KEY_AZAAN_URIS, encodeMap(uris)).apply()
    }

    /** "KEY=value;KEY=value" -> map. */
    private fun decodeMap(raw: String?): Map<String, String> {
        if (raw.isNullOrBlank()) return emptyMap()
        return raw.split(";")
            .mapNotNull { entry ->
                val separator = entry.indexOf('=')
                if (separator <= 0) {
                    null
                } else {
                    entry.substring(0, separator) to entry.substring(separator + 1)
                }
            }
            .toMap()
    }

    /** map -> "KEY=value;KEY=value". */
    private fun encodeMap(values: Map<String, String>): String =
        values.entries.joinToString(";") { "${it.key}=${it.value}" }

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
