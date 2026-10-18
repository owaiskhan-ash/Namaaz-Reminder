package com.example.data.model

import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Date
import java.util.Locale
import java.util.TimeZone

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
    val rawTime: String, // e.g. "05:05"
    val formattedTime12: String, // e.g. "05:05 AM"
    val formattedTime24: String, // e.g. "05:05"
    val targetEpochMillis: Long,
    val isNext: Boolean = false,
    val isPassed: Boolean = false,
    val notificationEnabled: Boolean = true
) {
    fun displayTime(use24Hour: Boolean): String = if (use24Hour) formattedTime24 else formattedTime12
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

data class UserSettings(
    val selectedCity: String = "Delhi",
    val methodId: Int = 1,
    val themeMode: String = "SYSTEM", // "SYSTEM", "LIGHT", "DARK"
    val notificationsEnabled: Boolean = true,
    val reminderOffsetMinutes: Int = 5, // 0, 5, 10, 15, 30
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val is24HourFormat: Boolean = false,
    val mutedPrayerNames: Set<String> = emptySet()
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
