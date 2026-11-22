package com.example.receiver

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import com.example.notification.AlarmRescheduler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

/**
 * Re-arms prayer alarms after a device reboot (AlarmManager alarms do not
 * survive reboots), after the clock/timezone changes (absolute RTC alarms
 * would otherwise fire at the wrong wall-clock time), and after an app
 * update (so a new build re-arms with its own logic immediately).
 *
 * Uses [goAsync] so the process is kept alive while the (potentially slow)
 * schedule fetch/reschedule runs; a bare coroutine scope returned from
 * onReceive could be killed by the system mid-flight, leaving the device
 * without any reminders after boot.
 */
class BootReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent?) {
        val action = intent?.action
        if (action != Intent.ACTION_BOOT_COMPLETED &&
            action != Intent.ACTION_TIME_SET &&
            action != Intent.ACTION_TIMEZONE_CHANGED &&
            action != Intent.ACTION_MY_PACKAGE_REPLACED
        ) return

        val appContext = context.applicationContext
        val pendingResult = goAsync()
        CoroutineScope(Dispatchers.IO).launch {
            try {
                AlarmRescheduler.rescheduleAlarms(appContext)
            } catch (e: Exception) {
                // Best effort: alarms are also rescheduled whenever the app is
                // opened and after every fired reminder.
            } finally {
                pendingResult.finish()
            }
        }
    }
}
