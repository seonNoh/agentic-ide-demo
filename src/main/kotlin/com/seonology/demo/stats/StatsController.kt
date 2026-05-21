package com.seonology.demo.stats

import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

@RestController
@RequestMapping("/api/stats")
class StatsController(private val statsService: StatsService) {

    @GetMapping
    fun summary(): StatsSummary = statsService.summary()
}
