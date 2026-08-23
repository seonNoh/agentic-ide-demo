# README structure: agentic-ide-demo

The three README variants describe the same Kotlin and Spring Boot note application. Each keeps the H1, the language switcher directly below it, the nine-section order, repository facts, endpoint table, and all fenced command blocks. Prose and diagram labels are localized for Korean and Japanese readers.

## Required order

1. `Overview` / `개요` / `概要`: identify the note application and its comparison scope.
2. `Repository layout` / `저장소 구조` / `リポジトリ構成`: show the actual Kotlin, resource, and test layout.
3. `Quick start` / `빠른 시작` / `すぐに始める`: provide the exact Gitea clone and Gradle Wrapper commands.
4. `Application structure` / `애플리케이션 구조` / `アプリケーション構成`: explain the controllers, services, repository, and database.
5. `Demo scenarios` / `데모 시나리오` / `デモシナリオ`: summarize the four IDE workflows and source scripts.
6. `HTTP endpoints` / `HTTP 엔드포인트` / `HTTP エンドポイント`: list the routes implemented by the controllers.
7. `GitHub and Gitea` / `GitHub와 Gitea` / `GitHub と Gitea`: document the source repository, push mirror, branch, and commit.
8. `Operations` / `운영` / `運用`: explain the H2 lifecycle and test command.
9. `Related` / `관련 자료` / `関連資料`: link the presentation scripts and official project documentation.

## Language and diagram mapping

- `README.md` references the four English SVGs in `docs/svg/`.
- `README.ko.md` references `.ko.svg` variants and uses Korean plain-form prose.
- `README.ja.md` references `.ja.svg` variants and uses Japanese 常体 prose.
- The language switcher is the same independent paragraph immediately below each H1.
- All three README files contain the same three fenced command blocks byte-for-byte.

## Repository-specific facts required

- Gitea source URL: `https://git.seonology.com/seon-labs/agentic-ide-demo`
- GitHub push mirror URL: `https://github.com/seonNoh/agentic-ide-demo`
- Default branch: `main`
- Source commit: `b1dd56bc2045d54a4f1af43958753843e38be883`
- Runtime/build baseline: Kotlin 1.9, Java 21, Spring Boot 3.5, Gradle Kotlin DSL
- Persistence baseline: Spring Data JPA and H2 in-memory database
- No workflow files, runs, secrets, variables, environments, or tags
- Gitea Actions disabled
