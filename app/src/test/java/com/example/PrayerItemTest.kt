package com.example

import com.example.data.model.PrayerItem
import com.example.data.model.PrayerType
import org.junit.Assert.assertEquals
import org.junit.Test

class PrayerItemTest {

    @Test
    fun `custom time is shown in both 12 and 24 hour formats while default remains available`() {
        val fajr = PrayerItem(
            type = PrayerType.FAJR,
            rawTime = "05:05",
            formattedTime12 = "5:05 AM",
            formattedTime24 = "05:05",
            targetEpochMillis = 0L,
            customTime = "05:35"
        )

        assertEquals("5:35 AM", fajr.displayTime(use24Hour = false))
        assertEquals("05:35", fajr.displayTime(use24Hour = true))
        assertEquals("5:05 AM", fajr.defaultDisplayTime(use24Hour = false))
        assertEquals("05:05", fajr.defaultDisplayTime(use24Hour = true))
    }
}
