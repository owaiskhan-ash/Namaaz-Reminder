package com.example.notification

import android.content.Context
import com.example.data.local.PreferencesManager
import com.example.data.model.PrayerScheduleData
import com.example.data.repository.PrayerRepository
import kotlinx.coroutines.withTimeoutOrNull

/**
 * Re-arms upcoming prayer alarms from broadcast receivers (after boot and after
 * each fired alarm), so reminders keep working day after day without the user
 * having to open the app.
 *
 * The alarms scheduled by [PrayerNotificationManager.schedulePrayerAlarms] are
 * one-shot: without this re-arm step, reminders silently stopped once the last
 * alarm of a day fired.
 *
 * Strategy (designed for the ~10 s window a `goAsync()` broadcast gets):
 *  1. Try a bounded network refresh via [PrayerRepository.getPrayerSchedule],
 *     which itself falls back to the cached schedule when offline.
 *  2. If that call times out (network hanging), parse the locally cached
 *     schedule directly so alarms are still re-armed immediately.
 *
 * Cached timings are re-anchored to "today" by the parser, which keeps them
 * accurate to within a minute or two; they are refreshed from the network the
 * next time the app is opened.
 */
object AlarmRescheduler {

    private const val FETCH_TIMEOUT_MILLIS = 8_000L

    suspend fun rescheduleAlarms(context: Context) {
        val appContext = context.applicationContext
        val prefs = PreferencesManager(appContext)
        val settings = prefs.loadSettings()
        if (!settings.notificationsEnabled) return

        val repository = PrayerRepository(prefs)

        // 1) Bounded refresh (network with internal cache fallback).
        var schedule: PrayerScheduleData? = withTimeoutOrNull(FETCH_TIMEOUT_MILLIS) {
            repository.getPrayerSchedule(
                city = settings.selectedCity,
                methodId = settings.methodId,
                mutedPrayers = settings.mutedPrayerNames
            )
        }?.getOrNull()

        // 2) Timed out or failed with no usable cache: re-arm from the cached
        //    payload directly so reminders never silently die.
        if (schedule == null) {
            val (cachedJson, cachedAt) = prefs.getCachedScheduleJson(
                settings.selectedCity,
                settings.methodId
            )
            schedule = cachedJson
                ?.takeIf { it.isNotBlank() }
                ?.let { json ->
                    runCatching {
                        repository.parseJsonResponse(
                            jsonStr = json,
                            city = settings.selectedCity,
                            methodId = settings.methodId,
                            mutedPrayers = settings.mutedPrayerNames,
                            isOffline = true,
                            cacheTime = cachedAt
                        )
                    }.getOrNull()
                }
        }

        schedule?.let {
            PrayerNotificationManager.schedulePrayerAlarms(appContext, it, settings)
        }
    }
}
