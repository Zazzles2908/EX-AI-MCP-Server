from __future__ import annotations
import os
import re
import json
from pathlib import Path
from typing import List, Dict, Any, Tuple

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.(md|png|jpg|jpeg|gif|svg)$")
INTERNAL_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def is_http(href: str) -> bool:
    return href.startswith("http://") or href.startswith("https://")


def extract_links(md_text: str) -> List[str]:
    return [m.group(1) for m in INTERNAL_LINK_RE.finditer(md_text or "")]


def find_markdown_files(base_dir: str) -> List[Path]:
    base = Path(base_dir)
    return [p for p in base.rglob("*.md") if p.is_file()]


def is_internal(href: str) -> bool:
    if is_http(href):
        return False
    if href.startswith("#"):
        return False
    if href.startswith("mailto:"):
        return False
    return True


def check_internal_link(md_path: Path, href: str) -> Tuple[bool, str]:
    # Anchor handling: file.md#anchor
    target = href
    if "#" in href:
        target = href.split("#", 1)[0]
    target_path = (md_path.parent / target).resolve()
    return (target_path.exists(), str(target_path))


def validate_kebab_case(paths: List[Path]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    for p in paths:
        if p.name.lower() != p.name:
            issues.append({"type": "kebab_case", "path": str(p), "detail": "Filename has uppercase letters"})
            continue
        if " " in p.name or "_" in p.name:
            issues.append({"type": "kebab_case", "path": str(p), "detail": "Filename contains spaces or underscores"})
            continue
        if p.suffix.lower() in (".md", ".png", ".jpg", ".jpeg", ".gif", ".svg") and not KEBAB_RE.match(p.name):
            issues.append({"type": "kebab_case", "path": str(p), "detail": "Filename not kebab-case"})
    return issues


def validate_docs(base_dir: str) -> Dict[str, Any]:
    base = Path(base_dir)
    md_files = find_markdown_files(base_dir)
    link_issues: List[Dict[str, Any]] = []
    for md in md_files:
        text = md.read_text(encoding="utf-8", errors="ignore")
        for href in extract_links(text):
            if not is_internal(href):
                continue
            ok, resolved = check_internal_link(md, href)
            if not ok:
                link_issues.append({
                    "type": "broken_link", "file": str(md), "href": href, "resolved": resolved
                })
    name_issues = validate_kebab_case([p for p in base.rglob("*") if p.is_file()])
    return {
        "base": str(base.resolve()),
        "counts": {"markdown": len(md_files), "link_issues": len(link_issues), "name_issues": len(name_issues)},
        "link_issues": link_issues,
        "name_issues": name_issues,
        "ok": len(link_issues) == 0 and len(name_issues) == 0,
    }


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Validate docs structure and internal links")
    ap.add_argument("base", nargs="?", default="docs", help="Base docs directory (default: docs)")
    ap.add_argument("--json-out", default="", help="Optional path to write JSON report")
    args = ap.parse_args()
    report = validate_docs(args.base)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    if args.json_out:
        Path(args.json_out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json_out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    raise SystemExit(0 if report["ok"] else 2)

if __name__ == "__main__":
    main()

