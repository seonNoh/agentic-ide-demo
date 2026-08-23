# Agentic IDE Demo

Base project for a side-by-side comparison talk on four agentic IDEs:

- **Kiro** (AWS) — spec-driven, agent hooks
- **GitHub Copilot in VS Code** — agent + inline + next edit + cloud agent
- **Google Antigravity** — multi-agent, artifacts, manager view
- **JetBrains Junie** — IDE-native, three modes (Auto / Think / Brave)

All four tools are exercised against this same codebase using the same model (Claude Opus 4.6 or 4.7) so that the differences observed are purely from the agent harness, not the model.

## Stack

- Kotlin 1.9 + Java 21
- Spring Boot 3.5 (Web, Data JPA, Thymeleaf, Validation)
- H2 in-memory database
- Gradle (Kotlin DSL)
- JUnit 5

## Quick start

```bash
./gradlew bootRun
```

Then open:

| Path | Purpose |
| --- | --- |
| `http://localhost:8090/` | Notes dashboard (Thymeleaf UI) |
| `http://localhost:8090/notes/new` | Create a new note |
| `http://localhost:8090/api/notes` | REST API |
| `http://localhost:8090/api/stats` | Stats JSON |
| `http://localhost:8090/h2-console` | H2 console (JDBC URL: `jdbc:h2:mem:notes`) |

Run tests:

```bash
./gradlew test
```

## Layout

```
src/main/kotlin/com/seonology/demo/
  AgenticIdeDemoApplication.kt
  note/
    Note.kt              # JPA entity
    NoteRepository.kt
    NoteService.kt
    NoteController.kt    # Thymeleaf
    NoteApiController.kt # REST
  stats/
    StatsService.kt
    StatsController.kt
src/main/resources/
  application.properties
  data.sql               # seed notes
  templates/
    fragments/header.html
    index.html
    new.html
    detail.html
```

## Demo scripts

See language-specific demo scripts:

- [DEMO.ko.md](DEMO.ko.md) — 한국어
- [DEMO.ja.md](DEMO.ja.md) — 日本語

Each script contains four "strength" scenarios (one per tool) plus one cross-tool comparison scenario, with prompts ready to copy.

## Why this base

Small enough to read in five minutes, large enough to exercise:

- Multi-file edits (controller + service + entity + template + test)
- Database schema change (add a column)
- Refactoring (split a service)
- UI change with immediate visual feedback (Thymeleaf + Tailwind)
- REST API change with breaking diff

That set covers the corners of each tool's strengths.
