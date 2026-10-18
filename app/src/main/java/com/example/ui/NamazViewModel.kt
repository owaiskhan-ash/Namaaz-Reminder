package com.example.ui

import android.app.Application
import android.net.Uri
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.local.PreferencesManager
import com.example.data.model.AzaanSoundIds
import com.example.data.model.CALCULATION_METHODS
import com.example.data.model.POPULAR_INDIAN_CITIES
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.PrayerType
import com.example.data.model.UserSettings
import com.example.data.repository.PrayerRepository
import com.example.data.repository.PrayerScheduleCustomizer
import com.example.notification.AzaanSoundStore
import com.example.notification.PrayerNotificationManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.util.Locale

data class NamazUiState(
    val isLoading: Boolean = false,
    val schedule: PrayerScheduleData? = null,
    val nextPrayer: PrayerItem? = null,
    val countdownText: String = "--:--:--",
    val countdownSecondsRemaining: Long = 0L,
    val settings: UserSettings = UserSettings(),
    val searchQuery: String = "",
    val suggestedCities: List<String> = POPULAR_INDIAN_CITIES,
    val errorMessage: String? = null,
    val isSettingsOpen: Boolean = false,
    val isCityPickerOpen: Boolean = false,
    val toastMessage: String? = null
)

class NamazViewModel(application: Application) : AndroidViewModel(application) {

    private val preferencesManager = PreferencesManager(application)
    private val repository = PrayerRepository(preferencesManager)

    private val _uiState = MutableStateFlow(NamazUiState())
    val uiState: StateFlow<NamazUiState> = _uiState.asStateFlow()

    private var countdownJob: Job? = null
    private var madinahDownloadJob: Job? = null
    private var madinahSoundReady = false
    private var loadedScheduleDateKey: String? = null
    private var lastExpiredPrayerRefreshMillis: Long? = null

    init {
        val initialSettings = preferencesManager.loadSettings()
        _uiState.update { it.copy(settings = initialSettings) }
        ensureMadinahAzaanDownloaded()
        loadTimings(initialSettings.selectedCity, initialSettings.methodId)
        startCountdownTicker()
    }

    fun loadTimings(city: String, methodId: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val requestSettings = _uiState.value.settings
            val result = repository.getPrayerSchedule(
                city = city,
                methodId = methodId,
                mutedPrayers = requestSettings.mutedPrayerNames
            )

            result.fold(
                onSuccess = { fetchedSchedule ->
                    val latestSettings = _uiState.value.settings
                    val schedule = PrayerScheduleCustomizer.apply(fetchedSchedule, latestSettings)
                    loadedScheduleDateKey = PrayerScheduleCustomizer.dateKey(schedule)
                    val next = schedule.nextPrayer
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            schedule = schedule,
                            nextPrayer = next,
                            errorMessage = null
                        )
                    }
                    updateCountdownDisplay()
                    PrayerNotificationManager.schedulePrayerAlarms(
                        getApplication(),
                        schedule,
                        latestSettings
                    )
                },
                onFailure = { error ->
                    val message = error.localizedMessage ?: "Failed to load prayer times."
                    _uiState.update {
                        it.copy(
                            isLoading = false,
                            errorMessage = message,
                            // The full-screen error state only renders when there is no
                            // schedule to show; surface failures as a snackbar instead so
                            // refresh errors are never silent.
                            toastMessage = if (it.schedule != null) message else it.toastMessage
                        )
                    }
                }
            )
        }
    }

    fun refresh() {
        val current = _uiState.value
        loadTimings(current.settings.selectedCity, current.settings.methodId)
    }

    /**
     * Re-arms alarms from the current schedule + settings. Used when a relevant
     * permission (e.g. SCHEDULE_EXACT_ALARM) was just granted, so pending
     * inexact alarms are upgraded to exact ones without a network refresh.
     */
    fun rescheduleAlarms() {
        val state = _uiState.value
        val schedule = state.schedule ?: return
        PrayerNotificationManager.schedulePrayerAlarms(getApplication(), schedule, state.settings)
    }

    fun onSearchQueryChange(query: String) {
        val filtered = if (query.isBlank()) {
            POPULAR_INDIAN_CITIES
        } else {
            val q = query.trim().lowercase(Locale.ROOT)
            val matches = POPULAR_INDIAN_CITIES.filter { it.lowercase(Locale.ROOT).contains(q) }
            if (matches.none { it.equals(query.trim(), ignoreCase = true) }) {
                // Prepend user's exact typed query if not in popular list
                listOf(query.trim().replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.ROOT) else it.toString() }) + matches
            } else {
                matches
            }
        }
        _uiState.update { it.copy(searchQuery = query, suggestedCities = filtered) }
    }

    fun selectCity(city: String) {
        val clean = city.trim().replaceFirstChar { if (it.isLowerCase()) it.titlecase(Locale.ROOT) else it.toString() }
        if (clean.isBlank()) return

        val newSettings = _uiState.value.settings.copy(selectedCity = clean)
        preferencesManager.saveSettings(newSettings)
        _uiState.update {
            it.copy(
                settings = newSettings,
                searchQuery = "",
                suggestedCities = POPULAR_INDIAN_CITIES,
                isCityPickerOpen = false
            )
        }
        loadTimings(clean, newSettings.methodId)
    }

    fun openCityPicker(open: Boolean) {
        _uiState.update {
            it.copy(
                isCityPickerOpen = open,
                searchQuery = "",
                suggestedCities = POPULAR_INDIAN_CITIES
            )
        }
    }

    fun selectMethod(methodId: Int) {
        val newSettings = _uiState.value.settings.copy(methodId = methodId)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
        loadTimings(newSettings.selectedCity, methodId)
    }

    fun setThemeMode(mode: String) {
        val newSettings = _uiState.value.settings.copy(themeMode = mode)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
    }

    fun toggleNotifications(enabled: Boolean) {
        val newSettings = _uiState.value.settings.copy(notificationsEnabled = enabled)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }

        _uiState.value.schedule?.let { sched ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), sched, newSettings)
        }
    }

    fun setReminderOffset(minutes: Int) {
        val newSettings = _uiState.value.settings.copy(reminderOffsetMinutes = minutes)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }

        _uiState.value.schedule?.let { sched ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), sched, newSettings)
        }
    }

    fun setCustomPrayerTime(prayerName: String, hour: Int, minute: Int) {
        val state = _uiState.value
        val schedule = state.schedule ?: return
        val prayerType = runCatching { PrayerType.valueOf(prayerName) }.getOrNull() ?: return
        if (!prayerType.isPrimaryPrayer) return

        val dayKey = PrayerScheduleCustomizer.dateKey(schedule)
        val overrides = state.settings.customPrayerTimes
            .filterKeys { it.substringBefore('|') == dayKey }
            .toMutableMap()
        overrides[PrayerScheduleCustomizer.customTimeKey(schedule, prayerType)] =
            String.format(Locale.US, "%02d:%02d", hour, minute)
        val newSettings = state.settings.copy(customPrayerTimes = overrides)
        preferencesManager.saveSettings(newSettings)

        val updatedSchedule = PrayerScheduleCustomizer.apply(schedule, newSettings)
        _uiState.update {
            it.copy(
                settings = newSettings,
                schedule = updatedSchedule,
                nextPrayer = updatedSchedule.nextPrayer
            )
        }
        updateCountdownDisplay()
        PrayerNotificationManager.schedulePrayerAlarms(getApplication(), updatedSchedule, newSettings)
    }

    fun clearCustomPrayerTime(prayerName: String) {
        val state = _uiState.value
        val schedule = state.schedule ?: return
        val prayerType = runCatching { PrayerType.valueOf(prayerName) }.getOrNull() ?: return
        val overrides = state.settings.customPrayerTimes.toMutableMap().apply {
            remove(PrayerScheduleCustomizer.customTimeKey(schedule, prayerType))
        }
        val newSettings = state.settings.copy(customPrayerTimes = overrides)
        preferencesManager.saveSettings(newSettings)

        val updatedSchedule = PrayerScheduleCustomizer.apply(schedule, newSettings)
        _uiState.update {
            it.copy(
                settings = newSettings,
                schedule = updatedSchedule,
                nextPrayer = updatedSchedule.nextPrayer
            )
        }
        updateCountdownDisplay()
        PrayerNotificationManager.schedulePrayerAlarms(getApplication(), updatedSchedule, newSettings)
    }

    fun selectAzaan(soundId: String) {
        if (soundId !in setOf(AzaanSoundIds.MADINAH, AzaanSoundIds.DEVICE_DEFAULT, AzaanSoundIds.CUSTOM)) return
        val current = _uiState.value.settings
        if (soundId == AzaanSoundIds.CUSTOM && current.customAzaanUri.isNullOrBlank()) return

        val newSettings = current.copy(azaanSoundId = soundId)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
        PrayerNotificationManager.createNotificationChannel(getApplication(), newSettings)
        _uiState.value.schedule?.let { schedule ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), schedule, newSettings)
        }
    }

    fun importCustomAzaan(sourceUri: Uri) {
        viewModelScope.launch {
            val imported = runCatching {
                withContext(Dispatchers.IO) {
                    AzaanSoundStore.importAzaan(getApplication(), sourceUri)
                }
            }
            imported.fold(
                onSuccess = { sound ->
                    val newSettings = _uiState.value.settings.copy(
                        azaanSoundId = AzaanSoundIds.CUSTOM,
                        customAzaanName = sound.name,
                        customAzaanUri = sound.uri.toString()
                    )
                    preferencesManager.saveSettings(newSettings)
                    _uiState.update {
                        it.copy(
                            settings = newSettings,
                            toastMessage = "${sound.name} saved on this device and selected for reminders."
                        )
                    }
                    PrayerNotificationManager.createNotificationChannel(getApplication(), newSettings)
                    _uiState.value.schedule?.let { schedule ->
                        PrayerNotificationManager.schedulePrayerAlarms(getApplication(), schedule, newSettings)
                    }
                },
                onFailure = { error ->
                    _uiState.update {
                        it.copy(toastMessage = error.localizedMessage ?: "Could not import that audio file.")
                    }
                }
            )
        }
    }

    /** Downloads the supplied Madinah Azaan automatically and retries on resume if offline. */
    fun ensureMadinahAzaanDownloaded() {
        if (madinahDownloadJob?.isActive == true || madinahSoundReady) return
        madinahDownloadJob = viewModelScope.launch {
            val result = runCatching {
                withContext(Dispatchers.IO) {
                    AzaanSoundStore.ensureMadinahAzaanDownloaded(getApplication(), preferencesManager)
                }
            }
            if (result.isSuccess) {
                madinahSoundReady = true
                val latestSettings = _uiState.value.settings
                PrayerNotificationManager.createNotificationChannel(getApplication(), latestSettings)
                rescheduleAlarms()
            } else {
                // Keep the normal device notification sound as a fallback and retry later.
                madinahDownloadJob = null
            }
        }
    }

    fun toggleSound(enabled: Boolean) {
        val newSettings = _uiState.value.settings.copy(soundEnabled = enabled)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }

        _uiState.value.schedule?.let { sched ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), sched, newSettings)
        }
    }

    fun toggleVibration(enabled: Boolean) {
        val newSettings = _uiState.value.settings.copy(vibrationEnabled = enabled)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }

        _uiState.value.schedule?.let { sched ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), sched, newSettings)
        }
    }

    fun toggle24HourFormat(enabled: Boolean) {
        val newSettings = _uiState.value.settings.copy(is24HourFormat = enabled)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
    }

    fun togglePrayerNotification(prayerName: String) {
        val currentMuted = _uiState.value.settings.mutedPrayerNames.toMutableSet()
        if (currentMuted.contains(prayerName)) {
            currentMuted.remove(prayerName)
        } else {
            currentMuted.add(prayerName)
        }
        val newSettings = _uiState.value.settings.copy(mutedPrayerNames = currentMuted)
        preferencesManager.saveSettings(newSettings)

        // Update in-memory prayer item notification states
        val updatedSchedule = _uiState.value.schedule?.let { sched ->
            val updatedPrayers = sched.prayers.map { item ->
                if (item.type.name == prayerName) {
                    item.copy(notificationEnabled = !currentMuted.contains(prayerName))
                } else {
                    item
                }
            }
            sched.copy(prayers = updatedPrayers)
        }

        _uiState.update {
            it.copy(
                settings = newSettings,
                schedule = updatedSchedule
            )
        }

        updatedSchedule?.let { sched ->
            PrayerNotificationManager.schedulePrayerAlarms(getApplication(), sched, newSettings)
        }
    }

    fun sendTestNotification() {
        val current = _uiState.value
        val prayerName = current.nextPrayer?.type?.englishName ?: "Fajr"
        val prayerTime = current.nextPrayer?.displayTime(current.settings.is24HourFormat) ?: "05:00 AM"

        PrayerNotificationManager.showPrayerNotification(
            context = getApplication(),
            prayerName = prayerName,
            prayerTime = prayerTime,
            city = current.settings.selectedCity,
            offsetMinutes = current.settings.reminderOffsetMinutes,
            settings = current.settings,
            isTest = true
        )

        _uiState.update { it.copy(toastMessage = "Test notification sent! Check notification tray.") }
    }

    fun clearCache() {
        preferencesManager.clearCache()
        _uiState.update { it.copy(toastMessage = "Offline cache cleared. Refreshing...") }
        refresh()
    }

    fun openSettings(open: Boolean) {
        _uiState.update { it.copy(isSettingsOpen = open) }
    }

    fun clearToast() {
        _uiState.update { it.copy(toastMessage = null) }
    }

    private fun startCountdownTicker() {
        countdownJob?.cancel()
        countdownJob = viewModelScope.launch {
            while (isActive) {
                updateCountdownDisplay()
                delay(1000L)
            }
        }
    }

    private fun updateCountdownDisplay() {
        val schedule = _uiState.value.schedule ?: return
        val todayKey = PrayerScheduleCustomizer.dateKey(schedule)
        if (loadedScheduleDateKey != null && loadedScheduleDateKey != todayKey) {
            // Date-scoped overrides expire at local midnight, so refresh the schedule
            // once to drop yesterday's custom times and re-arm today's prayers.
            loadedScheduleDateKey = todayKey
            loadTimings(_uiState.value.settings.selectedCity, _uiState.value.settings.methodId)
            return
        }
        val now = System.currentTimeMillis()

        // Check if next prayer passed or needs re-calculation
        val next = schedule.nextPrayer
        if (next == null) {
            _uiState.update { it.copy(countdownText = "--:--:--", countdownSecondsRemaining = 0L) }
            return
        }

        val diffMillis = next.targetEpochMillis - now

        if (diffMillis <= 0) {
            // The ticker runs every second; request a refresh only once for this
            // expired prayer so a slow or failed request cannot spawn a request storm.
            if (lastExpiredPrayerRefreshMillis != next.targetEpochMillis) {
                lastExpiredPrayerRefreshMillis = next.targetEpochMillis
                loadTimings(_uiState.value.settings.selectedCity, _uiState.value.settings.methodId)
            }
            return
        }

        lastExpiredPrayerRefreshMillis = null
        val totalSeconds = diffMillis / 1000
        val hours = totalSeconds / 3600
        val minutes = (totalSeconds % 3600) / 60
        val seconds = totalSeconds % 60

        val formatted = String.format(Locale.US, "%02dh %02dm %02ds", hours, minutes, seconds)
        _uiState.update {
            it.copy(
                countdownText = formatted,
                countdownSecondsRemaining = totalSeconds,
                nextPrayer = next
            )
        }
    }

    override fun onCleared() {
        super.onCleared()
        countdownJob?.cancel()
        madinahDownloadJob?.cancel()
    }
}
