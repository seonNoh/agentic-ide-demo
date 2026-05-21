package com.seonology.demo.stats

import com.seonology.demo.note.NoteRepository
import org.springframework.stereotype.Service
import java.time.LocalDate

data class StatsSummary(
    val total: Int,
    val today: Int,
    val byColor: Map<String, Int>,
)

@Service
class StatsService(private val noteRepo: NoteRepository) {

    fun summary(): StatsSummary {
        val notes = noteRepo.findAll()
        val today = LocalDate.now()
        val todayCount = notes.count { it.createdAt.toLocalDate() == today }
        val byColor = notes.groupingBy { it.color }.eachCount()
        return StatsSummary(total = notes.size, today = todayCount, byColor = byColor)
    }
}
