package com.example.notification

import android.content.Context
import android.media.AudioAttributes
import android.media.AudioFocusRequest
import android.media.AudioManager
import android.media.MediaPlayer
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.os.VibrationAttributes
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager

/**
 * Plays the selected Azaan directly on Android's [AudioManager.STREAM_ALARM]
 * ([AudioAttributes.USAGE_ALARM]) so the Madinah Azaan remains audible even when
 * the phone's ringer switch is set to Silent or Vibrate mode.
 */
object AzaanAlarmPlayer {
    private const val MAX_PLAYBACK_MS = 5L * 60L * 1000L
    private val lock = Any()
    private val mainHandler = Handler(Looper.getMainLooper())

    private var mediaPlayer: MediaPlayer? = null
    private var wakeLock: PowerManager.WakeLock? = null
    private var audioFocusRequest: Any? = null
    private var restoredAlarmVolume: Int? = null
    private var activeGeneration: Long = 0L

    val isPlaying: Boolean
        get() = synchronized(lock) {
            runCatching { mediaPlayer?.isPlaying == true }.getOrDefault(false)
        }

    fun play(
        context: Context,
        soundUri: Uri?,
        vibrate: Boolean,
        onFinished: (() -> Unit)? = null
    ) {
        val appContext = context.applicationContext
        synchronized(lock) {
            stopLocked(appContext)
            val generation = ++activeGeneration

            if (vibrate) {
                triggerAlarmVibration(appContext)
            }
            if (soundUri == null) {
                onFinished?.let { mainHandler.post(it) }
                return
            }

            acquireWakeLock(appContext)
            val audioManager = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager
            val alarmAttrs = AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_ALARM)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build()

            ensureAudibleAlarmStream(audioManager)
            requestAlarmAudioFocus(audioManager, alarmAttrs)

            val started = startMediaPlayer(appContext, soundUri, alarmAttrs, generation, onFinished) ||
                fallbackAlarmUri(appContext, soundUri)?.let { fallback ->
                    startMediaPlayer(appContext, fallback, alarmAttrs, generation, onFinished)
                } == true

            if (!started) {
                stopLocked(appContext)
                onFinished?.let { mainHandler.post(it) }
            }
        }
    }

    fun stop(context: Context) {
        synchronized(lock) {
            activeGeneration++
            stopLocked(context.applicationContext)
        }
    }

    fun vibrateOnly(context: Context) {
        triggerAlarmVibration(context.applicationContext)
    }

    private fun startMediaPlayer(
        appContext: Context,
        uri: Uri,
        alarmAttrs: AudioAttributes,
        generation: Long,
        onFinished: (() -> Unit)?
    ): Boolean = runCatching {
        val player = MediaPlayer()
        player.setAudioAttributes(alarmAttrs)
        player.setDataSource(appContext, uri)
        player.isLooping = false
        player.setOnCompletionListener {
            val shouldNotify = synchronized(lock) {
                if (generation == activeGeneration) {
                    stopLocked(appContext)
                    true
                } else {
                    false
                }
            }
            if (shouldNotify) {
                onFinished?.let { mainHandler.post(it) }
            }
        }
        player.setOnErrorListener { _, _, _ ->
            val shouldNotify = synchronized(lock) {
                if (generation == activeGeneration) {
                    stopLocked(appContext)
                    true
                } else {
                    false
                }
            }
            if (shouldNotify) {
                onFinished?.let { mainHandler.post(it) }
            }
            true
        }
        player.prepare()
        player.start()
        mediaPlayer = player
        true
    }.getOrDefault(false)

    private fun fallbackAlarmUri(context: Context, failedUri: Uri): Uri? {
        val candidate = AzaanSoundStore.bundledMadinahUri(context)?.takeIf { it != failedUri }
            ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
            ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION)
        return candidate?.takeIf { it != failedUri }
    }

    private fun ensureAudibleAlarmStream(audioManager: AudioManager?) {
        if (audioManager == null) return
        runCatching {
            val current = audioManager.getStreamVolume(AudioManager.STREAM_ALARM)
            val max = audioManager.getStreamMaxVolume(AudioManager.STREAM_ALARM)
            if (current == 0 && max > 0) {
                val target = ((max * 0.65f).toInt()).coerceAtLeast(1)
                audioManager.setStreamVolume(AudioManager.STREAM_ALARM, target, 0)
                restoredAlarmVolume = 0
            }
        }
    }

    private fun requestAlarmAudioFocus(audioManager: AudioManager?, alarmAttrs: AudioAttributes) {
        if (audioManager == null) return
        runCatching {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                val req = AudioFocusRequest.Builder(AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK)
                    .setAudioAttributes(alarmAttrs)
                    .setAcceptsDelayedFocusGain(false)
                    .setOnAudioFocusChangeListener { }
                    .build()
                audioManager.requestAudioFocus(req)
                audioFocusRequest = req
            } else {
                @Suppress("DEPRECATION")
                audioManager.requestAudioFocus(
                    null,
                    AudioManager.STREAM_ALARM,
                    AudioManager.AUDIOFOCUS_GAIN_TRANSIENT_MAY_DUCK
                )
            }
        }
    }

    private fun acquireWakeLock(appContext: Context) {
        runCatching {
            val pm = appContext.getSystemService(Context.POWER_SERVICE) as? PowerManager ?: return
            val wl = pm.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "NamaazReminder:AzaanAlarm")
            wl.setReferenceCounted(false)
            wl.acquire(MAX_PLAYBACK_MS)
            wakeLock = wl
        }
    }

    private fun triggerAlarmVibration(appContext: Context) {
        runCatching {
            val pattern = longArrayOf(0, 450, 220, 450)
            val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                (appContext.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as? VibratorManager)
                    ?.defaultVibrator
            } else {
                @Suppress("DEPRECATION")
                appContext.getSystemService(Context.VIBRATOR_SERVICE) as? Vibrator
            }
            if (vibrator?.hasVibrator() != true) return

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                val attrs = VibrationAttributes.createForUsage(VibrationAttributes.USAGE_ALARM)
                vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1), attrs)
            } else if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                @Suppress("DEPRECATION")
                val attrs = AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build()
                @Suppress("DEPRECATION")
                vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1), attrs)
            } else {
                @Suppress("DEPRECATION")
                vibrator.vibrate(pattern, -1)
            }
        }
    }

    private fun stopLocked(appContext: Context) {
        mediaPlayer?.let { player ->
            runCatching {
                if (player.isPlaying) player.stop()
            }
            runCatching { player.reset() }
            runCatching { player.release() }
        }
        mediaPlayer = null

        val audioManager = appContext.getSystemService(Context.AUDIO_SERVICE) as? AudioManager
        restoredAlarmVolume?.let { previous ->
            runCatching {
                audioManager?.setStreamVolume(AudioManager.STREAM_ALARM, previous, 0)
            }
        }
        restoredAlarmVolume = null

        if (audioManager != null) {
            runCatching {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    (audioFocusRequest as? AudioFocusRequest)?.let {
                        audioManager.abandonAudioFocusRequest(it)
                    }
                } else {
                    @Suppress("DEPRECATION")
                    audioManager.abandonAudioFocus(null)
                }
            }
        }
        audioFocusRequest = null

        wakeLock?.let { wl ->
            runCatching {
                if (wl.isHeld) wl.release()
            }
        }
        wakeLock = null
    }
}
