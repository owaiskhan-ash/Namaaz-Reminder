package com.example.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.local.PreferencesManager
import com.example.data.model.AzaanCatalogue
import com.example.data.model.AzaanSound
import com.example.data.model.CALCULATION_METHODS
import com.example.data.model.POPULAR_INDIAN_CITIES
import com.example.data.model.PrayerItem
import com.example.data.model.PrayerScheduleData
import com.example.data.model.UserSettings
import com.example.data.repository.PrayerRepository
import com.example.notification.AzaanManager
import com.example.notification.PrayerNotificationManager
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
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
    val toastMessage: String? = null,
    /** The azaans the user can pick as the reminder sound. */
    val azaans: List<AzaanSound> = emptyList()
)

class NamazViewModel(application: Application) : AndroidViewModel(application) {

    private val preferencesManager = PreferencesManager(application)
    private val repository = PrayerRepository(preferencesManager)

    private val _uiState = MutableStateFlow(NamazUiState())
    val uiState: StateFlow<NamazUiState> = _uiState.asStateFlow()

    private var countdownJob: Job? = null
    private var lastExpiredPrayerRefreshMillis: Long? = null
    private var downloadingAzaanId: String? = null
    private val failedAzaanIds = mutableSetOf<String>()

    init {
        val initialSettings = preferencesManager.loadSettings()
        _uiState.update { it.copy(settings = initialSettings) }
        loadTimings(initialSettings.selectedCity, initialSettings.methodId)
        startCountdownTicker()
        refreshAzaans()

        // The azaan is saved on the device automatically, so the reminder can
        // play it even when the phone is offline.
        initialSettings.selectedAzaanId?.let { azaanId ->
            val azaan = AzaanCatalogue.byId(azaanId)
            if (azaan != null && !AzaanManager.isDownloaded(getApplication(), azaan)) {
                downloadAzaan(azaanId)
            }
        }
    }

    fun loadTimings(city: String, methodId: Int) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, errorMessage = null) }
            val currentSettings = _uiState.value.settings
            val result = repository.getPrayerSchedule(
                city = city,
                methodId = methodId,
                mutedPrayers = currentSettings.mutedPrayerNames,
                customTimes = currentSettings.customPrayerTimes
            )

            result.fold(
                onSuccess = { schedule ->
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
                    // Reschedule alarms
                    PrayerNotificationManager.schedulePrayerAlarms(
                        getApplication(),
                        schedule,
                        currentSettings
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

        // The test reminder plays the azaan the user picked, if there is one.
        val azaanUri = current.settings.selectedAzaanId
            ?.let { AzaanCatalogue.byId(it) }
            ?.let { AzaanManager.notificationUri(getApplication(), it) }

        PrayerNotificationManager.showPrayerNotification(
            context = getApplication(),
            prayerName = prayerName,
            prayerTime = prayerTime,
            city = current.settings.selectedCity,
            offsetMinutes = current.settings.reminderOffsetMinutes,
            soundEnabled = current.settings.soundEnabled,
            vibrateEnabled = current.settings.vibrationEnabled,
            isTest = true,
            prayerEpochMillis = current.nextPrayer?.effectiveEpochMillis ?: 0L,
            azaanUri = azaanUri
        )

        _uiState.update { it.copy(toastMessage = "Test notification sent! Check notification tray.") }
    }

    /**
     * Sets a prayer time by hand. The custom time is shown next to the
     * calculated one and is used for the countdown and the reminder.
     */
    fun setCustomPrayerTime(prayerName: String, hour: Int, minute: Int) {
        val customTimes = _uiState.value.settings.customPrayerTimes.toMutableMap()
        customTimes[prayerName] = String.format(Locale.US, "%02d:%02d", hour, minute)
        val newSettings = _uiState.value.settings.copy(customPrayerTimes = customTimes)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
        applyCustomTimesToSchedule()
        _uiState.update {
            it.copy(toastMessage = "Custom time saved for $prayerName.")
        }
    }

    /** Removes the hand set time of a prayer again. */
    fun clearCustomPrayerTime(prayerName: String) {
        val customTimes = _uiState.value.settings.customPrayerTimes.toMutableMap()
        if (customTimes.remove(prayerName) == null) return
        val newSettings = _uiState.value.settings.copy(customPrayerTimes = customTimes)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
        applyCustomTimesToSchedule()
        _uiState.update {
            it.copy(toastMessage = "Custom time removed for $prayerName.")
        }
    }

    /** Re-applies the hand set times to the schedule that is already loaded. */
    private fun applyCustomTimesToSchedule() {
        val schedule = _uiState.value.schedule ?: return
        val settings = _uiState.value.settings
        val updated = repository.applyCustomTimes(schedule, settings.customPrayerTimes)
        _uiState.update { it.copy(schedule = updated, nextPrayer = updated.nextPrayer) }
        updateCountdownDisplay()
        PrayerNotificationManager.schedulePrayerAlarms(getApplication(), updated, settings)
    }

    /** Picks the azaan that is used as the reminder sound (null = system sound). */
    fun selectAzaan(azaanId: String?) {
        val newSettings = _uiState.value.settings.copy(selectedAzaanId = azaanId)
        preferencesManager.saveSettings(newSettings)
        _uiState.update { it.copy(settings = newSettings) }
        if (azaanId != null) {
            // Make sure the azaan is on the device before it is used.
            downloadAzaan(azaanId)
        }
        rescheduleAlarms()
    }

    /** Downloads an azaan and saves it on the device. */
    fun downloadAzaan(azaanId: String) {
        val azaan = AzaanCatalogue.byId(azaanId) ?: return
        if (downloadingAzaanId == azaanId) return
        viewModelScope.launch {
            downloadingAzaanId = azaanId
            failedAzaanIds.remove(azaanId)
            refreshAzaans()

            val downloaded = AzaanManager.download(getApplication(), azaan)
            if (downloaded.isSuccess) {
                AzaanManager.install(getApplication(), azaan)
            } else {
                failedAzaanIds.add(azaanId)
            }

            downloadingAzaanId = null
            refreshAzaans()
            rescheduleAlarms()
        }
    }

    /** Plays an azaan so the user can hear it. */
    fun previewAzaan(azaanId: String) {
        val azaan = AzaanCatalogue.byId(azaanId) ?: return
        if (!AzaanManager.isDownloaded(getApplication(), azaan)) {
            downloadAzaan(azaanId)
            return
        }
        AzaanManager.preview(getApplication(), azaan)
    }

    /** Refreshes the download state of every azaan. */
    private fun refreshAzaans() {
        val context = getApplication<Application>()
        val sounds = AzaanCatalogue.sounds.map { azaan ->
            azaan.copy(
                isDownloaded = AzaanManager.isDownloaded(context, azaan),
                isDownloading = downloadingAzaanId == azaan.id,
                hasFailed = failedAzaanIds.contains(azaan.id)
            )
        }
        _uiState.update { it.copy(azaans = sounds) }
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
        val now = System.currentTimeMillis()

        // Check if next prayer passed or needs re-calculation
        val next = schedule.nextPrayer
        if (next == null) {
            _uiState.update { it.copy(countdownText = "--:--:--", countdownSecondsRemaining = 0L) }
            return
        }

        val diffMillis = next.effectiveEpochMillis - now

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
    }
}
