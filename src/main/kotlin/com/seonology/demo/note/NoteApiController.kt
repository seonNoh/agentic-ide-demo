package com.seonology.demo.note

import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.web.bind.annotation.DeleteMapping
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.PutMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.ResponseStatus
import org.springframework.web.bind.annotation.RestController
import java.time.LocalDateTime

@RestController
@RequestMapping("/api/notes")
class NoteApiController(private val service: NoteService) {

    @GetMapping
    fun list(): List<NoteResponse> = service.findAll().map(::toResponse)

    @GetMapping("/{id}")
    fun get(@PathVariable id: Long): NoteResponse = toResponse(service.findById(id))

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    fun create(@Valid @RequestBody req: NoteRequest): NoteResponse =
        toResponse(service.create(req.title, req.content, req.color))

    @PutMapping("/{id}")
    fun update(@PathVariable id: Long, @Valid @RequestBody req: NoteRequest): NoteResponse =
        toResponse(service.update(id, req.title, req.content, req.color))

    @DeleteMapping("/{id}")
    fun delete(@PathVariable id: Long): ResponseEntity<Void> {
        service.delete(id)
        return ResponseEntity.noContent().build()
    }

    @ExceptionHandler(NoSuchElementException::class)
    fun notFound(e: NoSuchElementException): ResponseEntity<Map<String, String>> =
        ResponseEntity
            .status(HttpStatus.NOT_FOUND)
            .body(mapOf("message" to (e.message ?: "not found")))

    private fun toResponse(n: Note) = NoteResponse(
        id = n.id!!,
        title = n.title,
        content = n.content,
        color = n.color,
        createdAt = n.createdAt,
        updatedAt = n.updatedAt,
    )
}

data class NoteRequest(
    @field:NotBlank
    @field:Size(max = 200)
    val title: String,

    @field:NotBlank
    @field:Size(max = 4000)
    val content: String,

    val color: String = "slate",
)

data class NoteResponse(
    val id: Long,
    val title: String,
    val content: String,
    val color: String,
    val createdAt: LocalDateTime,
    val updatedAt: LocalDateTime,
)
