package com.seonology.demo.note

import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Transactional
import java.time.LocalDateTime

@Service
@Transactional(readOnly = true)
class NoteService(private val repo: NoteRepository) {

    fun findAll(): List<Note> = repo.findAll().sortedByDescending { it.updatedAt }

    fun findById(id: Long): Note =
        repo.findById(id).orElseThrow { NoSuchElementException("note $id not found") }

    @Transactional
    fun create(title: String, content: String, color: String): Note {
        val note = Note(title = title, content = content, color = color)
        return repo.save(note)
    }

    @Transactional
    fun update(id: Long, title: String, content: String, color: String): Note {
        val note = findById(id)
        note.title = title
        note.content = content
        note.color = color
        note.updatedAt = LocalDateTime.now()
        return note
    }

    @Transactional
    fun delete(id: Long) {
        if (!repo.existsById(id)) throw NoSuchElementException("note $id not found")
        repo.deleteById(id)
    }
}
