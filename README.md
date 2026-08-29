# agentic-ide-demo

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

## Overview

`agentic-ide-demo` is a deliberately small Kotlin and Spring Boot note application for comparing four agentic IDE workflows on one stable JVM codebase. A Thymeleaf dashboard and JSON API share the same note domain, services, Spring Data JPA repository, H2 database, and tests. This keeps the application constant while Kiro, GitHub Copilot in VS Code, Google Antigravity, and JetBrains Junie exercise different agent harnesses.

The verified build uses Kotlin 1.9.25, Java 21, Spring Boot 3.5.6, Gradle Kotlin DSL, Thymeleaf, Spring Data JPA, H2, Bean Validation, and JUnit 5.

![Project overview](docs/readme/en/project-overview.svg)

## Repository layout

![Repository structure](docs/readme/en/repository-structure.svg)

```text
src/main/kotlin/com/seonology/demo/
  AgenticIdeDemoApplication.kt
  note/   # entity, repository, service, Thymeleaf controller, REST controller
  stats/  # statistics service and JSON controller
src/main/resources/
  application.properties
  data.sql
  templates/  # index, new, detail, and shared header
src/test/kotlin/com/seonology/demo/
  AgenticIdeDemoApplicationTests.kt
  note/  # REST and service tests
```

Repository-level operating metadata lives in `.gitea/`, `gitea-settings.json`, and `apply-gitea-settings.sh`. The three root READMEs are the operating entry points; the presentation prompts remain in `DEMO.ko.md` and `DEMO.ja.md`. The pre-migration English document is preserved byte-for-byte at `docs/README.original.en.md`, and `README_STRUCTURE.md` records the documentation contract.

## Quick start

Java 21 and Git are required. The application uses the Gradle Wrapper, so a separate Gradle installation is not required.

```bash
java -version
git --version
git clone https://git.seonology.com/seon-labs/agentic-ide-demo.git
cd agentic-ide-demo
```

Start the local application:

```bash
./gradlew bootRun
```

Open `http://localhost:8090/`. The note form is at `/notes/new`, the REST collection at `/api/notes`, the statistics response at `/api/stats`, and the H2 console at `/h2-console`.

## Build and deployment

Run the test suite before producing an executable archive:

```bash
./gradlew test
./gradlew clean bootJar
java -jar build/libs/agentic-ide-demo-0.0.1-SNAPSHOT.jar
```

The repository has no container image, infrastructure manifest, hosted-environment profile, or automated deployment workflow. `bootRun` and the executable Spring Boot JAR both start one local process on port `8090`; publishing that process is outside this repository's scope.

## Request flow

![Note request flow](docs/readme/en/request-flow.svg)

`NoteController` accepts the HTML form routes and returns Thymeleaf view names. `NoteApiController` validates JSON bodies and returns `NoteResponse` objects. Both call `NoteService`, whose read methods run in a read-only transaction and whose create, update, and delete methods open write transactions. `NoteRepository` provides the JPA boundary to H2. `StatsController` separately calls `StatsService`, which reads the same repository and returns `total`, `today`, and `byColor`.

## Configuration

![Runtime configuration structure](docs/readme/en/configuration-structure.svg)

`src/main/resources/application.properties` is the only runtime configuration file; the repository defines no profiles or environment-variable overrides.

| Key | Repository default | Effect |
| --- | --- | --- |
| `spring.application.name` | `agentic-ide-demo` | Names the Spring application |
| `spring.datasource.url` | `jdbc:h2:mem:notes;MODE=PostgreSQL;DB_CLOSE_DELAY=-1` | Creates an in-memory H2 database with PostgreSQL compatibility |
| `spring.datasource.driver-class-name` | `org.h2.Driver` | Selects the H2 JDBC driver |
| `spring.datasource.username` | `sa` | Sets the local database user |
| `spring.datasource.password` | empty | Leaves the local H2 password unset |
| `spring.jpa.hibernate.ddl-auto` | `create-drop` | Recreates and removes the schema with the process lifecycle |
| `spring.jpa.open-in-view` | `false` | Keeps persistence access outside view rendering |
| `spring.jpa.defer-datasource-initialization` | `true` | Creates the JPA schema before loading seed SQL |
| `spring.h2.console.enabled` | `true` | Enables the H2 browser console |
| `spring.h2.console.path` | `/h2-console` | Sets the console path |
| `spring.sql.init.mode` | `always` | Loads `data.sql` at startup |
| `server.port` | `8090` | Sets the HTTP listener port |

## Security and secrets

The application has no authentication or authorization dependency. Its HTML routes, JSON API, and H2 console are therefore suitable only for a trusted local demo environment. The templates load Tailwind CSS from `https://cdn.tailwindcss.com`, so the UI also depends on that external script at runtime.

No application secret value is committed. `spring.datasource.password` is an intentionally empty local H2 setting. `apply-gitea-settings.sh` requires the secret name `TOK` at execution time and exits if it is absent; do not write its value into the repository or command history. Live inspection found no Gitea Actions secrets or variables and no GitHub Actions secrets or variables. Actions are disabled on Gitea, and no workflow exists on either remote.

## Concept map

![Agentic IDE comparison concept](docs/readme/en/demo-scenarios.svg)

All four tools use the same model during a comparison run, so the result isolates the agent harness rather than a model change. Kiro exercises a specification-driven tag feature, Copilot combines four interaction modes, Antigravity delegates independent tasks, and Junie compares three JVM-native operating modes. The shared base covers multi-file editing, a database schema change, service splitting, a Thymeleaf UI change, and a breaking REST API change. The two `DEMO` documents contain the copy-ready prompts and evaluation sheet.

## Application architecture

![Application architecture](docs/readme/en/application-architecture.svg)

`AgenticIdeDemoApplication` starts one Spring Boot process. The web adapters call `NoteService` or `StatsService`; `NoteService` writes through `NoteRepository`, while `StatsService` derives counts from the same notes. JPA builds the `notes` table from `Note`, and `data.sql` inserts six sample rows after schema creation. Because the database is in memory and the schema mode is `create-drop`, restarting the process resets the data.

## HTTP endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | Render the note dashboard |
| `GET` | `/notes/new` | Render the note form |
| `POST` | `/notes` | Create a note and redirect to the dashboard |
| `GET` | `/notes/{id}` | Render one note |
| `POST` | `/notes/{id}/delete` | Delete a note and redirect to the dashboard |
| `GET` | `/api/notes` | Return all notes as JSON |
| `GET` | `/api/notes/{id}` | Return one note as JSON |
| `POST` | `/api/notes` | Create a note from JSON |
| `PUT` | `/api/notes/{id}` | Update a note from JSON |
| `DELETE` | `/api/notes/{id}` | Delete a note |
| `GET` | `/api/stats` | Return `total`, `today`, and `byColor` counts |

## GitHub and Gitea

The working source is `https://git.seonology.com/seon-labs/agentic-ide-demo` on `main`. Gitea sends a push mirror to `https://github.com/seonNoh/agentic-ide-demo` with `sync_on_commit=true` and an eight-hour fallback interval. The `main` branches on both remotes point to the same current commit. The initial GitHub source baseline was `b1dd56bc2045d54a4f1af43958753843e38be883`.

Live inspection found no branch protection or Gitea Actions runs, runners, secrets, or variables. GitHub reported `workflows=0`, `runs=0`, `secrets=0`, `variables=0`, and `environments=0`; both remotes had `tags=0`. Gitea Actions is disabled for this repository. Do not start either provider's Actions while maintaining this documentation.

## Operations

Use `./gradlew test` as the change gate. If port `8090` is occupied, stop the conflicting process or explicitly provide a temporary Spring property when running locally. Stop the application with `Ctrl+C`. A restart restores the six seed notes and discards notes created during the previous process.

## Related

- [Korean demo script](DEMO.ko.md): copy-ready comparison prompts and the scoring sheet.
- [Japanese demo script](DEMO.ja.md): the same presentation workflow localized for Japanese readers.
- [Original English README](docs/README.original.en.md): byte-preserved source documentation.
- [README structure contract](README_STRUCTURE.md): section, fact, and diagram mapping.
- [Contributing guide](CONTRIBUTING.md): contribution and review expectations.
- [Gitea Issues](https://git.seonology.com/seon-labs/agentic-ide-demo/issues): questions and defect reports.
- [Spring Boot documentation](https://docs.spring.io/spring-boot/)
- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Gradle Kotlin DSL documentation](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
