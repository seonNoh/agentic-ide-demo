# agentic-ide-demo

[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)

## 개요

`agentic-ide-demo`는 하나의 안정된 JVM 코드베이스에서 네 가지 에이전트형 IDE 작업 방식을 비교하기 위해 의도적으로 작게 만든 Kotlin·Spring Boot 노트 애플리케이션이다. Thymeleaf 대시보드와 JSON API가 노트 도메인, 서비스, Spring Data JPA 리포지토리, H2 데이터베이스, 테스트를 함께 사용한다. 애플리케이션을 고정한 상태에서 Kiro, VS Code의 GitHub Copilot, Google Antigravity, JetBrains Junie가 서로 다른 에이전트 하네스를 실행한다.

검증한 빌드는 Kotlin 1.9.25, Java 21, Spring Boot 3.5.6, Gradle Kotlin DSL, Thymeleaf, Spring Data JPA, H2, Bean Validation, JUnit 5를 사용한다.

![프로젝트 개요](docs/readme/ko/project-overview.svg)

## 저장소 구조

![저장소 구조](docs/readme/ko/repository-structure.svg)

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

저장소 운영 메타데이터는 `.gitea/`, `gitea-settings.json`, `apply-gitea-settings.sh`에 있다. 루트의 README 세 개가 운영 진입점이며, 발표용 프롬프트는 `DEMO.ko.md`와 `DEMO.ja.md`에 그대로 둔다. 이관 전 영어 문서는 `docs/README.original.en.md`에 바이트 단위로 보존되어 있고, `README_STRUCTURE.md`는 문서 계약을 기록한다.

## 빠른 시작

Java 21과 Git이 필요하다. Gradle Wrapper를 사용하므로 Gradle을 따로 설치하지 않아도 된다.

```bash
java -version
git --version
git clone https://git.seonology.com/seon-labs/agentic-ide-demo.git
cd agentic-ide-demo
```

로컬 애플리케이션을 시작한다.

```bash
./gradlew bootRun
```

브라우저에서 `http://localhost:8090/`을 연다. 노트 작성 화면은 `/notes/new`, REST 컬렉션은 `/api/notes`, 통계 응답은 `/api/stats`, H2 콘솔은 `/h2-console`에 있다.

## 빌드 및 배포

실행 가능한 아카이브를 만들기 전에 테스트를 실행한다.

```bash
./gradlew test
./gradlew clean bootJar
java -jar build/libs/agentic-ide-demo-0.0.1-SNAPSHOT.jar
```

저장소에는 컨테이너 이미지, 인프라 매니페스트, 호스팅 환경 프로파일, 자동 배포 워크플로가 없다. `bootRun`과 실행 가능한 Spring Boot JAR는 모두 포트 `8090`에서 하나의 로컬 프로세스를 시작한다. 이 프로세스를 외부에 게시하는 작업은 저장소 범위에 포함되지 않는다.

## 요청 흐름

![노트 요청 흐름](docs/readme/ko/request-flow.svg)

`NoteController`는 HTML 폼 경로를 받고 Thymeleaf 뷰 이름을 반환한다. `NoteApiController`는 JSON 본문을 검증하고 `NoteResponse` 객체를 반환한다. 두 컨트롤러 모두 `NoteService`를 호출한다. 조회 메서드는 읽기 전용 트랜잭션에서 실행되고 생성, 수정, 삭제 메서드는 쓰기 트랜잭션을 연다. `NoteRepository`는 H2로 이어지는 JPA 경계를 제공한다. 별도의 `StatsController`는 같은 리포지토리를 읽는 `StatsService`를 호출해 `total`, `today`, `byColor`를 반환한다.

## 설정

![런타임 설정 구조](docs/readme/ko/configuration-structure.svg)

`src/main/resources/application.properties`가 유일한 런타임 설정 파일이다. 저장소에는 프로파일이나 환경 변수 재정의가 없다.

| 키 | 저장소 기본값 | 역할 |
| --- | --- | --- |
| `spring.application.name` | `agentic-ide-demo` | Spring 애플리케이션 이름을 정한다 |
| `spring.datasource.url` | `jdbc:h2:mem:notes;MODE=PostgreSQL;DB_CLOSE_DELAY=-1` | PostgreSQL 호환 모드의 인메모리 H2 데이터베이스를 만든다 |
| `spring.datasource.driver-class-name` | `org.h2.Driver` | H2 JDBC 드라이버를 선택한다 |
| `spring.datasource.username` | `sa` | 로컬 데이터베이스 사용자를 정한다 |
| `spring.datasource.password` | 비어 있음 | 로컬 H2 비밀번호를 설정하지 않는다 |
| `spring.jpa.hibernate.ddl-auto` | `create-drop` | 프로세스 수명주기에 맞춰 스키마를 만들고 제거한다 |
| `spring.jpa.open-in-view` | `false` | 뷰 렌더링에서 영속성 접근을 분리한다 |
| `spring.jpa.defer-datasource-initialization` | `true` | 시드 SQL보다 먼저 JPA 스키마를 만든다 |
| `spring.h2.console.enabled` | `true` | H2 브라우저 콘솔을 활성화한다 |
| `spring.h2.console.path` | `/h2-console` | 콘솔 경로를 정한다 |
| `spring.sql.init.mode` | `always` | 시작할 때 `data.sql`을 불러온다 |
| `server.port` | `8090` | HTTP 수신 포트를 정한다 |

## 보안 및 시크릿

애플리케이션에는 인증이나 권한 확인 의존성이 없다. 따라서 HTML 경로, JSON API, H2 콘솔은 신뢰할 수 있는 로컬 데모 환경에서만 사용해야 한다. 템플릿은 `https://cdn.tailwindcss.com`에서 Tailwind CSS를 읽으므로 UI 실행 시 외부 스크립트에도 의존한다.

애플리케이션 시크릿 값은 커밋되어 있지 않다. `spring.datasource.password`는 로컬 H2에서 의도적으로 비워 둔 설정이다. `apply-gitea-settings.sh`는 실행할 때 `TOK`라는 시크릿 이름을 요구하며, 값이 없으면 종료한다. 그 값은 저장소나 명령 기록에 넣으면 안 된다. 라이브 확인 결과 Gitea Actions와 GitHub Actions에 시크릿이나 변수가 없었다. Gitea에서는 Actions가 비활성화되어 있고 두 원격 저장소 모두 워크플로가 없다.

## 개념도

![에이전트형 IDE 비교 개념도](docs/readme/ko/demo-scenarios.svg)

한 번의 비교에서는 네 도구에 동일한 모델을 사용한다. 따라서 결과는 모델 변경이 아니라 에이전트 하네스의 차이를 보여 준다. Kiro는 명세 주도 태그 기능, Copilot은 네 가지 상호작용 방식, Antigravity는 독립 작업 위임, Junie는 JVM 네이티브 운영 모드 세 가지를 다룬다. 공통 베이스는 여러 파일 편집, 데이터베이스 스키마 변경, 서비스 분리, Thymeleaf UI 변경, 호환성을 깨는 REST API 변경을 포함한다. 두 `DEMO` 문서에는 바로 복사할 수 있는 프롬프트와 평가표가 있다.

## 애플리케이션 아키텍처

![애플리케이션 아키텍처](docs/readme/ko/application-architecture.svg)

`AgenticIdeDemoApplication`이 하나의 Spring Boot 프로세스를 시작한다. 웹 어댑터는 `NoteService` 또는 `StatsService`를 호출한다. `NoteService`는 `NoteRepository`를 통해 변경 사항을 기록하고, `StatsService`는 같은 노트에서 통계를 계산한다. JPA는 `Note`를 기준으로 `notes` 테이블을 만들고 `data.sql`은 스키마를 만든 뒤 샘플 행 여섯 개를 넣는다. 데이터베이스가 메모리에 있고 스키마 모드가 `create-drop`이므로 프로세스를 다시 시작하면 데이터가 초기화된다.

## HTTP 엔드포인트

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/` | 노트 대시보드를 렌더링한다 |
| `GET` | `/notes/new` | 노트 작성 화면을 렌더링한다 |
| `POST` | `/notes` | 노트를 만들고 대시보드로 이동한다 |
| `GET` | `/notes/{id}` | 노트 하나를 렌더링한다 |
| `POST` | `/notes/{id}/delete` | 노트를 삭제하고 대시보드로 이동한다 |
| `GET` | `/api/notes` | 모든 노트를 JSON으로 반환한다 |
| `GET` | `/api/notes/{id}` | 노트 하나를 JSON으로 반환한다 |
| `POST` | `/api/notes` | JSON으로 노트를 만든다 |
| `PUT` | `/api/notes/{id}` | JSON으로 노트를 수정한다 |
| `DELETE` | `/api/notes/{id}` | 노트를 삭제한다 |
| `GET` | `/api/stats` | 노트 수를 `total`, `today`, `byColor`로 반환한다 |

## GitHub와 Gitea

작업 소스는 `https://git.seonology.com/seon-labs/agentic-ide-demo`의 `main` 브랜치다. Gitea는 `sync_on_commit=true`와 8시간 보조 주기로 `https://github.com/seonNoh/agentic-ide-demo`에 push 미러를 보낸다. 두 원격 저장소의 `main` 브랜치는 동일한 최신 커밋을 가리킨다. 최초 GitHub 원본 기준점은 `b1dd56bc2045d54a4f1af43958753843e38be883`이다.

라이브 확인 결과 브랜치 보호와 Gitea Actions 실행, 러너, 시크릿, 변수가 없었다. GitHub 상태는 `workflows=0`, `runs=0`, `secrets=0`, `variables=0`, `environments=0`이었고 두 원격 저장소 모두 `tags=0`이었다. 이 저장소에서는 Gitea Actions를 비활성화했다. 문서를 관리할 때 어느 공급자의 Actions도 시작하면 안 된다.

## 운영

변경 검증에는 `./gradlew test`를 사용한다. 포트 `8090`을 다른 프로세스가 사용 중이라면 해당 프로세스를 중지하거나 로컬 실행에서 임시 Spring 속성을 명시한다. 애플리케이션은 `Ctrl+C`로 중지한다. 다시 시작하면 샘플 노트 여섯 개가 복원되고 이전 프로세스에서 만든 노트는 사라진다.

## 관련 경로

- [한국어 데모 스크립트](DEMO.ko.md): 비교용 프롬프트와 평가표가 있다.
- [일본어 데모 스크립트](DEMO.ja.md): 같은 발표 흐름을 일본어로 제공한다.
- [원본 영어 README](docs/README.original.en.md): 소스 문서를 바이트 단위로 보존한다.
- [README 구조 계약](README_STRUCTURE.md): 절, 사실, 다이어그램 대응 관계를 기록한다.
- [기여 가이드](CONTRIBUTING.md): 기여와 검토 기준을 설명한다.
- [Gitea Issues](https://git.seonology.com/seon-labs/agentic-ide-demo/issues): 질문과 결함을 등록한다.
- [Spring Boot documentation](https://docs.spring.io/spring-boot/)
- [Kotlin documentation](https://kotlinlang.org/docs/home.html)
- [Gradle Kotlin DSL documentation](https://docs.gradle.org/current/userguide/kotlin_dsl.html)
