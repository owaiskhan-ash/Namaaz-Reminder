package com.example.notification

import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.database.Cursor
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import android.provider.OpenableColumns
import androidx.core.content.FileProvider
import com.example.data.local.PreferencesManager
import com.example.data.model.AzaanSoundIds
import com.example.data.model.UserSettings
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.InputStream
import java.util.Locale
import java.util.concurrent.TimeUnit

/**
 * Downloads and stores the default Azaan in the device's public Ringtones folder,
 * and imports user-selected audio there as well. This keeps notification sounds
 * available to Android's notification service after the app process is gone.
 */
object AzaanSoundStore {
    private const val MADINAH_AZAAN_URL =
        "https://oxtqzqynhtybrgushmjp.supabase.co/storage/v1/object/public/Just%20Apps/Namaaz%20reminder/Madinah%20Azaan.mp3"
    private const val SOUND_FOLDER = "Namaaz Reminder"
    private const val MAX_AUDIO_BYTES = 40L * 1024L * 1024L

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(45, TimeUnit.SECONDS)
        .followRedirects(true)
        .followSslRedirects(true)
        .build()

    data class ImportedAzaan(val name: String, val uri: Uri)

    fun soundName(settings: UserSettings): String = when (settings.azaanSoundId) {
        AzaanSoundIds.MADINAH -> "Madinah Azaan"
        AzaanSoundIds.CUSTOM -> settings.customAzaanName?.takeIf { it.isNotBlank() } ?: "Custom Azaan"
        else -> "Device default"
    }

    /**
     * Returns the APK-bundled Madinah Azaan URI (`res/raw/madinah_azaan`) when
     * present so reminders work immediately offline without waiting for a download.
     */
    fun bundledMadinahUri(context: Context): Uri? {
        val resId = context.resources.getIdentifier("madinah_azaan", "raw", context.packageName)
        return if (resId != 0) {
            Uri.parse("android.resource://${context.packageName}/$resId")
        } else {
            null
        }
    }

    fun selectedSoundUri(
        context: Context,
        settings: UserSettings,
        preferencesManager: PreferencesManager = PreferencesManager(context.applicationContext)
    ): Uri? {
        if (!settings.soundEnabled) return null
        val defaultUri = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)

        val selected = when (settings.azaanSoundId) {
            AzaanSoundIds.MADINAH -> bundledMadinahUri(context)
                ?: preferencesManager.getMadinahAzaanUri()
                    ?.let { value -> Uri.parse(value) }
                    ?.takeIf { canReadUri(context, it) }
                ?: defaultUri
            AzaanSoundIds.CUSTOM -> settings.customAzaanUri
                ?.let { value -> Uri.parse(value) }
                ?.takeIf { canReadUri(context, it) }
                ?: bundledMadinahUri(context)
                ?: defaultUri
            else -> defaultUri
        }
        grantLegacyFileRead(context, selected)
        return selected
    }

    /** Downloads the Madinah audio once if not already bundled in APK raw resources. */
    fun ensureMadinahAzaanDownloaded(
        context: Context,
        preferencesManager: PreferencesManager
    ): Uri {
        val appContext = context.applicationContext
        bundledMadinahUri(appContext)?.let { return it }

        preferencesManager.getMadinahAzaanUri()?.let { savedValue ->
            val savedUri = runCatching { Uri.parse(savedValue) }.getOrNull()
            if (savedUri != null && canReadUri(appContext, savedUri)) {
                grantLegacyFileRead(appContext, savedUri)
                return savedUri
            }
            preferencesManager.clearMadinahAzaanUri()
        }

        val request = Request.Builder()
            .url(MADINAH_AZAAN_URL)
            .header("User-Agent", "NamaazReminder/1.0")
            .build()

        httpClient.newCall(request).execute().use { response ->
            check(response.isSuccessful) { "Could not download the Madinah Azaan (${response.code})." }
            val body = response.body ?: error("The Madinah Azaan download was empty.")
            require(body.contentLength() <= MAX_AUDIO_BYTES || body.contentLength() == -1L) {
                "The Madinah Azaan file is too large to save."
            }
            val audioUri = saveAudioToDevice(
                context = appContext,
                input = body.byteStream(),
                displayName = "Madinah Azaan.mp3",
                mimeType = "audio/mpeg"
            )
            preferencesManager.saveMadinahAzaanUri(audioUri.toString())
            return audioUri
        }
    }

    /** Copies an audio document into local device storage for notification playback. */
    fun importAzaan(context: Context, sourceUri: Uri): ImportedAzaan {
        val appContext = context.applicationContext
        val resolver = appContext.contentResolver
        val displayName = queryDisplayName(resolver.query(sourceUri, null, null, null, null))
            ?: "Custom Azaan.mp3"
        val mimeType = resolver.getType(sourceUri)?.takeIf { it.startsWith("audio/") } ?: "audio/mpeg"
        val input = resolver.openInputStream(sourceUri) ?: error("Could not open the selected audio file.")
        val safeName = sanitizeAudioName(displayName)
        val savedUri = input.use {
            saveAudioToDevice(
                context = appContext,
                input = it,
                displayName = "Azaan - $safeName",
                mimeType = mimeType
            )
        }
        return ImportedAzaan(name = displayName.substringBeforeLast('.', displayName), uri = savedUri)
    }

    private fun queryDisplayName(cursor: Cursor?): String? = cursor?.use {
        val nameColumn = it.getColumnIndex(OpenableColumns.DISPLAY_NAME)
        if (nameColumn >= 0 && it.moveToFirst()) it.getString(nameColumn) else null
    }

    private fun sanitizeAudioName(name: String): String {
        val extension = name.substringAfterLast('.', "mp3")
            .lowercase(Locale.ROOT)
            .takeIf { it.matches(Regex("[a-z0-9]{1,8}")) }
            ?: "mp3"
        val baseName = name.substringBeforeLast('.', name)
            .replace(Regex("[^A-Za-z0-9 _-]"), "")
            .trim()
            .take(70)
            .ifBlank { "Custom Azaan" }
        return "$baseName.$extension"
    }

    private fun saveAudioToDevice(
        context: Context,
        input: InputStream,
        displayName: String,
        mimeType: String
    ): Uri {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            saveToMediaStore(context, input, displayName, mimeType)
        } else {
            saveToAppExternalFiles(context, input, displayName).also { uri ->
                grantLegacyFileRead(context, uri)
            }
        }
    }

    @androidx.annotation.RequiresApi(Build.VERSION_CODES.Q)
    private fun saveToMediaStore(
        context: Context,
        input: InputStream,
        displayName: String,
        mimeType: String
    ): Uri {
        val resolver = context.contentResolver
        val collection = MediaStore.Audio.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        val values = ContentValues().apply {
            put(MediaStore.MediaColumns.DISPLAY_NAME, displayName)
            put(MediaStore.MediaColumns.MIME_TYPE, mimeType)
            put(
                MediaStore.MediaColumns.RELATIVE_PATH,
                "${Environment.DIRECTORY_RINGTONES}/$SOUND_FOLDER"
            )
            put(MediaStore.Audio.Media.IS_RINGTONE, 1)
            put(MediaStore.Audio.Media.IS_NOTIFICATION, 1)
            put(MediaStore.Audio.Media.IS_ALARM, 1)
            put(MediaStore.Audio.Media.IS_MUSIC, 0)
            put(MediaStore.MediaColumns.IS_PENDING, 1)
        }

        val uri = resolver.insert(collection, values)
            ?: error("Could not create a local Azaan audio file.")
        try {
            val output = resolver.openOutputStream(uri, "w")
                ?: error("Could not save the Azaan audio file.")
            output.use { copyWithLimit(input, it) }
            resolver.update(
                uri,
                ContentValues().apply { put(MediaStore.MediaColumns.IS_PENDING, 0) },
                null,
                null
            )
            return uri
        } catch (error: Exception) {
            resolver.delete(uri, null, null)
            throw error
        }
    }

    private fun saveToAppExternalFiles(context: Context, input: InputStream, displayName: String): Uri {
        val parent = context.getExternalFilesDir(Environment.DIRECTORY_NOTIFICATIONS)
            ?: File(context.filesDir, "azaan")
        if (!parent.exists()) check(parent.mkdirs()) { "Could not create audio storage." }
        val target = File(parent, displayName)
        input.use { source -> target.outputStream().use { copyWithLimit(source, it) } }
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.azaanfiles", target)
        grantLegacyFileRead(context, uri)
        return uri
    }

    private fun copyWithLimit(input: InputStream, output: java.io.OutputStream) {
        val buffer = ByteArray(DEFAULT_BUFFER_SIZE)
        var totalBytes = 0L
        while (true) {
            val read = input.read(buffer)
            if (read < 0) break
            totalBytes += read
            check(totalBytes <= MAX_AUDIO_BYTES) { "The audio file is too large to save." }
            output.write(buffer, 0, read)
        }
        check(totalBytes > 0L) { "The audio file was empty." }
    }

    private fun canReadUri(context: Context, uri: Uri): Boolean = runCatching {
        context.contentResolver.openFileDescriptor(uri, "r")?.use { }
            ?: error("Audio file is unavailable")
    }.isSuccess

    /**
     * FileProvider is only used for Android 7-9, where we keep audio in app-specific
     * external files. Re-grant access when a channel is created (also after reboot).
     */
    private fun grantLegacyFileRead(context: Context, uri: Uri?) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q || uri?.scheme != "content") return
        listOf("android", "com.android.systemui").forEach { packageName ->
            runCatching {
                context.grantUriPermission(packageName, uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
            }
        }
    }
}
