from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
import re
import sys


DEFAULT_PATHS = (
    "README.md",
    "dnd_game",
    "information/Story",
)
DEFAULT_SUFFIXES = {".md", ".py", ".txt"}
EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    "tests",
    "tests_output",
    "saves",
    "sim_saves",
    "android_port",
}
ALLOW_DIRECTIVE = "prose-lint: allow"

BANNED_PHRASES = (
    "not just",
    "not merely",
    "not only",
    "in truth",
    "at its core",
    "the real",
)
CONTRASTIVE_THESIS_RE = re.compile(
    r"\b(?:it\s+is|it's)\s+not\b[^.\n;]{0,140}\b(?:it\s+is|it's)\b",
    re.IGNORECASE,
)

LEGACY_TERMS = {
    "Agatha": "Pale Witness",
    "Barthen": "Hadrik",
    "Conyberry": "Hushfen",
    "Cragmaw": "Ashen Brand",
    "Daran Edermath": "Daran Orchard",
    "Forge of Spells": "Meridian Forge",
    "Halia Thornton": "Halia Vey",
    "High Road": "Emberway",
    "Linene Graywind": "Linene Ironward",
    "Mara Stonehill": "Mara Ashlamp",
    "Neverwinter": "Greywake",
    "Old Owl Well": "Blackglass Well",
    "Phandalin": "Iron Hollow",
    "Phandelver": "Aethrune",
    "Shrine of Tymora": "Wayside Luck Shrine",
    "Stonehill Inn": "Ashlamp Inn",
    "Sword Coast": "Shatterbelt Frontier",
    "Tresendar": "Duskmere",
    "Tymora": "the Lantern",
    "Wave Echo": "Resonant Vaults",
    "Wyvern Tor": "Red Mesa Hold",
}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    column: int
    code: str
    message: str
    excerpt: str


def line_is_allowed(line: str) -> bool:
    return ALLOW_DIRECTIVE in line


def term_pattern(term: str) -> re.Pattern[str]:
    escaped = re.escape(term)
    if re.search(r"\W", term):
        return re.compile(rf"(?<![A-Za-z0-9_]){escaped}(?![A-Za-z0-9_])", re.IGNORECASE)
    return re.compile(rf"\b{escaped}\b", re.IGNORECASE)


LEGACY_PATTERNS = {
    term: term_pattern(term)
    for term in sorted(LEGACY_TERMS, key=len, reverse=True)
}


def looks_like_internal_token(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    if re.fullmatch(r"[a-z0-9_./\\:-]+", stripped):
        return True
    if stripped.startswith(("quest_", "act", "camp_", "dialogue_input_")):
        return True
    return False


def lint_line(path: Path, line_number: int, line: str, *, checks: set[str]) -> list[Finding]:
    if line_is_allowed(line):
        return []
    findings: list[Finding] = []
    if "style" in checks:
        match = CONTRASTIVE_THESIS_RE.search(line)
        if match is not None:
            findings.append(
                Finding(
                    path,
                    line_number,
                    match.start() + 1,
                    "STYLE001",
                    "Replace the contrastive thesis pattern with a direct statement.",
                    line.strip(),
                )
            )
        lowered = line.lower()
        for phrase in BANNED_PHRASES:
            index = lowered.find(phrase)
            if index >= 0:
                findings.append(
                    Finding(
                        path,
                        line_number,
                        index + 1,
                        "STYLE002",
                        f"Rewrite banned phrase: {phrase!r}.",
                        line.strip(),
                    )
                )
    if "legacy" in checks:
        for term, pattern in LEGACY_PATTERNS.items():
            match = pattern.search(line)
            if match is None:
                continue
            replacement = LEGACY_TERMS[term]
            findings.append(
                Finding(
                    path,
                    line_number,
                    match.start() + 1,
                    "LEGACY001",
                    f"Legacy public term {term!r} found; prefer {replacement!r}.",
                    line.strip(),
                )
            )
    return findings


def lint_text(
    text: str,
    *,
    path: Path = Path("<text>"),
    checks: Iterable[str] = ("style", "legacy"),
    starting_line: int = 1,
) -> list[Finding]:
    enabled_checks = set(checks)
    findings: list[Finding] = []
    for offset, line in enumerate(text.splitlines(), start=0):
        findings.extend(lint_line(path, starting_line + offset, line, checks=enabled_checks))
    return findings


def lint_python_file(path: Path, *, checks: Iterable[str]) -> list[Finding]:
    source = path.read_text(encoding="utf-8")
    source_lines = source.splitlines()
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return [
            Finding(
                path,
                exc.lineno or 1,
                exc.offset or 1,
                "PYTHON001",
                f"Could not parse Python file: {exc.msg}.",
                (exc.text or "").strip(),
            )
        ]

    findings: list[Finding] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        if looks_like_internal_token(node.value):
            continue
        source_line = source_lines[node.lineno - 1] if 0 <= node.lineno - 1 < len(source_lines) else ""
        if line_is_allowed(source_line):
            continue
        findings.extend(
            lint_text(
                node.value,
                path=path,
                checks=checks,
                starting_line=node.lineno,
            )
        )
    return findings


def should_scan(path: Path) -> bool:
    if any(part in EXCLUDED_PARTS for part in path.parts):
        return False
    return path.suffix.lower() in DEFAULT_SUFFIXES


def iter_scan_paths(paths: Sequence[Path]) -> Iterable[Path]:
    for path in paths:
        if path.is_dir():
            for child in path.rglob("*"):
                if child.is_file() and should_scan(child):
                    yield child
        elif path.is_file() and should_scan(path):
            yield path


def lint_path(path: Path, *, checks: Iterable[str] = ("style", "legacy")) -> list[Finding]:
    if path.suffix.lower() == ".py":
        return lint_python_file(path, checks=checks)
    return lint_text(path.read_text(encoding="utf-8"), path=path, checks=checks)


def format_finding(finding: Finding, *, root: Path) -> str:
    try:
        display_path = finding.path.resolve().relative_to(root.resolve())
    except ValueError:
        display_path = finding.path
    return (
        f"{display_path}:{finding.line}:{finding.column}: "
        f"{finding.code}: {finding.message}\n"
        f"  {finding.excerpt}"
    )


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Lint Aethrune-facing prose for style drift and legacy public terms.")
    parser.add_argument("paths", nargs="*", type=Path, help="Files or directories to scan.")
    parser.add_argument("--style-only", action="store_true", help="Check AGENTS.md writing patterns only.")
    parser.add_argument("--legacy-only", action="store_true", help="Check legacy public terms only.")
    return parser


def checks_from_args(args: argparse.Namespace) -> set[str]:
    if args.style_only and args.legacy_only:
        raise SystemExit("--style-only and --legacy-only cannot be combined.")
    if args.style_only:
        return {"style"}
    if args.legacy_only:
        return {"legacy"}
    return {"style", "legacy"}


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_argument_parser()
    args = parser.parse_args(argv)
    root = Path.cwd()
    paths = args.paths or [root / path for path in DEFAULT_PATHS]
    findings: list[Finding] = []
    checks = checks_from_args(args)
    for path in iter_scan_paths(paths):
        findings.extend(lint_path(path, checks=checks))
    for finding in findings:
        print(format_finding(finding, root=root))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
