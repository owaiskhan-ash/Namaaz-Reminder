package com.example.ui.components

import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.combinedClickable
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
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.PrayerItem

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PrayerTimeCard(
    prayer: PrayerItem,
    use24Hour: Boolean,
    onToggleReminder: () -> Unit,
    modifier: Modifier = Modifier,
    onLongClick: () -> Unit = {}
) {
    val isNext = prayer.isNext
    val isPassed = prayer.isPassed

    // Monochrome styling
    val cardBackground = if (isNext) {
        MaterialTheme.colorScheme.surfaceVariant
    } else {
        MaterialTheme.colorScheme.surface
    }

    val cardBorder = if (isNext) {
        MaterialTheme.colorScheme.onBackground
    } else {
        MaterialTheme.colorScheme.outline
    }

    val borderWidth = if (isNext) 1.5.dp else 1.dp

    val textAlpha = if (isPassed && !isNext) 0.45f else 1.0f

    Box(
        modifier = modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(14.dp))
            .background(cardBackground)
            .border(borderWidth, cardBorder, RoundedCornerShape(14.dp))
            .combinedClickable(
                onClick = {},
                onLongClick = onLongClick,
                onLongClickLabel = "Set a custom time for ${prayer.type.englishName}"
            )
            .padding(horizontal = 16.dp, vertical = 14.dp)
            .testTag("prayer_card_${prayer.type.name}"),
        contentAlignment = Alignment.Center
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            // Left: Status dot / pill & Name
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                // Indicator indicator
                Box(
                    modifier = Modifier
                        .size(8.dp)
                        .clip(RoundedCornerShape(4.dp))
                        .background(
                            when {
                                isNext -> MaterialTheme.colorScheme.onBackground
                                isPassed -> MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.3f)
                                else -> MaterialTheme.colorScheme.outline
                            }
                        )
                )

                Spacer(modifier = Modifier.width(12.dp))

                Column {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = prayer.type.englishName,
                            style = MaterialTheme.typography.titleMedium.copy(
                                fontWeight = if (isNext) FontWeight.Bold else FontWeight.Medium,
                                fontSize = 16.sp
                            ),
                            color = MaterialTheme.colorScheme.onBackground.copy(alpha = textAlpha)
                        )

                        if (isNext) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(MaterialTheme.colorScheme.onBackground)
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "NEXT",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold
                                    ),
                                    color = MaterialTheme.colorScheme.background
                                )
                            }
                        } else if (isPassed) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Text(
                                text = "Done",
                                style = MaterialTheme.typography.labelSmall.copy(
                                    fontSize = 10.sp,
                                    fontWeight = FontWeight.Normal
                                ),
                                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.6f)
                            )
                        }
                    }

                    Spacer(modifier = Modifier.height(2.dp))

                    Text(
                        text = prayer.type.arabicName,
                        style = MaterialTheme.typography.bodySmall.copy(
                            fontSize = 12.sp
                        ),
                        color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = textAlpha)
                    )
                }
            }

            // Right: Time and Notification Toggle Button
            Row(
                verticalAlignment = Alignment.CenterVertically
            ) {
                if (prayer.customTime != null) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            text = prayer.displayTime(use24Hour),
                            style = MaterialTheme.typography.titleLarge.copy(
                                fontWeight = if (isNext) FontWeight.Bold else FontWeight.SemiBold,
                                fontSize = 17.sp
                            ),
                            color = MaterialTheme.colorScheme.onBackground.copy(alpha = textAlpha)
                        )
                        Spacer(modifier = Modifier.width(7.dp))
                        Text(
                            text = prayer.defaultDisplayTime(use24Hour),
                            style = MaterialTheme.typography.bodySmall.copy(
                                fontWeight = FontWeight.Medium,
                                fontSize = 11.sp
                            ),
                            color = MaterialTheme.colorScheme.onSurfaceVariant.copy(
                                alpha = if (isPassed && !isNext) 0.4f else 0.72f
                            )
                        )
                    }
                } else {
                    Text(
                        text = prayer.displayTime(use24Hour),
                        style = MaterialTheme.typography.titleLarge.copy(
                            fontWeight = if (isNext) FontWeight.Bold else FontWeight.SemiBold,
                            fontSize = 17.sp
                        ),
                        color = MaterialTheme.colorScheme.onBackground.copy(alpha = textAlpha)
                    )
                }

                if (prayer.type.isPrimaryPrayer) {
                    Spacer(modifier = Modifier.width(10.dp))

                    IconButton(
                        onClick = onToggleReminder,
                        modifier = Modifier
                            .size(36.dp)
                            .clip(RoundedCornerShape(8.dp))
                            .background(
                                if (prayer.notificationEnabled) {
                                    MaterialTheme.colorScheme.onBackground.copy(alpha = 0.08f)
                                } else {
                                    MaterialTheme.colorScheme.surface
                                }
                            )
                            .testTag("toggle_reminder_${prayer.type.name}")
                    ) {
                        Icon(
                            imageVector = if (prayer.notificationEnabled) Icons.Default.Notifications else Icons.Default.NotificationsOff,
                            contentDescription = if (prayer.notificationEnabled) "Mute reminder for ${prayer.type.englishName}" else "Enable reminder for ${prayer.type.englishName}",
                            tint = if (prayer.notificationEnabled) {
                                MaterialTheme.colorScheme.onBackground
                            } else {
                                MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.4f)
                            },
                            modifier = Modifier.size(18.dp)
                        )
                    }
                }
            }
        }
    }
}
