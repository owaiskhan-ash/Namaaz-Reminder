package com.example.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.NotificationsOff
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.PrayerItem

@Composable
fun HeroCountdownCard(
    nextPrayer: PrayerItem?,
    countdownText: String,
    city: String,
    reminderOffsetMinutes: Int,
    use24Hour: Boolean,
    onToggleReminder: (String) -> Unit,
    onOpenCityPicker: (() -> Unit)? = null,
    modifier: Modifier = Modifier
) {
    // Warm layered card treatment shared with Vaccine Routine: quiet charcoal/paper
    // surfaces, soft borders and one restrained gold accent.
    val cardBackground = MaterialTheme.colorScheme.surface
    val cardTextColor = MaterialTheme.colorScheme.onSurface
    val subtleTextColor = MaterialTheme.colorScheme.onSurfaceVariant
    val pillBorderColor = MaterialTheme.colorScheme.outline

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .clip(RoundedCornerShape(20.dp))
            .background(cardBackground)
            .border(1.dp, MaterialTheme.colorScheme.outline, RoundedCornerShape(20.dp))
            .padding(22.dp)
            .testTag("hero_countdown_card")
    ) {
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            // Header: NEXT PRAYER Tag & City indicator
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Badge
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(6.dp))
                        .border(1.dp, pillBorderColor, RoundedCornerShape(6.dp))
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "NEXT PRAYER",
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.2.sp
                        ),
                        color = cardTextColor
                    )
                }

                // City indicator
                Text(
                    text = city.uppercase(),
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontWeight = FontWeight.Medium,
                        letterSpacing = 1.sp
                    ),
                    color = subtleTextColor,
                    modifier = Modifier.clickable(enabled = onOpenCityPicker != null) {
                        onOpenCityPicker?.invoke()
                    }
                )
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Prayer Name & Arabic
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.Bottom
            ) {
                Column {
                    Text(
                        text = nextPrayer?.type?.englishName?.uppercase() ?: "PRAYER",
                        style = MaterialTheme.typography.displayMedium.copy(
                            fontWeight = FontWeight.ExtraBold,
                            letterSpacing = 1.sp
                        ),
                        color = cardTextColor
                    )
                    Text(
                        text = "Starts at ${nextPrayer?.displayTime(use24Hour) ?: "--:--"}",
                        style = MaterialTheme.typography.bodyMedium.copy(
                            fontWeight = FontWeight.Medium
                        ),
                        color = subtleTextColor
                    )
                }

                Text(
                    text = nextPrayer?.type?.arabicName ?: "",
                    style = MaterialTheme.typography.headlineLarge.copy(
                        fontWeight = FontWeight.Normal
                    ),
                    color = subtleTextColor
                )
            }

            Spacer(modifier = Modifier.height(20.dp))

            // Live Countdown Display
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .clip(RoundedCornerShape(12.dp))
                    .background(cardTextColor.copy(alpha = 0.08f))
                    .border(1.dp, pillBorderColor, RoundedCornerShape(12.dp))
                    .padding(vertical = 14.dp, horizontal = 16.dp)
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Column {
                        Text(
                            text = "TIME REMAINING",
                            style = MaterialTheme.typography.labelSmall.copy(
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.sp,
                                fontSize = 10.sp
                            ),
                            color = subtleTextColor
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = countdownText,
                            style = MaterialTheme.typography.headlineMedium.copy(
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.5.sp
                            ),
                            color = cardTextColor,
                            modifier = Modifier.testTag("countdown_timer_text")
                        )
                    }

                    // Notification quick button
                    val isReminderActive = nextPrayer?.notificationEnabled == true
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(8.dp))
                            .border(1.dp, pillBorderColor, RoundedCornerShape(8.dp))
                            .clickable {
                                nextPrayer?.type?.name?.let { onToggleReminder(it) }
                            }
                            .padding(horizontal = 10.dp, vertical = 8.dp)
                            .testTag("hero_reminder_toggle"),
                        contentAlignment = Alignment.Center
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = if (isReminderActive) Icons.Default.Notifications else Icons.Default.NotificationsOff,
                                contentDescription = if (isReminderActive) "Reminder Active" else "Reminder Muted",
                                tint = cardTextColor,
                                modifier = Modifier.size(16.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = if (isReminderActive) {
                                    if (reminderOffsetMinutes == 0) "At Adhan" else "${reminderOffsetMinutes}m after"
                                } else {
                                    "Muted"
                                },
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.Medium
                                ),
                                color = cardTextColor
                            )
                        }
                    }
                }
            }
        }
    }
}
