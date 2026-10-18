package com.example.notification

import android.content.ContentResolver
import android.content.ContentValues
import android.content.Context
import android.media.MediaPlayer
import android.net.Uri
import android.os.Build
import android.provider.MediaStore
import com.example.data.local.PreferencesManager
import com.example.data.model.AzaanSound
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import java.io.File
import java.io.IOException

/**
 * Downloads the azaans and keeps them on the device.
 *
 * The audio is not shipped inside the APK: it is fetched from the public asset
 * bucket the first time the user picks it, and is then copied into the device's
 * media library so the system can play it as the notification sound.
 */
object AzaanManager {

    private const val FOLDER = "azaan"
    private const val MEDIA_RELATIVE_PATH = "Notifications/Namaaz Reminder"

    private val client = OkHttpClient()
    private var previewPlayer: MediaPlayer? = null

    /** The working copy of the azaan inside the app's private storage. */
    fun localFile(context: Context, azaan: AzaanSound): File =
        File(File(context.filesDir, FOLDER), "${azaan.id}.mp3")

    fun isDownloaded(context: Context, azaan: AzaanSound): Boolean {
        val file = localFile(context, azaan)
        return file.exists() && file.length() > 0L
    }

    /**
     * Downloads the azaan into the app's storage. The file is written to a
     * temporary file first so an interrupted download never leaves a broken
     * azaan behind.
     */
    suspend fun download(context: Context, azaan: AzaanSound): Result<File> = withContext(Dispatchers.IO) {
        val target = localFile(context, azaan)
        val temporary = File(target.parentFile, "${azaan.id}.part")
        try {
            target.parentFile?.mkdirs()
            val request = Request.Builder()
                .url(azaan.url)
                .header("User-Agent", "NamazTimesAndroidApp/1.0")
                .build()
            client.newCall(request).execute().use { response ->
                if (!response.isSuccessful) {
                    return@withContext Result.failure(IOException("HTTP ${response.code}"))
                }
                val body = response.body ?: return@withContext Result.failure(IOException("Empty response"))
                body.byteStream().use { input ->
                    temporary.outputStream().use { output -> input.copyTo(output) }
                }
            }
            if (temporary.length() <= 0L) {
                temporary.delete()
                return@withContext Result.failure(IOException("The azaan file was empty"))
            }
            if (target.exists()) target.delete()
            if (!temporary.renameTo(target)) {
                temporary.delete()
                return@withContext Result.failure(IOException("Could not store the azaan"))
            }
            Result.success(target)
        } catch (e: Exception) {
            temporary.delete()
            Result.failure(e)
        }
    }

    /**
     * Copies the azaan onto the device and remembers the uri the notification
     * should play. From Android 10 onwards the media store is used, so the file
     * shows up in the device's music library and the system is allowed to read
     * it when the reminder fires.
     */
    suspend fun install(context: Context, azaan: AzaanSound): Result<Uri> = withContext(Dispatchers.IO) {
        val file = localFile(context, azaan)
        if (!file.exists() || file.length() <= 0L) {
            return@withContext Result.failure(IOException("The azaan has not been downloaded yet"))
        }
        // Already saved on the device? Then keep the copy that is there, so the
        // music library does not fill up with duplicates.
        val existing = PreferencesManager(context).getAzaanUri(azaan.id)
        if (existing != null && isStillOnDevice(context, existing)) {
            return@withContext Result.success(Uri.parse(existing))
        }
        val uri = try {
            saveToDevice(context, azaan, file)
        } catch (e: Exception) {
            null
        } ?: return@withContext Result.failure(IOException("Could not save the azaan onto the device"))

        PreferencesManager(context).saveAzaanUri(azaan.id, uri.toString())
        Result.success(uri)
    }

    /**
     * The uri that should be handed to the notification, or null when the
     * azaan is not available on the device (yet).
     */
    fun notificationUri(context: Context, azaan: AzaanSound): Uri? {
        val stored = PreferencesManager(context).getAzaanUri(azaan.id) ?: return null
        if (!isDownloaded(context, azaan)) return null
        return runCatching { Uri.parse(stored) }.getOrNull()
    }

    /** Plays the azaan so the user can hear it before selecting it. */
    fun preview(context: Context, azaan: AzaanSound): Boolean {
        val file = localFile(context, azaan)
        if (!file.exists()) return false
        stopPreview()
        return try {
            val player = MediaPlayer()
            previewPlayer = player
            player.setDataSource(file.absolutePath)
            player.setOnPreparedListener { it.start() }
            player.setOnCompletionListener {
                it.release()
                if (previewPlayer === it) previewPlayer = null
            }
            player.prepareAsync()
            true
        } catch (e: Exception) {
            previewPlayer = null
            false
        }
    }

    fun stopPreview() {
        previewPlayer?.let { player ->
            runCatching {
                if (player.isPlaying) player.stop()
                player.release()
            }
        }
        previewPlayer = null
    }

    private fun saveToDevice(context: Context, azaan: AzaanSound, source: File): Uri? {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            return saveToMediaStore(context, azaan, source)
        }
        // Before Android 10 the app's external files directory is used and the
        // file is made world readable, so the system can play it.
        val directory = context.getExternalFilesDir(FOLDER) ?: context.filesDir
        directory.mkdirs()
        val target = File(directory, "${azaan.id}.mp3")
        source.inputStream().use { input ->
            target.outputStream().use { output -> input.copyTo(output) }
        }
        target.setReadable(true, false)
        return Uri.fromFile(target)
    }

    private fun saveToMediaStore(context: Context, azaan: AzaanSound, source: File): Uri? {
        val resolver = context.contentResolver
        val values = ContentValues().apply {
            put(MediaStore.Audio.Media.DISPLAY_NAME, "Namaaz Azaan - ${azaan.displayName}.mp3")
            put(MediaStore.Audio.Media.MIME_TYPE, "audio/mpeg")
            put(MediaStore.Audio.Media.RELATIVE_PATH, MEDIA_RELATIVE_PATH)
            put(MediaStore.Audio.Media.IS_PENDING, 1)
        }
        val collection = MediaStore.Audio.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)
        val uri = resolver.insert(collection, values) ?: return null
        try {
            resolver.openOutputStream(uri)?.use { output ->
                source.inputStream().use { input -> input.copyTo(output) }
            } ?: return null
        } catch (e: Exception) {
            runCatching { resolver.delete(uri, null, null) }
            return null
        }
        values.clear()
        values.put(MediaStore.Audio.Media.IS_PENDING, 0)
        resolver.update(uri, values, null, null)
        return uri
    }
}
