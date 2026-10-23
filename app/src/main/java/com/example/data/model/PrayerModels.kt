package com.example.data.model

enum class PrayerType(
    val englishName: String,
    val arabicName: String,
    val isPrimaryPrayer: Boolean
) {
    FAJR("Fajr", "الفجر", true),
    SUNRISE("Sunrise", "الشروق", false),
    DHUHR("Dhuhr", "الظهر", true),
    ASR("Asr", "العصر", true),
    SUNSET("Sunset", "الغروب", false),
    MAGHRIB("Maghrib", "المغرب", true),
    ISHA("Isha", "العشاء", true)
}

data class PrayerItem(
    val type: PrayerType,
    val rawTime: String, // Default time, e.g. "05:05"
    val formattedTime12: String, // Default time, e.g. "5:05 AM"
    val formattedTime24: String, // Default time, e.g. "05:05"
    val targetEpochMillis: Long,
    val isNext: Boolean = false,
    val isPassed: Boolean = false,
    val notificationEnabled: Boolean = true,
    /** Optional today-only override in HH:mm format. */
    val customTime: String? = null
) {
    fun defaultDisplayTime(use24Hour: Boolean): String =
        if (use24Hour) formattedTime24 else formattedTime12

    fun displayTime(use24Hour: Boolean): String {
        val override = customTime ?: return defaultDisplayTime(use24Hour)
        val parts = override.split(":")
        val hour = parts.getOrNull(0)?.toIntOrNull()?.coerceIn(0, 23)
            ?: return defaultDisplayTime(use24Hour)
        val minute = parts.getOrNull(1)?.toIntOrNull()?.coerceIn(0, 59)
            ?: return defaultDisplayTime(use24Hour)
        if (use24Hour) return String.format(java.util.Locale.US, "%02d:%02d", hour, minute)

        val amPm = if (hour >= 12) "PM" else "AM"
        val hour12 = when (hour % 12) {
            0 -> 12
            else -> hour % 12
        }
        return String.format(java.util.Locale.US, "%d:%02d %s", hour12, minute, amPm)
    }
}

data class CalculationMethod(
    val id: Int,
    val name: String,
    val description: String
)

data class PrayerScheduleData(
    val city: String,
    val country: String = "India",
    val methodId: Int,
    val methodName: String,
    val dateGregorian: String,
    val dateHijri: String,
    val timezone: String,
    val prayers: List<PrayerItem>,
    val isOfflineCache: Boolean = false,
    val cachedAtMillis: Long = System.currentTimeMillis()
) {
    val nextPrayer: PrayerItem?
        get() = prayers.firstOrNull { it.isNext } ?: prayers.firstOrNull { !it.isPassed && it.type.isPrimaryPrayer }
}

object AzaanSoundIds {
    const val MADINAH = "madinah"
    const val DEVICE_DEFAULT = "device_default"
    const val CUSTOM = "custom"
}

data class UserSettings(
    val selectedCity: String = "Delhi",
    val methodId: Int = 1,
    val themeMode: String = "DARK", // "SYSTEM", "LIGHT", "DARK" — defaults to Black Leather
    val notificationsEnabled: Boolean = true,
    val reminderOffsetMinutes: Int = 5, // 0, 5, 10, 15, 30
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val is24HourFormat: Boolean = false,
    val mutedPrayerNames: Set<String> = emptySet(),
    /** Overrides are keyed by yyyy-MM-dd|PRAYER_NAME and apply to that day only. */
    val customPrayerTimes: Map<String, String> = emptyMap(),
    val azaanSoundId: String = AzaanSoundIds.MADINAH,
    val customAzaanName: String? = null,
    val customAzaanUri: String? = null
)

val POPULAR_INDIAN_CITIES = listOf(
    "Delhi",
    "Mumbai",
    "Bengaluru",
    "Hyderabad",
    "Kolkata",
    "Chennai",
    "Lucknow",
    "Ahmedabad",
    "Pune",
    "Srinagar",
    "Patna",
    "Jaipur",
    "Bhopal",
    "Surat",
    "Kanpur",
    "Nagpur",
    "Varanasi",
    "Kozhikode",
    "Aligarh",
    "Agra"
)

val CALCULATION_METHODS = listOf(
    CalculationMethod(1, "Karachi (Univ. of Islamic Sciences)", "Default standard widely used in India & Pakistan"),
    CalculationMethod(2, "ISNA (North America)", "Islamic Society of North America"),
    CalculationMethod(3, "Muslim World League (MWL)", "Standard international calculation"),
    CalculationMethod(4, "Umm Al-Qura, Makkah", "Official Saudi Arabia calculation"),
    CalculationMethod(5, "Egyptian General Authority", "Standard for Egypt and Africa"),
    CalculationMethod(7, "Institute of Geophysics, Tehran", "Leveled angle calculation"),
    CalculationMethod(13, "Diyanet İşleri Başkanlığı, Turkey", "Presidency of Religious Affairs"),
    CalculationMethod(14, "Spiritual Administration of Russia", "Standard for Russian Federation")
)
