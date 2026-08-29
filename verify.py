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
ACTIVE_SVG_DIR = ROOT / "docs" / "readme"
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
        "에이전트 하네스의 차이를 보여 준다",
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
    "project-overview": ("960", "540", "po"),
    "repository-structure": ("960", "540", "rs"),
    "request-flow": ("960", "540", "rf"),
    "configuration-structure": ("960", "540", "cs"),
    "demo-scenarios": ("960", "540", "ds"),
    "application-architecture": ("960", "540", "aa"),
}
LEGACY_SVG_SHA256 = {
    "application-architecture.ja.svg": "f08b3e526336bbc8ce37732652563f6a0686bbaa172bdb7c4cde5904f02f211a",
    "application-architecture.ko.svg": "9ba70bf7755e1b7583d311b3728054ad9aa532886c91b559ce6edb3ebd1edc72",
    "application-architecture.svg": "d3902fed176ffa2189d636d02bd371f9b73b7bcb2293875653985c8a51d36fb0",
    "demo-scenarios.ja.svg": "7fe5d31c2d97947088857ed72ecf631b1bcdebd3bb6e3de71b54b83f4a969b5a",
    "demo-scenarios.ko.svg": "f8929ba85d9fde99d713a822a7cffcf41d8d704cefecd41265dd5cd34de63799",
    "demo-scenarios.svg": "4059ec344ab43808c6545f7eecc803cf28c4c04d951875d92b1a68e2e06a408a",
    "repository-roles.ja.svg": "e6a704bfca74600e0f227cbcda38baac8b395e8ea934ed5d5bb4602ced31cb76",
    "repository-roles.ko.svg": "81f1f316a8da7211ef88eb1c75c0426913c8326b510b255f1c8366f844e93cf9",
    "repository-roles.svg": "938499a16bdfaf09e5eede66be6bf129b8cd6a1c6ac8127693814b57ef5cf234",
    "request-flow.ja.svg": "43dd27c53250d2ba6e0fc61b95aecd007bcb9f71499be0060efb48d6ae5c6b6d",
    "request-flow.ko.svg": "011ecec2a69288644781a04e63cf6c38a32cfa4d59e17578aeb31ccbff9dc0bb",
    "request-flow.svg": "8756f2a563de01d7bbb710b190ac2b89662d7ea70544e9e63a8d4caf643f2ab5",
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
        "README.md": ["# agentic-ide-demo", "## Overview", "## Repository layout", "## Quick start", "## Build and deployment", "## Request flow", "## Configuration", "## Security and secrets", "## Concept map", "## Application architecture", "## HTTP endpoints", "## GitHub and Gitea", "## Operations", "## Related"],
        "README.ko.md": ["# agentic-ide-demo", "## 개요", "## 저장소 구조", "## 빠른 시작", "## 빌드 및 배포", "## 요청 흐름", "## 설정", "## 보안 및 시크릿", "## 개념도", "## 애플리케이션 아키텍처", "## HTTP 엔드포인트", "## GitHub와 Gitea", "## 운영", "## 관련 경로"],
        "README.ja.md": ["# agentic-ide-demo", "## 概要", "## リポジトリ構成", "## クイックスタート", "## ビルドとデプロイ", "## リクエストフロー", "## 設定", "## セキュリティとシークレット", "## 概念図", "## アプリケーションアーキテクチャ", "## HTTP エンドポイント", "## GitHub と Gitea", "## 運用", "## 関連パス"],
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
            if value.lower() not in text.lower():
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
        language = {"README.md": "en", "README.ko.md": "ko", "README.ja.md": "ja"}[name]
        images = re.findall(r"!\[[^]]*\]\(([^)]+)\)", text)
        expected_images = [f"docs/readme/{language}/{stem}.svg" for stem in SVG_SPECS]
        if len(images) != 6 or set(images) != set(expected_images):
            fail(f"{name} diagram references differ: {images!r}")
    fences = code_fences(texts["README.md"])
    if len(fences) != 4:
        fail(f"English README has {len(fences)} fenced blocks, expected 4")
    for name in README_NAMES[1:]:
        if code_fences(texts[name]) != fences:
            fail(f"{name} fenced code blocks differ byte-for-byte")
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
        english = read(ACTIVE_SVG_DIR / "en" / f"{stem}.svg")
        english_root = ET.fromstring(english)
        for language in ("en", "ko", "ja"):
            name = f"{language}/{stem}.svg"
            text = read(ACTIVE_SVG_DIR / name)
            root = ET.fromstring(text)
            if root.attrib.get("viewBox") != f"0 0 {width} {height}":
                fail(f"{name} has unexpected viewBox")
            required_style = ("<style", "<defs", "prefers-reduced-motion", "prefers-color-scheme:light", "#0d1117", "#f6f8fa", "@keyframes", "rx=\"12\"")
            if any(token not in text for token in required_style):
                fail(f"{name} does not implement the self-contained Relief theme")
            if '"Pretendard",system-ui,sans-serif' not in text:
                fail(f"{name} has altered font fallback")
            if any(token in text.lower() for token in TAILWIND):
                fail(f"{name} contains forbidden palette token")
            ids = re.findall(r'\bid="([^"]+)"', text)
            if len(ids) != len(set(ids)):
                fail(f"{name} contains duplicate IDs")
            variant_prefix = f"{prefix}-{language}"
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
            if stem == "request-flow":
                for identifier in ("NoteController", "NoteApiController", "NoteService", "NoteRepository"):
                    if identifier not in text:
                        fail(f"{name} lacks exact source identifier: {identifier}")
            if text.count(f'class="{variant_prefix}-flow"') > 2:
                fail(f"{name} animates more than two flow arrows")
    active = list(ACTIVE_SVG_DIR.glob("*/*.svg"))
    if len(active) != 18:
        fail(f"active README SVG directory must contain exactly 18 files, found {len(active)}")
    for filename, expected_hash in LEGACY_SVG_SHA256.items():
        actual_hash = hashlib.sha256((SVG_DIR / filename).read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            fail(f"preserved SVG changed: {filename}")


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
