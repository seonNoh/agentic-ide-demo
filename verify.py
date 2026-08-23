#!/usr/bin/env python3
"""Offline checks for the agentic-ide-demo migration deliverables."""

from __future__ import annotations

from collections import Counter
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "source"
SVG_DIR = ROOT / "docs" / "svg"
README_NAMES = ("README.md", "README.ko.md", "README.ja.md")
SVG_SPECS = {
    "application-architecture": ("960", "540", "aa"),
    "request-flow": ("960", "540", "rf"),
    "demo-scenarios": ("960", "540", "ds"),
    "repository-roles": ("640", "420", "gd"),
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


def check_readmes() -> None:
    texts = {name: read(ROOT / name) for name in README_NAMES}
    expected = {
        "README.md": ["# agentic-ide-demo", "## Overview", "## Repository layout", "## Quick start", "## Application structure", "## Demo scenarios", "## HTTP endpoints", "## GitHub and Gitea", "## Operations", "## Related"],
        "README.ko.md": ["# agentic-ide-demo", "## 개요", "## 저장소 구조", "## 빠른 시작", "## 애플리케이션 구조", "## 데모 시나리오", "## HTTP 엔드포인트", "## GitHub와 Gitea", "## 운영", "## 관련 자료"],
        "README.ja.md": ["# agentic-ide-demo", "## 概要", "## リポジトリ構成", "## すぐに始める", "## アプリケーション構成", "## デモシナリオ", "## HTTP エンドポイント", "## GitHub と Gitea", "## 運用", "## 関連資料"],
    }
    switcher = "[English](README.md) | [한국어](README.ko.md) | [日本語](README.ja.md)"
    required = ("https://git.seonology.com/seon-labs/agentic-ide-demo", "https://github.com/seonNoh/agentic-ide-demo", "Kotlin 1.9", "Java 21", "Spring Boot 3.5", "b1dd56bc2045d54a4f1af43958753843e38be883", "NoteService", "NoteApiController", "StatsService")
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
            if re.search(r"(?i)claude|anthropic|generated with|co-authored-by", text) or EMOJI.search(text):
                fail(f"{name} contains attribution or emoji")
            if element_signature(root) != element_signature(english_root):
                fail(f"{name} changed SVG structure or coordinates")
    if len(list(SVG_DIR.glob("*.svg"))) != 12:
        fail("SVG directory must contain exactly 12 files")


def check_files() -> None:
    required = ["README.md", "README.ko.md", "README.ja.md", "LICENSE", "CONTRIBUTING.md", ".editorconfig", ".gitignore", "README_STRUCTURE.md", "verify.py", "gitea-settings.json", "apply-gitea-settings.sh", "DEMO.ko.md", "DEMO.ja.md"]
    for rel in required:
        text = read(ROOT / rel)
        if EMOJI.search(text) or EMAIL.search(text):
            fail(f"forbidden character in {rel}")
    if (ROOT / "docs/README.original.en.md").read_bytes() != (SOURCE / "README.md").read_bytes():
        fail("original README copy is not byte-identical")
    if not (ROOT / ".gitignore").read_bytes().startswith((SOURCE / ".gitignore").read_bytes()):
        fail(".gitignore source prefix is not preserved")
    settings = json.loads((ROOT / "gitea-settings.json").read_text(encoding="utf-8"))
    if settings["repo"] != "seon-labs/agentic-ide-demo" or settings["units"]["has_actions"] is not False:
        fail("unexpected Gitea settings")


def check_source() -> None:
    result = subprocess.run(["git", "-C", str(SOURCE), "status", "--porcelain"], capture_output=True, text=True, check=False)
    if result.returncode != 0 or result.stdout.strip():
        fail(f"source is not clean: {result.stdout.strip()!r}")


if __name__ == "__main__":
    try:
        check_readmes(); check_svg(); check_files(); check_source()
        print("SUMMARY: ALL PASS")
    except (AssertionError, ET.ParseError) as exc:
        print(f"SUMMARY: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
