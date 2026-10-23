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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.PrayerItem
import com.example.ui.theme.LeatherCreamInk
import com.example.ui.theme.LeatherCreamPill
import com.example.ui.theme.LeatherCyan
import com.example.ui.theme.WarmAccent

@Composable
fun HeroCountdownCard(
    nextPrayer: PrayerItem?,
    countdownText: String,
    city: String,
    reminderOffsetMinutes: Int,
    use24Hour: Boolean,
    onToggleReminder: (String) -> Unit,
    onOpenCityPicker: (() -> Unit)? = null,
    isDark: Boolean = true,
    grainBrush: Brush? = null,
    modifier: Modifier = Modifier
) {
    val cardBackground = MaterialTheme.colorScheme.surface
    val cardTextColor = MaterialTheme.colorScheme.onSurface
    val subtleTextColor = MaterialTheme.colorScheme.onSurfaceVariant
    val pillBorderColor = MaterialTheme.colorScheme.outline
    val outerBorder = if (isDark) {
        LeatherCyan.copy(alpha = 0.28f)
    } else {
        MaterialTheme.colorScheme.outline
    }
    val stitchColor = if (isDark) {
        WarmAccent.copy(alpha = 0.14f)
    } else {
        MaterialTheme.colorScheme.outline.copy(alpha = 0.45f)
    }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .leatherCard(
                cornerRadius = 20.dp,
                isDark = isDark,
                fillColor = cardBackground,
                borderColor = outerBorder,
                grainBrush = grainBrush,
                stitchColor = stitchColor
            )
            .padding(22.dp)
            .testTag("hero_countdown_card")
    ) {
        Column(
            modifier = Modifier.fillMaxWidth()
        ) {
            // Header: NEXT PRAYER suede pill & City indicator
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(50))
                        .background(if (isDark) LeatherCreamPill else MaterialTheme.colorScheme.onSurface)
                        .padding(horizontal = 11.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = "NEXT PRAYER",
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Bold,
                            letterSpacing = 1.2.sp,
                            fontSize = 10.sp
                        ),
                        color = if (isDark) LeatherCreamInk else MaterialTheme.colorScheme.surface
                    )
                }

                Box(
                    modifier = Modifier
                        .clip(RoundedCornerShape(50))
                        .border(1.dp, pillBorderColor, RoundedCornerShape(50))
                        .clickable(enabled = onOpenCityPicker != null) {
                            onOpenCityPicker?.invoke()
                        }
                        .padding(horizontal = 10.dp, vertical = 4.dp)
                ) {
                    Text(
                        text = city.uppercase(),
                        style = MaterialTheme.typography.labelSmall.copy(
                            fontWeight = FontWeight.Medium,
                            letterSpacing = 1.sp,
                            fontSize = 10.sp
                        ),
                        color = subtleTextColor
                    )
                }
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

            Spacer(modifier = Modifier.height(18.dp))

            // Recessed Leather Countdown Well
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .leatherWell(
                        cornerRadius = 13.dp,
                        isDark = isDark,
                        borderColor = pillBorderColor
                    )
                    .padding(vertical = 13.dp, horizontal = 15.dp)
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
                                letterSpacing = 1.1.sp,
                                fontSize = 9.5.sp
                            ),
                            color = subtleTextColor
                        )
                        Spacer(modifier = Modifier.height(2.dp))
                        Text(
                            text = countdownText,
                            style = MaterialTheme.typography.headlineMedium.copy(
                                fontFamily = FontFamily.Monospace,
                                fontWeight = FontWeight.Bold,
                                letterSpacing = 1.4.sp
                            ),
                            color = cardTextColor,
                            modifier = Modifier.testTag("countdown_timer_text")
                        )
                    }

                    // Subtle Reminder Quick Chip
                    val isReminderActive = nextPrayer?.notificationEnabled == true
                    val chipBg = if (isReminderActive && isDark) {
                        LeatherCreamPill.copy(alpha = 0.12f)
                    } else {
                        MaterialTheme.colorScheme.surface
                    }
                    val chipBorder = if (isReminderActive && isDark) {
                        WarmAccent.copy(alpha = 0.36f)
                    } else {
                        pillBorderColor
                    }
                    Box(
                        modifier = Modifier
                            .clip(RoundedCornerShape(50))
                            .background(chipBg)
                            .border(1.dp, chipBorder, RoundedCornerShape(50))
                            .clickable {
                                nextPrayer?.type?.name?.let { onToggleReminder(it) }
                            }
                            .padding(horizontal = 12.dp, vertical = 7.dp)
                            .testTag("hero_reminder_toggle"),
                        contentAlignment = Alignment.Center
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = if (isReminderActive) Icons.Default.Notifications else Icons.Default.NotificationsOff,
                                contentDescription = if (isReminderActive) "Reminder Active" else "Reminder Muted",
                                tint = if (isReminderActive && isDark) WarmAccent else subtleTextColor,
                                modifier = Modifier.size(15.dp)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(
                                text = if (isReminderActive) {
                                    if (reminderOffsetMinutes == 0) "At Adhan" else "${reminderOffsetMinutes}m after"
                                } else {
                                    "Muted"
                                },
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontWeight = FontWeight.SemiBold
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
