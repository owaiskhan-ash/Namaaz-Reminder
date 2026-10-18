package com.example.ui.components

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TimePicker
import androidx.compose.material3.rememberTimePickerState
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

/**
 * Lets the user set a prayer time by hand. The dialog is opened by long
 * pressing a prayer card.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CustomPrayerTimeDialog(
    prayerName: String,
    calculatedTime: String,
    initialHour: Int,
    initialMinute: Int,
    hasCustomTime: Boolean,
    onDismiss: () -> Unit,
    onSave: (hour: Int, minute: Int) -> Unit,
    onReset: () -> Unit
) {
    val timePickerState = rememberTimePickerState(
        initialHour = initialHour.coerceIn(0, 23),
        initialMinute = initialMinute.coerceIn(0, 59),
        is24Hour = true
    )

    AlertDialog(
        onDismissRequest = onDismiss,
        title = {
            Text(
                text = "Set $prayerName time",
                style = MaterialTheme.typography.titleMedium.copy(fontWeight = FontWeight.Bold)
            )
        },
        text = {
            Column {
                Text(
                    text = "Calculated time: $calculatedTime",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                if (hasCustomTime) {
                    Text(
                        text = "A custom time is set for this prayer.",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                Spacer(modifier = Modifier.height(8.dp))
                TimePicker(state = timePickerState)
            }
        },
        confirmButton = {
            TextButton(
                onClick = { onSave(timePickerState.hour, timePickerState.minute) },
                modifier = Modifier.testTag("custom_time_save")
            ) {
                Text("SAVE", fontSize = 12.sp, fontWeight = FontWeight.Bold)
            }
        },
        dismissButton = {
            Row(verticalAlignment = Alignment.CenterVertically) {
                if (hasCustomTime) {
                    TextButton(
                        onClick = onReset,
                        modifier = Modifier.testTag("custom_time_reset")
                    ) {
                        Text("RESET", fontSize = 12.sp)
                    }
                }
                TextButton(onClick = onDismiss) {
                    Text("CANCEL", fontSize = 12.sp)
                }
            }
        }
    )
}
