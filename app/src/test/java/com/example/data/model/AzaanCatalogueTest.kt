package com.example.data.model

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Tests for the azaans the app can play.
 */
class AzaanCatalogueTest {

    @Test
    fun `the madinah azaan is used until another one is picked`() {
        assertEquals("madinah", AzaanCatalogue.DEFAULT_AZAAN_ID)
        assertNotNull(AzaanCatalogue.byId(AzaanCatalogue.DEFAULT_AZAAN_ID))
    }

    @Test
    fun `every azaan has its own id and a downloadable url`() {
        val sounds = AzaanCatalogue.sounds

        assertTrue(sounds.isNotEmpty())
        assertEquals(sounds.size, sounds.map { it.id }.distinct().size)
        sounds.forEach { sound ->
            assertTrue(sound.id.isNotBlank())
            assertTrue(sound.displayName.isNotBlank())
            assertTrue(sound.url.startsWith("https://"))
            assertTrue(sound.url.endsWith(".mp3"))
        }
    }

    @Test
    fun `an unknown azaan is not found`() {
        assertEquals(null, AzaanCatalogue.byId("does-not-exist"))
        assertEquals(null, AzaanCatalogue.byId(null))
    }

    @Test
    fun `the status label tells the user what happens next`() {
        assertEquals("Tap to download", AzaanSound("a", "A", "url").statusLabel)
        assertEquals(
            "Saved on device",
            AzaanSound("a", "A", "url", isDownloaded = true).statusLabel
        )
        assertEquals(
            "Downloading…",
            AzaanSound("a", "A", "url", isDownloading = true).statusLabel
        )
        assertEquals(
            "Download failed",
            AzaanSound("a", "A", "url", hasFailed = true).statusLabel
        )
    }
}
