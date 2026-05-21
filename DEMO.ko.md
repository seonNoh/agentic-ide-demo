# 발표 데모 스크립트 (한국어)

이 베이스 코드를 사용하여 4개 IDE를 비교 발표합니다. 모델은 모두 Claude Opus 4.6 또는 4.7로 통일하여 차이가 모델이 아니라 에이전트 하네스에서 오는 것임을 보여줍니다.

## 사전 준비

브랜치 4개 생성 (동일 커밋에서 분기):

```bash
git checkout -b demo/kiro
git checkout -b demo/copilot
git checkout -b demo/antigravity
git checkout -b demo/junie
```

각 도구는 자기 브랜치에서만 작업합니다.

## 시나리오 1 — Kiro 강점 시연 (spec-driven 풀 사이클)

`tag` 기능을 추가합니다. spec 모드로 시작하여 산출물 자체를 데모로 사용합니다.

**프롬프트**

```
이 프로젝트에 노트 태그(tag) 기능을 추가하고 싶습니다.

먼저 spec 모드로 진입해서 requirements.md, design.md, tasks.md를
순서대로 작성해주세요. 다음 요구사항을 반영해주세요.

- 노트 1개에 여러 태그를 붙일 수 있음
- 태그로 필터링 가능한 /api/notes?tag=xxx 엔드포인트
- 기존 노트는 태그가 비어 있어도 동작해야 함
- 마이그레이션 + JPA 엔티티 + 컨트롤러 + Thymeleaf UI + 테스트까지

설계가 확정된 후에 코드 생성을 진행합니다.
코드 생성이 끝나면 자동으로 ./gradlew test 를 실행하는
Post Task Execution hook도 함께 설정해주세요.
```

**관전 포인트**
- `requirements.md` / `design.md` / `tasks.md`가 실제로 생성되는지
- 중간에 `design.md`에서 한 항목을 수정했을 때 `tasks.md`로 cascade되는지
- Hook이 실제로 발화하여 테스트를 실행하는지

## 시나리오 2 — GitHub Copilot 강점 시연 (4-in-1 인터페이스)

한 세션 안에서 Agent mode, Inline, Next Edit Suggestions, Cloud agent를 모두 섞어 사용합니다.

**프롬프트**

```
이 프로젝트에서 다음 작업을 진행해주세요.

1. (Agent mode) Note 엔티티에 `pinned` boolean 필드 추가
   - 마이그레이션, 엔티티, 서비스, 컨트롤러, UI 모두 반영
   - pinned 노트는 목록 최상단에 표시

2. (Inline / Ctrl+I) NoteController.kt 의 index 메서드에서
   pinned 노트를 우선 정렬하도록 직접 수정

3. (Cloud agent) README.md 의 Quick start 섹션 아래에
   "Features" 절을 추가하는 작업을 비동기로 위임

작업 중 Next Edit Suggestions가 제안하는 인접 편집은 그대로 수용합니다.
```

**관전 포인트**
- 4가지 인터페이스가 한 IDE 안에서 자연스럽게 교차되는지
- Cloud agent가 정말 비동기적으로 동작하는지
- Next Edit Suggestions가 의미 있는 인접 편집을 제안하는지

## 시나리오 3 — Antigravity 강점 시연 (병렬 위임 + Artifacts)

서로 독립적인 task 3개를 Manager View에서 동시 실행합니다.

**프롬프트**

```
Manager View에서 다음 3개 task를 병렬로 실행해주세요.

Task A: NoteApiController.kt 의 응답 모델을 별도 Dto 파일로 분리.
        기존 테스트는 모두 통과해야 함.

Task B: 노트 검색 엔드포인트 추가.
        GET /api/notes/search?q=keyword (제목 + 내용 LIKE 검색).
        통합 테스트 포함.

Task C: README.md 와 DEMO.ko.md, DEMO.ja.md 의 Endpoints 표 갱신.

각 task의 Implementation Plan / Code Diffs / Walkthrough가 만들어지면
검토 요청해주세요. Artifact에 코멘트로 피드백하면서 진행하겠습니다.
```

**관전 포인트**
- 3개 에이전트가 진짜로 동시에 진행되는지 (Manager View)
- 발표자가 1~2분 자리를 뜨고 돌아왔을 때 진행 상태가 어떻게 시각화되어 있는지
- Artifact에 코멘트를 달았을 때 에이전트가 멈추지 않고 반영하는지

## 시나리오 4 — Junie 강점 시연 (3 mode 비교, JVM 홈그라운드)

동일한 리팩토링 task를 Auto → Think → Brave 모드로 차례로 진행합니다.

**프롬프트**

```
NoteService.kt 를 다음과 같이 리팩토링해주세요.

- 조회 로직과 변경 로직을 NoteQueryService 와 NoteCommandService 로 분리
- 호출부(NoteController, NoteApiController)도 그에 맞게 수정
- 기존 테스트는 전부 통과해야 함
- IntelliJ refactor 기능을 사용해서 안전하게 시그니처를 변경할 것

먼저 Auto Mode로 진행해주세요.

(완료 후)
같은 task를 새 세션에서 Think Mode로 다시 진행해주세요.

(완료 후)
같은 task를 새 세션에서 Brave Mode로 다시 진행해주세요.

각 모드에서 (a) 사전 분석량 (b) 사용자 개입 횟수 (c) 완료 시간을 측정합니다.
```

**관전 포인트**
- 3 mode의 분석량과 자율성 차이
- IntelliJ refactor·inspection·debugger 호출이 실제로 작동하는지
- Brave Mode가 위험을 어떻게 처리하는지 (또는 못 하는지)
- JVM 환경에서 다른 3개 도구(VS Code 기반)와의 격차

## 시나리오 5 — 횡비교 (4개 도구 동일 입력)

위 1~4 시나리오에서 각 도구의 색깔을 보여준 다음, 같은 시험지 1장으로 횡비교합니다.

**프롬프트 (4개 도구 모두에게 동일)**

```
이 프로젝트에 노트 즐겨찾기(favorite) 기능을 추가해주세요.

- Note 엔티티에 `favorite: Boolean` 필드 추가 (기본값 false)
- 마이그레이션 (data.sql 갱신)
- 토글용 엔드포인트 PUT /api/notes/{id}/favorite
- index.html 에 즐겨찾기 별 아이콘 + 클릭으로 토글
- favorite=true 인 노트는 목록 최상단에 표시
- 단위 + 통합 테스트 추가

완료까지 진행해주세요.
```

**평가 시트 (청중 배포용)**

| 항목 | Kiro | Copilot | Antigravity | Junie |
| --- | --- | --- | --- | --- |
| 완료까지 턴 수 |  |  |  |  |
| 사용자 개입 횟수 |  |  |  |  |
| 테스트 통과 여부 |  |  |  |  |
| 불필요한 파일 변경 |  |  |  |  |
| 체감 시간 |  |  |  |  |

## 측정 팁

- 측정 전 `git stash` 또는 clean 상태 확인
- 사람이 직접 했을 때의 "정답"을 미리 메모해두고 비교
- 도구가 끝났다고 선언한 시점에 측정 종료
- 인간 개입은 도구가 명시적으로 물었을 때만 답하고, 먼저 끼어들지 않음
