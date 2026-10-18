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
    val rawTime: String, // e.g. "05:05"
    val formattedTime12: String, // e.g. "05:05 AM"
    val formattedTime24: String, // e.g. "05:05"
    val targetEpochMillis: Long,
    val isNext: Boolean = false,
    val isPassed: Boolean = false,
    val notificationEnabled: Boolean = true,
    /** User defined time ("HH:mm") that overrides the calculated one. */
    val customRawTime: String? = null,
    val customFormattedTime12: String? = null,
    val customFormattedTime24: String? = null,
    val customEpochMillis: Long? = null
) {
    fun displayTime(use24Hour: Boolean): String = if (use24Hour) formattedTime24 else formattedTime12

    /** The calculated time, shown next to the custom one. */
    fun defaultTime(use24Hour: Boolean): String = displayTime(use24Hour)

    /** The time the app works with: the custom one when the user set it. */
    fun effectiveTime(use24Hour: Boolean): String = when {
        !hasCustomTime -> displayTime(use24Hour)
        use24Hour -> customFormattedTime24 ?: formattedTime24
        else -> customFormattedTime12 ?: formattedTime12
    }

    val hasCustomTime: Boolean
        get() = customEpochMillis != null

    /** Epoch used for the countdown and for the reminder alarms. */
    val effectiveEpochMillis: Long
        get() = customEpochMillis ?: targetEpochMillis

    /** The hour and minute of the time that is in use ("HH:mm"). */
    fun effectiveHourMinute(): Pair<Int, Int> {
        val raw = customRawTime ?: rawTime
        return try {
            val parts = raw.split(":")
            parts[0].trim().toInt() to parts[1].trim().toInt()
        } catch (e: Exception) {
            0 to 0
        }
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

data class UserSettings(
    val selectedCity: String = "Delhi",
    val methodId: Int = 1,
    val themeMode: String = "SYSTEM", // "SYSTEM", "LIGHT", "DARK"
    val notificationsEnabled: Boolean = true,
    val reminderOffsetMinutes: Int = 5, // 0, 5, 10, 15, 30
    val soundEnabled: Boolean = true,
    val vibrationEnabled: Boolean = true,
    val is24HourFormat: Boolean = false,
    val mutedPrayerNames: Set<String> = emptySet(),
    /** Prayer name -> user defined time ("HH:mm"), overriding the calculation. */
    val customPrayerTimes: Map<String, String> = emptyMap(),
    /** Id of the selected azaan, or null for the default notification sound. */
    val selectedAzaanId: String? = AzaanCatalogue.DEFAULT_AZAAN_ID
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
