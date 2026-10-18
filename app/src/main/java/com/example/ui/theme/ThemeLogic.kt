package com.example.ui.theme

/**
 * The theme that is really on screen.
 *
 * "SYSTEM" follows the setting of the phone, "LIGHT" and "DARK" are the two
 * fixed themes. The header switch uses this value, so it always shows the
 * theme the user would get by tapping it.
 */
fun isDarkThemeActive(themeMode: String, systemInDarkTheme: Boolean): Boolean =
    when (themeMode) {
        "DARK" -> true
        "LIGHT" -> false
        else -> systemInDarkTheme
    }

/**
 * The theme the header switch switches to: the opposite of the theme that is
 * on screen. "SYSTEM" stays available in the settings.
 */
fun nextThemeMode(isDarkTheme: Boolean): String = if (isDarkTheme) "LIGHT" else "DARK"
