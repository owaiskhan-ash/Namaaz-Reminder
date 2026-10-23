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
import androidx.compose.foundation.shape.CircleShape
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
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.data.model.PrayerItem
import com.example.ui.theme.DarkNextCard
import com.example.ui.theme.LeatherCognac
import com.example.ui.theme.LeatherCyan
import com.example.ui.theme.LeatherCyanSoft
import com.example.ui.theme.LeatherLime
import com.example.ui.theme.LightNextCard
import com.example.ui.theme.WarmAccent

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun PrayerTimeCard(
    prayer: PrayerItem,
    use24Hour: Boolean,
    onToggleReminder: () -> Unit,
    modifier: Modifier = Modifier,
    isDark: Boolean = true,
    grainBrush: Brush? = null,
    onLongClick: () -> Unit = {}
) {
    val isNext = prayer.isNext
    val isPassed = prayer.isPassed

    val cardBackground = when {
        isNext && isDark -> DarkNextCard
        isNext -> LightNextCard
        else -> MaterialTheme.colorScheme.surface
    }

    val cardBorder = when {
        isNext && isDark -> LeatherCyan.copy(alpha = 0.46f)
        isNext -> LeatherCyan.copy(alpha = 0.65f)
        else -> MaterialTheme.colorScheme.outline
    }

    val stitchColor = if (isNext) {
        LeatherCyan.copy(alpha = if (isDark) 0.16f else 0.22f)
    } else {
        null
    }

    val borderWidth = if (isNext) 1.2.dp else 1.dp
    val textAlpha = if (isPassed && !isNext) 0.48f else 1.0f

    val dotColor = when {
        isNext && isDark -> LeatherLime
        isNext -> LeatherCyan
        isPassed -> WarmAccent.copy(alpha = 0.32f)
        else -> LeatherCognac.copy(alpha = 0.58f)
    }

    Box(
        modifier = modifier
            .fillMaxWidth()
            .leatherCard(
                cornerRadius = 14.dp,
                isDark = isDark,
                fillColor = cardBackground,
                borderColor = cardBorder,
                borderWidth = borderWidth,
                grainBrush = grainBrush,
                stitchColor = stitchColor
            )
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
            // Left: Status dot & Prayer Name
            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.weight(1f)
            ) {
                Box(
                    modifier = Modifier
                        .size(7.dp)
                        .clip(CircleShape)
                        .background(dotColor)
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
                                    .background(LeatherCyan.copy(alpha = if (isDark) 0.18f else 0.14f))
                                    .border(
                                        0.8.dp,
                                        LeatherCyan.copy(alpha = 0.42f),
                                        RoundedCornerShape(4.dp)
                                    )
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "NEXT",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold,
                                        letterSpacing = 0.8.sp
                                    ),
                                    color = if (isDark) LeatherCyanSoft else LeatherCyan
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
                                color = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.58f)
                            )
                        }

                        if (prayer.customTime != null) {
                            Spacer(modifier = Modifier.width(8.dp))
                            Box(
                                modifier = Modifier
                                    .clip(RoundedCornerShape(4.dp))
                                    .background(MaterialTheme.colorScheme.surfaceVariant)
                                    .border(
                                        1.dp,
                                        MaterialTheme.colorScheme.outline,
                                        RoundedCornerShape(4.dp)
                                    )
                                    .padding(horizontal = 6.dp, vertical = 2.dp)
                            ) {
                                Text(
                                    text = "CUSTOM",
                                    style = MaterialTheme.typography.labelSmall.copy(
                                        fontSize = 9.sp,
                                        fontWeight = FontWeight.Bold
                                    ),
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
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

            // Right: Time and Recessed Leather Notification Toggle
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

                    val bellBorder = when {
                        prayer.notificationEnabled && isNext -> LeatherCyan.copy(alpha = 0.42f)
                        prayer.notificationEnabled && isDark -> WarmAccent.copy(alpha = 0.22f)
                        else -> MaterialTheme.colorScheme.outline
                    }
                    val bellTint = when {
                        !prayer.notificationEnabled -> MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.36f)
                        isNext && isDark -> LeatherCyanSoft
                        isDark -> WarmAccent
                        else -> MaterialTheme.colorScheme.onBackground
                    }

                    IconButton(
                        onClick = onToggleReminder,
                        modifier = Modifier
                            .size(36.dp)
                            .leatherWell(
                                cornerRadius = 9.dp,
                                isDark = isDark,
                                borderColor = bellBorder
                            )
                            .testTag("toggle_reminder_${prayer.type.name}")
                    ) {
                        Icon(
                            imageVector = if (prayer.notificationEnabled) Icons.Default.Notifications else Icons.Default.NotificationsOff,
                            contentDescription = if (prayer.notificationEnabled) "Mute reminder for ${prayer.type.englishName}" else "Enable reminder for ${prayer.type.englishName}",
                            tint = bellTint,
                            modifier = Modifier.size(17.dp)
                        )
                    }
                }
            }
        }
    }
}
