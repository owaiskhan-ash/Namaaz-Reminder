package com.example.ui.components

import android.graphics.BitmapFactory
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.drawBehind
import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.ImageShader
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.ShaderBrush
import androidx.compose.ui.graphics.TileMode
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.example.R
import com.example.ui.theme.DarkBackground
import com.example.ui.theme.DarkWell
import com.example.ui.theme.LightBackground
import com.example.ui.theme.LightWell

/**
 * Memoized seamless matte black calfskin grain brush. Returns null in light mode
 * or if resources are unavailable in headless unit tests.
 */
@Composable
fun rememberBlackLeatherBrush(isDark: Boolean): Brush? {
    if (!isDark) return null
    val context = LocalContext.current
    return remember(context, isDark) {
        runCatching {
            val bmp = BitmapFactory.decodeResource(context.resources, R.drawable.leather_black_tile)
                ?: return@runCatching null
            ShaderBrush(ImageShader(bmp.asImageBitmap(), TileMode.Repeated, TileMode.Repeated))
        }.getOrNull()
    }
}

/**
 * Full-screen matte black calfskin canvas with a soft overhead studio vignette
 * and whisper-subtle blind-stitched side seams (kept very quiet so content leads).
 */
fun Modifier.blackLeatherCanvas(
    isDark: Boolean,
    grainBrush: Brush?
): Modifier = this.drawBehind {
    val base = if (isDark) DarkBackground else LightBackground
    drawRect(color = base)
    if (isDark && grainBrush != null) {
        drawRect(brush = grainBrush, alpha = 0.88f)
        drawRect(
            brush = Brush.verticalGradient(
                0.0f to Color.White.copy(alpha = 0.022f),
                0.35f to Color.Transparent,
                1.0f to Color.Black.copy(alpha = 0.36f)
            )
        )
        // Whisper-quiet vertical saddle stitch along the outer hide margin
        val seamInset = 6.dp.toPx()
        val stitchEffect = PathEffect.dashPathEffect(
            floatArrayOf(5.dp.toPx(), 4.5.dp.toPx()),
            0f
        )
        val seamColor = Color(0xFFD8C2A0).copy(alpha = 0.075f)
        drawLine(
            color = seamColor,
            start = Offset(seamInset, 0f),
            end = Offset(seamInset, size.height),
            strokeWidth = 1.dp.toPx(),
            pathEffect = stitchEffect
        )
        drawLine(
            color = seamColor,
            start = Offset(size.width - seamInset, 0f),
            end = Offset(size.width - seamInset, size.height),
            strokeWidth = 1.dp.toPx(),
            pathEffect = stitchEffect
        )
    }
}

/**
 * Subtle padded black-leather card surface: gentle studio top catchlight,
 * optional matte hide grain, hairline edge border, and optional understated
 * inset saddle stitching.
 */
fun Modifier.leatherCard(
    cornerRadius: Dp = 14.dp,
    isDark: Boolean,
    fillColor: Color,
    borderColor: Color,
    borderWidth: Dp = 1.dp,
    grainBrush: Brush? = null,
    stitchColor: Color? = null
): Modifier = this
    .clip(RoundedCornerShape(cornerRadius))
    .drawBehind {
        val r = cornerRadius.toPx()
        val cr = CornerRadius(r, r)

        drawRoundRect(color = fillColor, cornerRadius = cr)

        if (isDark) {
            if (grainBrush != null) {
                drawRoundRect(brush = grainBrush, cornerRadius = cr, alpha = 0.34f)
            }
            drawRoundRect(
                brush = Brush.verticalGradient(
                    0.0f to Color.White.copy(alpha = 0.036f),
                    0.45f to Color.Transparent,
                    1.0f to Color.Black.copy(alpha = 0.24f)
                ),
                cornerRadius = cr
            )
        }

        // Outer hide edge
        val bw = borderWidth.toPx()
        drawRoundRect(
            color = borderColor,
            topLeft = Offset(bw / 2f, bw / 2f),
            size = Size((size.width - bw).coerceAtLeast(0f), (size.height - bw).coerceAtLeast(0f)),
            cornerRadius = CornerRadius((r - bw / 2f).coerceAtLeast(0f)),
            style = Stroke(width = bw)
        )

        // Subtle top rim highlight on dark leather
        if (isDark) {
            val inset = 1.1.dp.toPx()
            drawRoundRect(
                brush = Brush.verticalGradient(
                    0.0f to Color.White.copy(alpha = 0.075f),
                    0.22f to Color.Transparent
                ),
                topLeft = Offset(inset, inset),
                size = Size((size.width - inset * 2).coerceAtLeast(0f), (size.height - inset * 2).coerceAtLeast(0f)),
                cornerRadius = CornerRadius((r - inset).coerceAtLeast(0f)),
                style = Stroke(width = 0.8.dp.toPx())
            )
        }

        // Optional understated inset saddle stitch
        if (stitchColor != null) {
            val stitchInset = 4.5.dp.toPx()
            val dash = PathEffect.dashPathEffect(
                floatArrayOf(4.5.dp.toPx(), 3.8.dp.toPx()),
                0f
            )
            drawRoundRect(
                color = stitchColor,
                topLeft = Offset(stitchInset, stitchInset),
                size = Size(
                    (size.width - stitchInset * 2).coerceAtLeast(0f),
                    (size.height - stitchInset * 2).coerceAtLeast(0f)
                ),
                cornerRadius = CornerRadius((r - stitchInset).coerceAtLeast(0f)),
                style = Stroke(width = 0.9.dp.toPx(), pathEffect = dash)
            )
        }
    }

/**
 * Recessed leather pocket for icon wells and the live countdown display.
 */
fun Modifier.leatherWell(
    cornerRadius: Dp = 12.dp,
    isDark: Boolean,
    borderColor: Color
): Modifier = this
    .clip(RoundedCornerShape(cornerRadius))
    .drawBehind {
        val r = cornerRadius.toPx()
        val cr = CornerRadius(r, r)
        val wellColor = if (isDark) DarkWell else LightWell
        drawRoundRect(color = wellColor, cornerRadius = cr)
        if (isDark) {
            drawRoundRect(
                brush = Brush.verticalGradient(
                    0.0f to Color.Black.copy(alpha = 0.45f),
                    0.35f to Color.Transparent,
                    1.0f to Color.White.copy(alpha = 0.03f)
                ),
                cornerRadius = cr
            )
        }
        val bw = 1.dp.toPx()
        drawRoundRect(
            color = borderColor,
            topLeft = Offset(bw / 2f, bw / 2f),
            size = Size((size.width - bw).coerceAtLeast(0f), (size.height - bw).coerceAtLeast(0f)),
            cornerRadius = CornerRadius((r - bw / 2f).coerceAtLeast(0f)),
            style = Stroke(width = bw)
        )
    }
