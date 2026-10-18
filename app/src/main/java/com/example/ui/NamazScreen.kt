package com.example.ui

import android.Manifest
import android.app.AlertDialog
import android.app.TimePickerDialog
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import android.text.format.DateUtils
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CloudOff
import androidx.compose.material.icons.filled.Info
import androidx.compose.material.icons.filled.KeyboardArrowDown
import androidx.compose.material.icons.filled.KeyboardArrowUp
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.NotificationsActive
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.data.model.PrayerItem
import com.example.notification.PrayerNotificationManager
import com.example.ui.components.CitySelectionSheet
import com.example.ui.components.HeroCountdownCard
import com.example.ui.components.NamazTopBar
import com.example.ui.components.PrayerTimeCard
import com.example.ui.components.SettingsSheet

@Composable
fun NamazScreen(
    viewModel: NamazViewModel,
    modifier: Modifier = Modifier
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val isDarkTheme = when (uiState.settings.themeMode) {
        "DARK" -> true
        "LIGHT" -> false
        else -> isSystemInDarkTheme()
    }
    val snackbarHostState = remember { SnackbarHostState() }

    var hasNotificationPermission by remember {
        mutableStateOf(checkNotificationPermission(context))
    }
    var canScheduleExactAlarms by remember {
        mutableStateOf(PrayerNotificationManager.canScheduleExactAlarms(context))
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        hasNotificationPermission = isGranted
    }

    val audioPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.OpenDocument()
    ) { audioUri ->
        if (audioUri != null) {
            runCatching {
                context.contentResolver.takePersistableUriPermission(
                    audioUri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION
                )
            }
            viewModel.importCustomAzaan(audioUri)
        }
    }

    var isAstronomicalExpanded by remember { mutableStateOf(false) }

    // Ask for notification permission on load as required by user prompt
    LaunchedEffect(Unit) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && !hasNotificationPermission) {
            permissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    // Re-check permission states every time the app returns to the foreground.
    // This keeps the banners honest when permission was granted (or revoked)
    // from system settings, and upgrades pending inexact alarms to exact ones
    // as soon as SCHEDULE_EXACT_ALARM becomes available.
    val lifecycleOwner = LocalLifecycleOwner.current
    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) {
                hasNotificationPermission = checkNotificationPermission(context)
                viewModel.ensureMadinahAzaanDownloaded()
                val exactAlarmsNow = PrayerNotificationManager.canScheduleExactAlarms(context)
                if (exactAlarmsNow && !canScheduleExactAlarms) {
                    viewModel.rescheduleAlarms()
                }
                canScheduleExactAlarms = exactAlarmsNow
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose { lifecycleOwner.lifecycle.removeObserver(observer) }
    }

    // Handle toast messages
    LaunchedEffect(uiState.toastMessage) {
        uiState.toastMessage?.let { msg ->
            snackbarHostState.showSnackbar(msg)
            viewModel.clearToast()
        }
    }

    fun showTimePicker(prayer: PrayerItem) {
        val currentTime = prayer.customTime ?: prayer.rawTime
        val parts = currentTime.split(":")
        val hour = parts.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23) ?: 12
        val minute = parts.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59) ?: 0
        TimePickerDialog(
            context,
            { _, selectedHour, selectedMinute ->
                viewModel.setCustomPrayerTime(prayer.type.name, selectedHour, selectedMinute)
            },
            hour,
            minute,
            uiState.settings.is24HourFormat
        ).show()
    }


    // Long press a card to set a custom time. When one is already set, offer to
    // change or clear it - otherwise a custom time could never be undone.
    fun showPrayerTimePicker(prayer: PrayerItem) {
        if (prayer.customTime == null) {
            showTimePicker(prayer)
            return
        }
        AlertDialog.Builder(context)
            .setTitle("${prayer.type.englishName} — custom time")
            .setMessage(
                "The calculated time today is " +
                    prayer.defaultDisplayTime(uiState.settings.is24HourFormat) + "."
            )
            .setPositiveButton("Change time") { _, _ -> showTimePicker(prayer) }
            .setNeutralButton("Reset to calculated") { _, _ ->
                viewModel.clearCustomPrayerTime(prayer.type.name)
            }
            .setNegativeButton("Cancel", null)
            .show()
    }

    Scaffold(
        modifier = modifier.fillMaxSize(),
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = MaterialTheme.colorScheme.background,
        topBar = {
            NamazTopBar(
                modifier = Modifier.statusBarsPadding(),
                isLoading = uiState.isLoading,
                currentCity = uiState.settings.selectedCity,
                currentTheme = if (isDarkTheme) "DARK" else "LIGHT",
                onToggleTheme = {
                    // Toggle against the effective theme so a first tap also changes
                    // appearance when the saved mode was SYSTEM.
                    viewModel.setThemeMode(if (isDarkTheme) "LIGHT" else "DARK")
                },
                onOpenCityPicker = { viewModel.openCityPicker(true) },
                onOpenSettings = { viewModel.openSettings(true) }
            )
        }
    ) { innerPadding ->
        BoxWithConstraints(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Adaptive max-width container for phones, foldables, and tablets
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .widthIn(max = 640.dp)
                    .align(Alignment.TopCenter)
            ) {
                // Notification Permission Banner (if not granted on API 33+)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU && !hasNotificationPermission) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 4.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(MaterialTheme.colorScheme.surfaceVariant)
                            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(10.dp))
                            .clickable { permissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS) }
                            .padding(horizontal = 14.dp, vertical = 10.dp)
                            .testTag("enable_permission_banner")
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.weight(1f)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.NotificationsActive,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.onBackground,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(
                                    text = "Enable notifications for prayer reminder alerts",
                                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                            }
                            Text(
                                text = "ENABLE",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    letterSpacing = 1.sp
                                ),
                                color = MaterialTheme.colorScheme.onBackground
                            )
                        }
                    }
                }

                // Exact-Alarm Permission Banner (Android 12+; without it reminders
                // fall back to inexact alarms that can fire minutes-to-hours late)
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S &&
                    !canScheduleExactAlarms &&
                    uiState.settings.notificationsEnabled
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 4.dp)
                            .clip(RoundedCornerShape(10.dp))
                            .background(MaterialTheme.colorScheme.surfaceVariant)
                            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(10.dp))
                            .clickable { openExactAlarmSettings(context) }
                            .padding(horizontal = 14.dp, vertical = 10.dp)
                            .testTag("exact_alarm_banner")
                    ) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween,
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Row(
                                verticalAlignment = Alignment.CenterVertically,
                                modifier = Modifier.weight(1f)
                            ) {
                                Icon(
                                    imageVector = Icons.Default.Schedule,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.onBackground,
                                    modifier = Modifier.size(18.dp)
                                )
                                Spacer(modifier = Modifier.width(10.dp))
                                Text(
                                    text = "Allow alarms & reminders for on-time prayer alerts",
                                    style = MaterialTheme.typography.bodySmall.copy(fontWeight = FontWeight.Medium),
                                    color = MaterialTheme.colorScheme.onBackground
                                )
                            }
                            Text(
                                text = "ALLOW",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Bold,
                                    letterSpacing = 1.sp
                                ),
                                color = MaterialTheme.colorScheme.onBackground
                            )
                        }
                    }
                }

                // Offline Cache Banner (if serving from offline cache)
                val schedule = uiState.schedule
                if (schedule?.isOfflineCache == true) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(horizontal = 16.dp, vertical = 4.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(8.dp))
                            .background(MaterialTheme.colorScheme.surface)
                            .padding(horizontal = 12.dp, vertical = 6.dp)
                            .testTag("offline_cache_indicator")
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = Icons.Default.CloudOff,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.size(14.dp)
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = buildString {
                                    append("Offline Mode • Displaying cached prayer times")
                                    if (schedule.cachedAtMillis > 0L) {
                                        val age = DateUtils.getRelativeTimeSpanString(
                                            schedule.cachedAtMillis,
                                            System.currentTimeMillis(),
                                            DateUtils.MINUTE_IN_MILLIS
                                        )
                                        append(" (cached ").append(age).append(")")
                                    }
                                },
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant
                            )
                        }
                    }
                }

                // Error State (when no data and network failed)
                if (uiState.errorMessage != null && schedule == null) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .padding(32.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Column(
                            horizontalAlignment = Alignment.CenterHorizontally
                        ) {
                            Icon(
                                imageVector = Icons.Default.Info,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.onBackground,
                                modifier = Modifier.size(48.dp)
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Text(
                                text = uiState.errorMessage ?: "Network Error",
                                style = MaterialTheme.typography.bodyMedium,
                                color = MaterialTheme.colorScheme.onBackground
                            )
                            Spacer(modifier = Modifier.height(16.dp))
                            Button(
                                onClick = { viewModel.refresh() },
                                shape = RoundedCornerShape(8.dp),
                                colors = ButtonDefaults.buttonColors(
                                    containerColor = MaterialTheme.colorScheme.onBackground,
                                    contentColor = MaterialTheme.colorScheme.background
                                ),
                                modifier = Modifier.testTag("retry_button")
                            ) {
                                Text("Retry Connection")
                            }
                        }
                    }
                } else {
                    // Main Scrollable Content
                    LazyColumn(
                        modifier = Modifier
                            .fillMaxWidth()
                            .weight(1f),
                        contentPadding = PaddingValues(bottom = 32.dp)
                    ) {
                        // Date & Method Header with clickable location selection shortcut
                        item {
                            schedule?.let { data ->
                                DateHeader(
                                    city = data.city,
                                    dateGregorian = data.dateGregorian,
                                    dateHijri = data.dateHijri,
                                    methodName = data.methodName,
                                    onOpenCityPicker = { viewModel.openCityPicker(true) }
                                )
                            }
                        }

                        // Hero Countdown Card (Highlighted Next Prayer)
                        item {
                            HeroCountdownCard(
                                nextPrayer = uiState.nextPrayer,
                                countdownText = uiState.countdownText,
                                city = uiState.settings.selectedCity,
                                reminderOffsetMinutes = uiState.settings.reminderOffsetMinutes,
                                use24Hour = uiState.settings.is24HourFormat,
                                onToggleReminder = { prayerName ->
                                    viewModel.togglePrayerNotification(prayerName)
                                },
                                onOpenCityPicker = { viewModel.openCityPicker(true) }
                            )
                        }

                        // Section Title: TODAY'S PRAYERS
                        item {
                            Row(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 18.dp, vertical = 8.dp),
                                horizontalArrangement = Arrangement.SpaceBetween,
                                verticalAlignment = Alignment.CenterVertically
                            ) {
                                Text(
                                    text = "TODAY'S PRAYERS",
                                    style = MaterialTheme.typography.labelMedium.copy(
                                        fontWeight = FontWeight.Bold,
                                        letterSpacing = 1.2.sp
                                    ),
                                    color = MaterialTheme.colorScheme.onBackground
                                )

                                Text(
                                    text = if (uiState.settings.is24HourFormat) "24-Hour" else "12-Hour AM/PM",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }

                        // List of 5 Main Prayers
                        val primaryPrayers = schedule?.prayers?.filter { it.type.isPrimaryPrayer } ?: emptyList()
                        items(primaryPrayers) { prayer ->
                            Box(
                                modifier = Modifier
                                    .fillMaxWidth()
                                    .padding(horizontal = 16.dp, vertical = 4.dp)
                            ) {
                                PrayerTimeCard(
                                    prayer = prayer,
                                    use24Hour = uiState.settings.is24HourFormat,
                                    onToggleReminder = {
                                        viewModel.togglePrayerNotification(prayer.type.name)
                                    },
                                    onLongClick = { showPrayerTimePicker(prayer) }
                                )
                            }
                        }

                        // Secondary Astronomical Times (Sunrise & Sunset) - Collapsed by default
                        val secondaryPrayers = schedule?.prayers?.filter { !it.type.isPrimaryPrayer } ?: emptyList()
                        if (secondaryPrayers.isNotEmpty()) {
                            item {
                                Spacer(modifier = Modifier.height(10.dp))
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(horizontal = 16.dp, vertical = 4.dp)
                                        .clip(RoundedCornerShape(10.dp))
                                        .background(MaterialTheme.colorScheme.surface)
                                        .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(10.dp))
                                        .clickable { isAstronomicalExpanded = !isAstronomicalExpanded }
                                        .padding(horizontal = 14.dp, vertical = 12.dp)
                                        .testTag("astronomical_dropdown_header"),
                                    horizontalArrangement = Arrangement.SpaceBetween,
                                    verticalAlignment = Alignment.CenterVertically
                                ) {
                                    Row(verticalAlignment = Alignment.CenterVertically) {
                                        Icon(
                                            imageVector = Icons.Default.WbSunny,
                                            contentDescription = null,
                                            tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                            modifier = Modifier.size(16.dp)
                                        )
                                        Spacer(modifier = Modifier.width(10.dp))
                                        Text(
                                            text = "ASTRONOMICAL TIMES (SUNRISE & SUNSET)",
                                            style = MaterialTheme.typography.labelSmall.copy(
                                                fontWeight = FontWeight.Bold,
                                                letterSpacing = 1.sp
                                            ),
                                            color = MaterialTheme.colorScheme.onBackground
                                        )
                                    }

                                    Icon(
                                        imageVector = if (isAstronomicalExpanded) Icons.Default.KeyboardArrowUp else Icons.Default.KeyboardArrowDown,
                                        contentDescription = if (isAstronomicalExpanded) "Collapse" else "Expand",
                                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                                        modifier = Modifier.size(20.dp)
                                    )
                                }
                            }

                            if (isAstronomicalExpanded) {
                                items(secondaryPrayers) { prayer ->
                                    Box(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(horizontal = 16.dp, vertical = 3.dp)
                                    ) {
                                        PrayerTimeCard(
                                            prayer = prayer,
                                            use24Hour = uiState.settings.is24HourFormat,
                                            onToggleReminder = {}
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // City Selection Bottom Sheet
    CitySelectionSheet(
        isOpen = uiState.isCityPickerOpen,
        selectedCity = uiState.settings.selectedCity,
        searchQuery = uiState.searchQuery,
        suggestedCities = uiState.suggestedCities,
        onDismiss = { viewModel.openCityPicker(false) },
        onSearchQueryChange = { viewModel.onSearchQueryChange(it) },
        onCitySelected = { viewModel.selectCity(it) }
    )

    // Settings Bottom Sheet
    SettingsSheet(
        isOpen = uiState.isSettingsOpen,
        settings = uiState.settings,
        cachedAtMillis = uiState.schedule?.cachedAtMillis ?: 0L,
        onDismiss = { viewModel.openSettings(false) },
        onSelectMethod = { viewModel.selectMethod(it) },
        onToggleNotifications = { viewModel.toggleNotifications(it) },
        onSelectOffset = { viewModel.setReminderOffset(it) },
        onToggleSound = { viewModel.toggleSound(it) },
        onToggleVibration = { viewModel.toggleVibration(it) },
        onToggle24Hour = { viewModel.toggle24HourFormat(it) },
        onSelectTheme = { viewModel.setThemeMode(it) },
        onSelectAzaan = { viewModel.selectAzaan(it) },
        onChooseAzaanFile = { audioPickerLauncher.launch(arrayOf("audio/*")) },
        onSendTestNotification = { viewModel.sendTestNotification() },
        onClearCache = { viewModel.clearCache() }
    )
}

@Composable
private fun DateHeader(
    city: String,
    dateGregorian: String,
    dateHijri: String,
    methodName: String,
    onOpenCityPicker: () -> Unit
) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp)
            .clip(RoundedCornerShape(12.dp))
            .background(MaterialTheme.colorScheme.surface)
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(12.dp))
            .clickable { onOpenCityPicker() }
            .padding(14.dp)
            .testTag("date_header_city_card")
    ) {
        Column {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.LocationOn,
                        contentDescription = "Change City",
                        tint = MaterialTheme.colorScheme.onBackground,
                        modifier = Modifier.size(16.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "${city.uppercase()}, INDIA",
                        style = MaterialTheme.typography.titleMedium.copy(
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 0.8.sp
                        ),
                        color = MaterialTheme.colorScheme.onBackground
                    )
                }

                if (dateHijri.isNotBlank()) {
                    Text(
                        text = dateHijri,
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Medium
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }

            Spacer(modifier = Modifier.height(4.dp))

            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Text(
                    text = dateGregorian,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Text(
                    text = methodName.split(",").firstOrNull() ?: methodName,
                    style = MaterialTheme.typography.bodySmall.copy(fontSize = 11.sp),
                    color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.7f)
                )
            }
        }
    }
}

private fun checkNotificationPermission(context: Context): Boolean =
    Build.VERSION.SDK_INT < Build.VERSION_CODES.TIRAMISU ||
        ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.POST_NOTIFICATIONS
        ) == PackageManager.PERMISSION_GRANTED

/**
 * Opens the system page where the user grants SCHEDULE_EXACT_ALARM
 * ("Alarms & reminders"). Falls back to the app details page on builds
 * where the dedicated settings action is unavailable.
 */
private fun openExactAlarmSettings(context: Context) {
    if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return
    val packageUri = Uri.parse("package:${context.packageName}")
    try {
        context.startActivity(
            Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, packageUri)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        )
    } catch (e: Exception) {
        try {
            context.startActivity(
                Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS, packageUri)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            )
        } catch (ignored: Exception) {
            // No settings page available on this device; nothing else to do.
        }
    }
}
