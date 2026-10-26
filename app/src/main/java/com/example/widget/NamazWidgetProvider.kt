package com.example.widget

import android.app.PendingIntent
import android.appwidget.AppWidgetManager
import android.appwidget.AppWidgetProvider
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.SystemClock
import android.widget.RemoteViews
import com.example.MainActivity
import com.example.R
import com.example.data.local.PreferencesManager
import com.example.data.repository.PrayerRepository
import com.example.data.repository.PrayerScheduleCustomizer

/** A lightweight, offline-first widget powered by the schedule already cached by the app. */
class NamazWidgetProvider : AppWidgetProvider() {

    override fun onUpdate(
        context: Context,
        appWidgetManager: AppWidgetManager,
        appWidgetIds: IntArray
    ) {
        updateAll(context)
    }

    override fun onReceive(context: Context, intent: Intent) {
        super.onReceive(context, intent)
        when (intent.action) {
            Intent.ACTION_TIME_CHANGED,
            Intent.ACTION_DATE_CHANGED,
            Intent.ACTION_TIMEZONE_CHANGED -> updateAll(context)
        }
    }

    companion object {
        fun updateAll(context: Context) {
            val appContext = context.applicationContext
            val manager = AppWidgetManager.getInstance(appContext)
            val component = ComponentName(appContext, NamazWidgetProvider::class.java)
            val ids = manager.getAppWidgetIds(component)
            if (ids.isEmpty()) return

            val preferences = PreferencesManager(appContext)
            val settings = preferences.loadSettings()
            val (json, cachedAt) = preferences.getCachedScheduleJson(
                settings.selectedCity,
                settings.methodId
            )

            val schedule = json?.let {
                runCatching {
                    val parsed = PrayerRepository(preferences).parseJsonResponse(
                        jsonStr = it,
                        city = settings.selectedCity,
                        methodId = settings.methodId,
                        mutedPrayers = settings.mutedPrayerNames,
                        isOffline = true,
                        cacheTime = cachedAt
                    )
                    PrayerScheduleCustomizer.apply(parsed, settings)
                }.getOrNull()
            }
            val nextPrayer = schedule?.nextPrayer
            val now = System.currentTimeMillis()

            val views = RemoteViews(appContext.packageName, R.layout.widget_namaz).apply {
                val openApp = PendingIntent.getActivity(
                    appContext,
                    0,
                    Intent(appContext, MainActivity::class.java).apply {
                        flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
                    },
                    PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
                )
                setOnClickPendingIntent(R.id.widget_root, openApp)

                if (schedule != null && nextPrayer != null && nextPrayer.targetEpochMillis > now) {
                    setTextViewText(R.id.widget_city, schedule.city.uppercase())
                    setTextViewText(R.id.widget_prayer, nextPrayer.type.englishName)
                    setTextViewText(
                        R.id.widget_time,
                        nextPrayer.displayTime(settings.is24HourFormat)
                    )
                    val remaining = nextPrayer.targetEpochMillis - now
                    val base = SystemClock.elapsedRealtime() + remaining
                    setChronometer(R.id.widget_countdown, base, "%s", true)
                    setChronometerCountDown(R.id.widget_countdown, true)
                    setViewVisibility(R.id.widget_countdown, android.view.View.VISIBLE)
                    setViewVisibility(R.id.widget_no_schedule, android.view.View.GONE)
                    setViewVisibility(R.id.widget_until_label, android.view.View.VISIBLE)
                } else {
                    setTextViewText(R.id.widget_city, settings.selectedCity.uppercase())
                    setTextViewText(R.id.widget_prayer, appContext.getString(R.string.widget_open_app))
                    setTextViewText(R.id.widget_time, "--:--")
                    setViewVisibility(R.id.widget_countdown, android.view.View.GONE)
                    setViewVisibility(R.id.widget_no_schedule, android.view.View.VISIBLE)
                    setViewVisibility(R.id.widget_until_label, android.view.View.GONE)
                }
            }
            manager.updateAppWidget(ids, views)
        }
    }
}
