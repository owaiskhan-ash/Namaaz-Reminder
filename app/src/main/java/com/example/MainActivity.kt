package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.example.notification.PrayerNotificationManager
import com.example.ui.NamazScreen
import com.example.ui.NamazViewModel
import com.example.ui.theme.MyApplicationTheme

class MainActivity : ComponentActivity() {

    private val viewModel: NamazViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        // Initialize prayer reminder notification channel.
        // Runtime permissions (POST_NOTIFICATIONS on Android 13+, SCHEDULE_EXACT_ALARM
        // on Android 12+) are requested from NamazScreen, which keeps its banner state
        // in sync on every resume — requesting them here as well caused duplicate
        // prompts whose cancelled callbacks left the banner stale.
        PrayerNotificationManager.createNotificationChannel(this)

        setContent {
            val uiState by viewModel.uiState.collectAsStateWithLifecycle()
            val isDarkTheme = when (uiState.settings.themeMode) {
                "DARK" -> true
                "LIGHT" -> false
                else -> isSystemInDarkTheme()
            }

            MyApplicationTheme(darkTheme = isDarkTheme) {
                Surface(modifier = Modifier.fillMaxSize()) {
                    NamazScreen(viewModel = viewModel)
                }
            }
        }
    }
}
