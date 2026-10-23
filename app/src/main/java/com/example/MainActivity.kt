package com.example

import android.content.Intent
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.SideEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.core.view.WindowCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.data.local.PreferencesManager
import com.example.notification.PrayerNotificationManager
import com.example.ui.NamazScreen
import com.example.ui.NamazViewModel
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {

    private val viewModel: NamazViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        handleAlarmIntent(intent)

        // Runtime permissions (POST_NOTIFICATIONS on Android 13+, SCHEDULE_EXACT_ALARM
        // on Android 12+) are requested from NamazScreen to avoid duplicate prompts.
        PrayerNotificationManager.createNotificationChannel(
            this,
            PreferencesManager(applicationContext).loadSettings()
        )

        setContent {
            val uiState by viewModel.uiState.collectAsStateWithLifecycle()
            val isDarkTheme = when (uiState.settings.themeMode) {
                "DARK" -> true
                "LIGHT" -> false
                else -> isSystemInDarkTheme()
            }

            SideEffect {
                // enableEdgeToEdge() already keeps the system bars transparent
                // (setting the bar colours is a no-op from API 35), so only the
                // icon contrast has to follow the selected theme.
                WindowCompat.getInsetsController(window, window.decorView).apply {
                    isAppearanceLightStatusBars = !isDarkTheme
                    isAppearanceLightNavigationBars = !isDarkTheme
                }
            }

            MyApplicationTheme(darkTheme = isDarkTheme) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    NamazScreen(viewModel = viewModel)
                }
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleAlarmIntent(intent)
    }

    private fun handleAlarmIntent(incoming: Intent?) {
        if (incoming?.getBooleanExtra(PrayerNotificationManager.EXTRA_STOP_AZAAN_ON_OPEN, false) == true) {
            PrayerNotificationManager.stopAzaan(applicationContext)
            incoming.removeExtra(PrayerNotificationManager.EXTRA_STOP_AZAAN_ON_OPEN)
        }
    }
}
