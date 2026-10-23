package com.example.ui.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.DarkMode
import androidx.compose.material.icons.outlined.LightMode
import androidx.compose.material.icons.outlined.LocationOn
import androidx.compose.material.icons.outlined.Settings
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.R
import com.example.ui.theme.LeatherCognac

@Composable
fun NamazTopBar(
    isLoading: Boolean,
    currentCity: String,
    currentTheme: String,
    onToggleTheme: () -> Unit,
    onOpenCityPicker: () -> Unit,
    onOpenSettings: () -> Unit,
    modifier: Modifier = Modifier
) {
    val isDark = currentTheme == "DARK"
    val wellBorder = MaterialTheme.colorScheme.outline

    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        // Transparent-base stitched leather & suede NR squircle badge
        Image(
            painter = painterResource(id = R.drawable.ic_app_icon),
            contentDescription = "Namaaz Reminder logo",
            modifier = Modifier.size(34.dp)
        )

        Spacer(modifier = Modifier.width(11.dp))

        Column(
            modifier = Modifier
                .weight(1f)
                .clickable { onOpenCityPicker() }
        ) {
            Text(
                text = "NAMAAZ REMINDER",
                maxLines = 1,
                overflow = TextOverflow.Ellipsis,
                style = MaterialTheme.typography.titleMedium.copy(
                    fontSize = 14.sp,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.1.sp
                ),
                color = MaterialTheme.colorScheme.onBackground
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Box(
                    modifier = Modifier
                        .size(4.5.dp)
                        .clip(CircleShape)
                        .background(LeatherCognac.copy(alpha = 0.85f))
                )
                Spacer(modifier = Modifier.width(5.dp))
                Text(
                    text = "${currentCity.uppercase()}, INDIA",
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    style = MaterialTheme.typography.labelSmall.copy(
                        fontSize = 10.5.sp,
                        fontWeight = FontWeight.SemiBold,
                        letterSpacing = 0.55.sp
                    ),
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }

        Spacer(modifier = Modifier.width(12.dp))

        // Compact, evenly spaced header action buttons (32dp wells, 15dp icons, 10dp spacing)
        Row(
            horizontalArrangement = Arrangement.spacedBy(10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .leatherWell(cornerRadius = 9.dp, isDark = isDark, borderColor = wellBorder)
                    .clickable(role = Role.Button, onClick = onOpenCityPicker)
                    .testTag("location_button"),
                contentAlignment = Alignment.Center
            ) {
                if (isLoading) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(14.dp),
                        strokeWidth = 1.7.dp,
                        color = MaterialTheme.colorScheme.onBackground
                    )
                } else {
                    Icon(
                        imageVector = Icons.Outlined.LocationOn,
                        contentDescription = "Select City",
                        tint = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier.size(15.dp)
                    )
                }
            }

            HeaderIconButton(
                icon = if (isDark) Icons.Outlined.LightMode else Icons.Outlined.DarkMode,
                contentDescription = if (isDark) "Switch to light mode" else "Switch to dark mode",
                isDark = isDark,
                borderColor = wellBorder,
                testTag = "theme_toggle_button",
                onClick = onToggleTheme
            )

            HeaderIconButton(
                icon = Icons.Outlined.Settings,
                contentDescription = "Open Settings",
                isDark = isDark,
                borderColor = wellBorder,
                testTag = "settings_button",
                onClick = onOpenSettings
            )
        }
    }
}

@Composable
private fun HeaderIconButton(
    icon: ImageVector,
    contentDescription: String,
    isDark: Boolean,
    borderColor: Color,
    testTag: String,
    onClick: () -> Unit
) {
    Box(
        modifier = Modifier
            .size(32.dp)
            .leatherWell(cornerRadius = 9.dp, isDark = isDark, borderColor = borderColor)
            .clickable(role = Role.Button, onClick = onClick)
            .testTag(testTag),
        contentAlignment = Alignment.Center
    ) {
        Icon(
            imageVector = icon,
            contentDescription = contentDescription,
            tint = MaterialTheme.colorScheme.onSurfaceVariant,
            modifier = Modifier.size(15.dp)
        )
    }
}
