package com.seonology.demo.note

import com.seonology.demo.stats.StatsService
import jakarta.validation.Valid
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.Size
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.validation.BindingResult
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.ModelAttribute
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestMapping

@Controller
@RequestMapping("/")
class NoteController(
    private val service: NoteService,
    private val statsService: StatsService,
) {

    @GetMapping
    fun index(model: Model): String {
        model.addAttribute("notes", service.findAll())
        model.addAttribute("stats", statsService.summary())
        return "index"
    }

    @GetMapping("notes/new")
    fun newForm(model: Model): String {
        if (!model.containsAttribute("form")) {
            model.addAttribute("form", NoteForm())
        }
        return "new"
    }

    @PostMapping("notes")
    fun create(@Valid @ModelAttribute("form") form: NoteForm, br: BindingResult): String {
        if (br.hasErrors()) return "new"
        service.create(form.title, form.content, form.color)
        return "redirect:/"
    }

    @GetMapping("notes/{id}")
    fun detail(@PathVariable id: Long, model: Model): String {
        model.addAttribute("note", service.findById(id))
        return "detail"
    }

    @PostMapping("notes/{id}/delete")
    fun delete(@PathVariable id: Long): String {
        service.delete(id)
        return "redirect:/"
    }
}

data class NoteForm(
    @field:NotBlank
    @field:Size(max = 200)
    var title: String = "",

    @field:NotBlank
    @field:Size(max = 4000)
    var content: String = "",

    @field:NotBlank
    var color: String = "slate",
)
