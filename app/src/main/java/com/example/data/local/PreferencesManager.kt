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
        private const val KEY_CACHED_PAYLOAD = "key_cached_payload_"
        private const val KEY_LAST_CACHED_TIME = "key_last_cached_time_"
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
