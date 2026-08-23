#!/usr/bin/env python3
"""Offline checks for the agentic-ide-demo migration deliverables."""

from __future__ import annotations

from collections import Counter
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "source"
CURRENT_SOURCE = ROOT if (ROOT / "src").is_dir() else SOURCE if (SOURCE / "src").is_dir() else None
SVG_DIR = ROOT / "docs" / "svg"
README_NAMES = ("README.md", "README.ko.md", "README.ja.md")
SOURCE_BASELINE = "b1dd56bc2045d54a4f1af43958753843e38be883"
SOURCE_README_SHA256 = "b6486c10f633f6a162d7fb6c5891b2442ddad4764ee9f2e1df3b49c0593eb6e5"
STATS_FIELDS = ("total", "today", "byColor")
AUTOMATION_FACTS = ("workflows=0", "runs=0", "secrets=0", "variables=0", "environments=0", "tags=0")
EXPECTED_ROUTES = (
    ("GET", "/"),
    ("GET", "/notes/new"),
    ("POST", "/notes"),
    ("GET", "/notes/{id}"),
    ("POST", "/notes/{id}/delete"),
    ("GET", "/api/notes"),
    ("GET", "/api/notes/{id}"),
    ("POST", "/api/notes"),
    ("PUT", "/api/notes/{id}"),
    ("DELETE", "/api/notes/{id}"),
    ("GET", "/api/stats"),
)
README_FACTS = {
    "README.md": (
        "the `main` branches on both remotes point to the same current commit",
        f"The initial GitHub source baseline was `{SOURCE_BASELINE}`",
        "Gitea Actions is disabled for this repository",
        "All four tools use the same model during a comparison run",
        "agent harness rather than a model change",
        "multi-file editing, a database schema change, service splitting, a Thymeleaf UI change, and a breaking REST API change",
    ),
    "README.ko.md": (
        "두 원격 저장소의 `main` 브랜치는 동일한 최신 커밋을 가리킨다",
        f"최초 GitHub 원본 기준점은 `{SOURCE_BASELINE}`이다",
        "이 저장소에서는 Gitea Actions를 비활성화했다",
        "한 번의 비교에서는 네 도구에 동일한 모델을 사용",
        "에이전트 하네스에서 발생한다",
        "여러 파일 편집, 데이터베이스 스키마 변경, 서비스 분리, Thymeleaf UI 변경, 호환성을 깨는 REST API 변경",
    ),
    "README.ja.md": (
        "両リモートの `main` ブランチは現在同じ最新コミットを指している",
        f"GitHub から取得した最初のソース基準点は `{SOURCE_BASELINE}` である",
        "このリポジトリでは Gitea Actions を無効にしている",
        "1回の比較では4つのツールに同じモデルを使う",
        "エージェントハーネス）の差として比較できる",
        "複数ファイルの編集、データベーススキーマの変更、サービスの分割、Thymeleaf UI の変更、互換性を破る REST API の変更",
    ),
}
SVG_SPECS = {
    "application-architecture": ("960", "540", "aa"),
    "request-flow": ("960", "540", "rf"),
    "demo-scenarios": ("960", "540", "ds"),
    "repository-roles": ("640", "420", "gd"),
}
LOCALIZED_DESCS = {
    ("application-architecture", ".ko"): "브라우저가 Spring Boot 컨트롤러와 서비스를 거쳐 H2 노트 데이터베이스에 접근한다.",
    ("application-architecture", ".ja"): "ブラウザから Spring Boot のコントローラとサービスを経由して H2 ノートデータベースへアクセスする。",
    ("request-flow", ".ko"): "노트 요청이 컨트롤러, 서비스, 리포지토리, 응답을 차례로 거친다.",
    ("request-flow", ".ja"): "ノートのリクエストがコントローラ、サービス、リポジトリ、レスポンスを順に通過する。",
    ("demo-scenarios", ".ko"): "네 가지 IDE 작업 흐름이 하나의 노트 애플리케이션에서 실행된다.",
    ("demo-scenarios", ".ja"): "4つの IDE ワークフローを同じノートアプリケーションで実行する。",
    ("repository-roles", ".ko"): "Gitea가 소스 저장소이고 GitHub가 push 미러를 받는다.",
    ("repository-roles", ".ja"): "Gitea がソースリポジトリで、GitHub が push ミラーを受け取る。",
}
LOCALIZED_TITLES = {
    ("repository-roles", ".ko"): "Gitea와 GitHub 저장소 역할",
    ("repository-roles", ".ja"): "Gitea と GitHub のリポジトリの役割",
}
TAILWIND = ("#0f172a", "#1e293b", "#38bdf8", "#a78bfa", "#f472b6", "#34d399", "#fbbf24")
EMOJI = re.compile(r"[\U0001F000-\U0001FAFF\u2600-\u27BF]")
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")


def fail(message: str) -> None:
    raise AssertionError(message)


def read(path: Path) -> str:
    if not path.is_file():
        fail(f"missing file: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def code_fences(text: str) -> list[str]:
    return re.findall(r"```[^\n]*\n.*?\n```", text, flags=re.DOTALL)


def inline_code(text: str) -> Counter[str]:
    return Counter(re.findall(r"`([^`\n]+)`", text))


def documented_routes(text: str) -> tuple[tuple[str, str], ...]:
    return tuple(re.findall(r"^\| `(GET|POST|PUT|DELETE)` \| `([^`]+)` \|", text, re.MULTILINE))


def normalize_route(prefix: str, suffix: str) -> str:
    parts = [part.strip("/") for part in (prefix, suffix) if part.strip("/")]
    return "/" + "/".join(parts) if parts else "/"


def controller_routes(source_root: Path) -> tuple[tuple[str, str], ...]:
    routes: list[tuple[str, str]] = []
    controller_dir = source_root / "src/main/kotlin/com/seonology/demo"
    for path in sorted(controller_dir.rglob("*Controller.kt")):
        text = path.read_text(encoding="utf-8")
        prefix_match = re.search(r'@RequestMapping\("([^\"]*)"\)', text)
        prefix = prefix_match.group(1) if prefix_match else ""
        for match in re.finditer(r'@(Get|Post|Put|Delete)Mapping(?:\("([^\"]*)"\))?', text):
            routes.append((match.group(1).upper(), normalize_route(prefix, match.group(2) or "")))
    return tuple(routes)


def check_readmes() -> None:
    texts = {name: read(ROOT / name) for name in README_NAMES}
    expected = {
        "README.md": ["# agentic-ide-demo", "## Overview", "## Repository layout", "## Quick start", "## Application structure", "## Demo scenarios", "## HTTP endpoints", "## GitHub and Gitea", "## Operations", "## Related"],
        "README.ko.md": ["# agentic-ide-demo", "## 개요", "## 저장소 구조", "## 빠른 시작", "## 애플리케이션 구조", "## 데모 시나리오", "## HTTP 엔드포인트", "## GitHub와 Gitea", "## 운영", "## 관련 자료"],
        "README.ja.md": ["# agentic-ide-demo", "## 概要", "## リポジトリ構成", "## すぐに始める", "## アプリケーション構成", "## デモシナリオ", "## HTTP エンドポイント", "## GitHub と Gitea", "## 運用", "## 関連資料"],
    }
    switcher = "[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)"
    required = (
        "https://git.seonology.com/seon-labs/agentic-ide-demo",
        "https://github.com/seonNoh/agentic-ide-demo",
        "https://git.seonology.com/seon-labs/agentic-ide-demo/issues",
        "docs/README.original.en.md",
        "CONTRIBUTING.md",
        "Kotlin 1.9",
        "Java 21",
        "Spring Boot 3.5",
        "java -version",
        "git --version",
        SOURCE_BASELINE,
        "NoteService",
        "NoteController",
        "NoteApiController",
        "StatsService",
        *STATS_FIELDS,
        *AUTOMATION_FACTS,
    )
    for name, text in texts.items():
        prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        headings = re.findall(r"^#{1,2} .+$", prose, re.MULTILINE)
        if headings != expected[name]:
            fail(f"{name} headings differ: {headings!r}")
        if not text.startswith(f"# agentic-ide-demo\n\n{switcher}\n\n"):
            fail(f"{name} language switcher is not immediately below H1")
        for value in required:
            if value not in text:
                fail(f"{name} missing fact: {value}")
        for value in README_FACTS[name]:
            if value not in text:
                fail(f"{name} missing required repository wording: {value}")
        if documented_routes(text) != EXPECTED_ROUTES:
            fail(f"{name} endpoint table differs: {documented_routes(text)!r}")
        if re.search(rf"(?i)(?:current|currently|현재|現在)[^.。\n]*{SOURCE_BASELINE}", text):
            fail(f"{name} misstates the original source baseline as the current tip")
        if re.search(r"\btip\b", text, re.IGNORECASE):
            fail(f"{name} retains unexplained tip terminology")
        if re.search(r"(?i)word[ -]?count|aggregate words?", text) or "단어 수" in text or "単語数" in text:
            fail(f"{name} misstates StatsService as calculating word counts")
        if EMOJI.search(text) or EMAIL.search(text):
            fail(f"{name} contains emoji or email")
        suffix = {"README.md": "", "README.ko.md": ".ko", "README.ja.md": ".ja"}[name]
        images = re.findall(r"!\[[^]]*\]\(([^)]+)\)", text)
        expected_images = [f"docs/svg/{stem}{suffix}.svg" for stem in ("application-architecture", "request-flow", "demo-scenarios", "repository-roles")]
        if images != expected_images:
            fail(f"{name} diagram references differ: {images!r}")
    fences = code_fences(texts["README.md"])
    if len(fences) != 4:
        fail(f"English README has {len(fences)} fenced blocks, expected 4")
    for name in README_NAMES[1:]:
        if code_fences(texts[name]) != fences:
            fail(f"{name} fenced code blocks differ byte-for-byte")
        if inline_code(texts[name]) != inline_code(texts["README.md"]):
            fail(f"{name} inline-code multiset differs from English README")
    if re.search(r"(?:습니다|ㅂ니다|합니다|됩니다|있습니다|없습니다)\.", re.sub(r"```.*?```", "", texts["README.ko.md"], flags=re.DOTALL)):
        fail("README.ko.md contains honorific prose")
    if re.search(r"(?:です|ます|ください|ありません)[。.]", re.sub(r"```.*?```", "", texts["README.ja.md"], flags=re.DOTALL)):
        fail("README.ja.md contains polite-form prose")
    if CURRENT_SOURCE is not None:
        actual_routes = controller_routes(CURRENT_SOURCE)
        if Counter(actual_routes) != Counter(EXPECTED_ROUTES) or len(actual_routes) != len(EXPECTED_ROUTES):
            fail(f"Kotlin controller routes differ: {actual_routes!r}")


def element_signature(root: ET.Element) -> list[tuple[str, tuple[tuple[str, str], ...]]]:
    ignored = {"id", "class", "aria-labelledby", "marker-end", "filter"}
    return [(element.tag.rsplit("}", 1)[-1], tuple(sorted((key, value) for key, value in element.attrib.items() if key not in ignored))) for element in root.iter()]


def check_svg() -> None:
    all_ids: dict[str, str] = {}
    for stem, (width, height, prefix) in SVG_SPECS.items():
        english = read(SVG_DIR / f"{stem}.svg")
        english_root = ET.fromstring(english)
        for suffix in ("", ".ko", ".ja"):
            name = f"{stem}{suffix}.svg"
            text = read(SVG_DIR / name)
            root = ET.fromstring(text)
            if root.attrib.get("viewBox") != f"0 0 {width} {height}":
                fail(f"{name} has unexpected viewBox")
            if "<style" not in text or "<defs" not in text or "prefers-reduced-motion" not in text:
                fail(f"{name} is not self-contained or lacks reduced motion")
            if f'<rect width="{width}" height="{height}" fill="#0d1117"/>' not in text:
                fail(f"{name} lacks explicit Relief background")
            if "font-family:Pretendard,system-ui,sans-serif" not in text and "Pretendard,system-ui,sans-serif" not in text:
                fail(f"{name} has altered font fallback")
            if any(token in text.lower() for token in TAILWIND):
                fail(f"{name} contains forbidden palette token")
            ids = re.findall(r'\bid="([^"]+)"', text)
            if len(ids) != len(set(ids)):
                fail(f"{name} contains duplicate IDs")
            variant_prefix = prefix if not suffix else prefix + "-" + suffix[1:]
            if any(not item.startswith(variant_prefix + "-") for item in ids):
                fail(f"{name} contains an ID without {variant_prefix}- prefix")
            for item in ids:
                if item in all_ids:
                    fail(f"duplicate SVG ID across files: {item}")
                all_ids[item] = name
            marker_refs = re.findall(r"marker-end=\"url\(#([^\)]+)\)\"", text)
            if any(ref not in ids for ref in marker_refs):
                fail(f"{name} references missing marker")
            url_refs = re.findall(r"url\(([^)]+)\)", text)
            for raw_ref in url_refs:
                ref = raw_ref.strip().strip("\"'")
                if not ref.startswith("#") or ref[1:] not in ids:
                    fail(f"{name} contains unresolved or external url() reference: {raw_ref}")
            href_refs = re.findall(r"\b(?:href|xlink:href)\s*=\s*[\"']([^\"']+)[\"']", text)
            for ref in href_refs:
                if not ref.startswith("#") or ref[1:] not in ids:
                    fail(f"{name} contains unresolved or external href reference: {ref}")
            if re.search(r"(?i)claude|anthropic|generated with|co-authored-by", text) or EMOJI.search(text):
                fail(f"{name} contains attribution or emoji")
            if element_signature(root) != element_signature(english_root):
                fail(f"{name} changed SVG structure or coordinates")
            if suffix in (".ko", ".ja"):
                desc_text = next((element.text or "" for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "desc"), "")
                if desc_text != LOCALIZED_DESCS[(stem, suffix)]:
                    fail(f"{name} has an untranslated or unexpected localized desc")
                if stem == "repository-roles":
                    title_text = next((element.text or "" for element in root.iter() if element.tag.rsplit("}", 1)[-1] == "title"), "")
                    if title_text != LOCALIZED_TITLES[(stem, suffix)]:
                        fail(f"{name} has an untranslated or unexpected localized title")
            if stem == "request-flow":
                for identifier in ("NoteController", "NoteApiController", "NoteService", "NoteRepository"):
                    if identifier not in text:
                        fail(f"{name} lacks exact source identifier: {identifier}")
            if stem == "request-flow" and suffix == ".ko":
                if "or form submit" in text or "Controller → service → repository keeps responsibilities explicit" in text:
                    fail(f"{name} retains untranslated English prose")
                if "또는 폼 제출" not in text or "컨트롤러 → 서비스 → 리포지토리로 책임을 분명하게 유지" not in text:
                    fail(f"{name} lacks the approved Korean prose")
            if stem == "request-flow" and suffix == ".ja":
                if "or form submit" in text or "Controller → service → repository keeps responsibilities explicit" in text:
                    fail(f"{name} retains untranslated English prose")
                if "またはフォーム送信" not in text or "コントローラ → サービス → リポジトリで責務を明確にする" not in text:
                    fail(f"{name} lacks the approved Japanese prose")
            if stem == "repository-roles":
                if SOURCE_BASELINE[:8] in text or "main → mirror" not in text:
                    fail(f"{name} contains a stale fixed commit instead of the moving main mirror")
            if stem == "application-architecture":
                if "Note(title, content, color)" not in text:
                    fail(f"{name} omits the Note color field")
                if any(term in text for term in ("in-memory persistence", "인메모리 영속성", "インメモリ永続化")):
                    fail(f"{name} misstates the H2 data store as persistence")
                expected_store = {"": "H2 in-memory data store", ".ko": "H2 인메모리 데이터 저장소", ".ja": "H2 インメモリデータストア"}[suffix]
                if expected_store not in text:
                    fail(f"{name} lacks the approved H2 data-store label")
            if stem == "demo-scenarios" and suffix == ".ja":
                if "requirements.md" not in text or "要件.md" in text:
                    fail(f"{name} does not preserve the requirements.md filename")
    if len(list(SVG_DIR.glob("*.svg"))) != 12:
        fail("SVG directory must contain exactly 12 files")


def check_files() -> None:
    required = ["README.md", "README.ko.md", "README.ja.md", "LICENSE", "CONTRIBUTING.md", ".editorconfig", ".gitignore", "README_STRUCTURE.md", "verify.py", "gitea-settings.json", "apply-gitea-settings.sh", "DEMO.ko.md", "DEMO.ja.md"]
    for rel in required:
        text = read(ROOT / rel)
        if EMOJI.search(text) or EMAIL.search(text):
            fail(f"forbidden character in {rel}")
    preserved_readme = (ROOT / "docs/README.original.en.md").read_bytes()
    if hashlib.sha256(preserved_readme).hexdigest() != SOURCE_README_SHA256:
        fail("original README copy has an unexpected SHA-256")
    if SOURCE.is_dir():
        if preserved_readme != (SOURCE / "README.md").read_bytes():
            fail("original README copy is not byte-identical")
        if not (ROOT / ".gitignore").read_bytes().startswith((SOURCE / ".gitignore").read_bytes()):
            fail(".gitignore source prefix is not preserved")
    structure = read(ROOT / "README_STRUCTURE.md")
    structure_facts = (
        f"Original GitHub source baseline: `{SOURCE_BASELINE}`; current repository tip: the commit referenced by `main`",
        "same four fenced code blocks byte-for-byte",
        "Controller route set: 11 method/path pairs, including `POST /notes/{id}/delete`",
        "all four tools use the same model so the comparison isolates differences in the agent harness",
        "multi-file editing, database schema changes, service splitting, Thymeleaf UI changes, and a breaking REST API change",
        "`docs/README.original.en.md`",
        "`CONTRIBUTING.md` and Gitea Issues",
        *AUTOMATION_FACTS,
        "Gitea Actions disabled",
    )
    for value in structure_facts:
        if value not in structure:
            fail(f"README_STRUCTURE.md missing fact: {value}")
    settings = json.loads((ROOT / "gitea-settings.json").read_text(encoding="utf-8"))
    if settings["repo"] != "seon-labs/agentic-ide-demo" or settings["units"]["has_actions"] is not False:
        fail("unexpected Gitea settings")


def check_stats_service() -> None:
    relative_path = Path("src/main/kotlin/com/seonology/demo/stats/StatsService.kt")
    if CURRENT_SOURCE is None:
        return
    service_path = CURRENT_SOURCE / relative_path
    if not service_path.is_file():
        fail(f"missing StatsService source: {relative_path}")
    text = service_path.read_text(encoding="utf-8")
    match = re.search(r"data class StatsSummary\((.*?)\n\)", text, flags=re.DOTALL)
    if not match:
        fail("StatsSummary declaration not found")
    fields = tuple(re.findall(r"\bval\s+(\w+)\s*:", match.group(1)))
    if fields != STATS_FIELDS:
        fail(f"StatsSummary fields differ: {fields!r}")
    expected_return = "return StatsSummary(total = notes.size, today = todayCount, byColor = byColor)"
    if expected_return not in text:
        fail("StatsService return mapping differs from the documented fields")
    if re.search(r"(?i)word(?:count|s)?", text):
        fail("StatsService unexpectedly contains word-count logic")


def check_source() -> None:
    if not (SOURCE / ".git").exists():
        return
    result = subprocess.run(["git", "-C", str(SOURCE), "status", "--porcelain"], capture_output=True, text=True, check=False)
    if result.returncode != 0 or result.stdout.strip():
        fail(f"source is not clean: {result.stdout.strip()!r}")


if __name__ == "__main__":
    try:
        check_readmes(); check_svg(); check_files(); check_stats_service(); check_source()
        print("SUMMARY: ALL PASS")
    except (AssertionError, ET.ParseError) as exc:
        print(f"SUMMARY: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
