package com.example.ui.theme

import org.junit.Assert.assertEquals
import org.junit.Test

/**
 * Tests for the light / dark switch in the header.
 */
class ThemeLogicTest {

    @Test
    fun `a fixed theme is used as it is`() {
        assertEquals(true, isDarkThemeActive("DARK", systemInDarkTheme = false))
        assertEquals(false, isDarkThemeActive("LIGHT", systemInDarkTheme = true))
    }

    @Test
    fun `the system theme follows the phone`() {
        assertEquals(true, isDarkThemeActive("SYSTEM", systemInDarkTheme = true))
        assertEquals(false, isDarkThemeActive("SYSTEM", systemInDarkTheme = false))
    }

    @Test
    fun `the switch toggles between light and dark`() {
        assertEquals("LIGHT", nextThemeMode(isDarkTheme = true))
        assertEquals("DARK", nextThemeMode(isDarkTheme = false))
    }

    @Test
    fun `the switch moves the app out of the system theme`() {
        // Whatever the phone is set to, the switch picks the other theme.
        val onDarkPhone = isDarkThemeActive("SYSTEM", systemInDarkTheme = true)
        val onLightPhone = isDarkThemeActive("SYSTEM", systemInDarkTheme = false)

        assertEquals("LIGHT", nextThemeMode(onDarkPhone))
        assertEquals("DARK", nextThemeMode(onLightPhone))
    }
}
