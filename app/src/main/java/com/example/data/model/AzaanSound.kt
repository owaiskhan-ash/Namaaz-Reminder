package com.example.data.model

/**
 * A prayer call (azaan) that can be used as the reminder sound.
 *
 * The files live in a public storage bucket and are downloaded to the device
 * on demand, so the app does not have to ship megabytes of audio.
 */
data class AzaanSound(
    val id: String,
    val displayName: String,
    val url: String,
    val isDownloaded: Boolean = false,
    val isDownloading: Boolean = false,
    val hasFailed: Boolean = false
) {
    /** Short label shown under the name. */
    val statusLabel: String
        get() = when {
            isDownloading -> "Downloading…"
            isDownloaded -> "Saved on device"
            hasFailed -> "Download failed"
            else -> "Tap to download"
        }
}

/**
 * The azaans the app can offer. The list is intentionally small and explicit:
 * every entry points at a file in the public asset bucket.
 */
object AzaanCatalogue {
    /** The azaan that is used until the user picks another one. */
    const val DEFAULT_AZAAN_ID = "madinah"

    const val BASE_URL =
        "https://oxtqzqynhtybrgushmjp.supabase.co/storage/v1/object/public/Just%20Apps/Namaaz%20reminder/"

    val sounds: List<AzaanSound> = listOf(
        AzaanSound(
            id = "madinah",
            displayName = "Madinah Azaan",
            url = BASE_URL + "Madinah%20Azaan.mp3"
        )
    )

    fun byId(id: String?): AzaanSound? = sounds.firstOrNull { it.id == id }
}
