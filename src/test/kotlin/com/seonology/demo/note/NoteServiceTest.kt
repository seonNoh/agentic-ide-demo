package com.seonology.demo.note

import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.transaction.annotation.Transactional
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertFailsWith
import kotlin.test.assertNotNull

@SpringBootTest
@Transactional
class NoteServiceTest @Autowired constructor(
    private val service: NoteService,
) {

    @Test
    fun `creates and retrieves a note`() {
        val saved = service.create("Title", "Content body", "indigo")
        assertNotNull(saved.id)

        val found = service.findById(saved.id!!)
        assertEquals("Title", found.title)
        assertEquals("indigo", found.color)
    }

    @Test
    fun `updates a note`() {
        val saved = service.create("Original", "Original body", "slate")

        val updated = service.update(saved.id!!, "Renamed", "Updated body", "rose")

        assertEquals("Renamed", updated.title)
        assertEquals("Updated body", updated.content)
        assertEquals("rose", updated.color)
    }

    @Test
    fun `delete throws when note does not exist`() {
        assertFailsWith<NoSuchElementException> {
            service.delete(99_999L)
        }
    }
}
