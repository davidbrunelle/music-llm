#!/usr/bin/env python3
"""Convert a PDF manual to clean markdown for use as a wiki reference page."""

import re
import sys
from collections import Counter
from datetime import date
from pathlib import Path

try:
    import fitz  # pymupdf
except ImportError:
    print("Error: pymupdf is required. Install with: pip install pymupdf", file=sys.stderr)
    sys.exit(1)


# ── Helpers ──────────────────────────────────────────────────────────────────

def is_toc_entry(text: str) -> bool:
    """Dot-leader lines or space-separated page number columns."""
    if text.count(".") > 8:
        return True
    # Lines that are just "Chapter Title  ....... 42" or "1.2  Title   12"
    if re.search(r"\s{3,}\d+\s*$", text) and len(text) < 120:
        return True
    return False


def is_doi_or_pagenum(text: str) -> bool:
    stripped = text.strip()
    if re.fullmatch(r"\d+", stripped):
        return True
    if re.match(r"https?://doi\.org/", stripped):
        return True
    return False


def is_figure_caption(text: str, size: float, body_size: float) -> bool:
    return size < body_size * 0.95 and bool(re.match(r"FIGURE\s+\d", text.strip(), re.IGNORECASE))


def heading_level(size: float, body_size: float) -> int:
    ratio = size / body_size
    if ratio > 1.8:
        return 1
    if ratio > 1.2:
        return 2
    if ratio > 1.05:
        return 3
    return 0


# ── Block extraction ──────────────────────────────────────────────────────────

def extract_blocks(doc) -> list[dict]:
    """Extract all text blocks with size, y-position, and page info."""
    blocks = []
    for page in doc:
        page_height = page.rect.height
        raw = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)
        for block in raw.get("blocks", []):
            if block.get("type") != 0:  # skip images
                continue
            y0 = block["bbox"][1]
            # Strip running headers/footers near page edges
            if y0 < page_height * 0.08 or y0 > page_height * 0.94:
                continue

            for line in block.get("lines", []):
                spans = line.get("spans", [])
                if not spans:
                    continue
                text = "".join(s["text"] for s in spans).replace("\xad", "")
                text = text.strip()
                if not text:
                    continue
                size = round(spans[0]["size"], 1)
                blocks.append({"text": text, "size": size, "y": y0})

    return blocks


def detect_body_size(blocks: list[dict]) -> float:
    sizes = [b["size"] for b in blocks]
    if not sizes:
        return 11.0
    counter = Counter(sizes)
    return counter.most_common(1)[0][0]


def split_mixed_blocks(blocks: list[dict], body_size: float) -> list[dict]:
    """
    If a block contains text at a heading size followed by body-size text,
    split it so the heading doesn't absorb the paragraph.
    This is already handled by line-level extraction above, but we keep this
    as a no-op pass in case future extraction changes.
    """
    return blocks


# ── Rendering ────────────────────────────────────────────────────────────────

def render_markdown(blocks: list[dict], body_size: float, title: str) -> str:
    lines = []
    prev_was_heading = False

    for block in blocks:
        text = block["text"]
        size = block["size"]

        if is_doi_or_pagenum(text):
            continue
        if is_toc_entry(text):
            continue

        level = heading_level(size, body_size)

        if is_figure_caption(text, size, body_size):
            lines.append(f"*{text}*")
            lines.append("")
            prev_was_heading = False
            continue

        if level > 0:
            prefix = "#" * level
            if lines and not prev_was_heading:
                lines.append("")
            lines.append(f"{prefix} {text}")
            lines.append("")
            prev_was_heading = True
        else:
            lines.append(text)
            lines.append("")
            prev_was_heading = False

    # Collapse runs of blank lines to a single blank
    result = []
    blank_run = 0
    for line in lines:
        if line == "":
            blank_run += 1
            if blank_run == 1:
                result.append("")
        else:
            blank_run = 0
            result.append(line)

    return "\n".join(result).strip()


# ── Main ──────────────────────────────────────────────────────────────────────

def pdf_to_markdown(input_path: str, output_path: str) -> None:
    src = Path(input_path)
    dst = Path(output_path)

    if not src.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    doc = fitz.open(str(src))
    title = src.stem.replace("-", " ").replace("_", " ").title()

    blocks = extract_blocks(doc)
    body_size = detect_body_size(blocks)
    blocks = split_mixed_blocks(blocks, body_size)

    body = render_markdown(blocks, body_size, title)

    today = date.today().isoformat()
    # Infer slug-based name for type field
    slug = dst.stem
    frontmatter = f"""---
title: {title}
type: manual
tags: []
created: {today}
updated: {today}
---

"""

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(frontmatter + body, encoding="utf-8")
    print(f"Written: {dst}  ({len(blocks)} blocks, body size {body_size}pt)")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pdf_to_markdown.py <input.pdf> <output.md>", file=sys.stderr)
        sys.exit(1)
    pdf_to_markdown(sys.argv[1], sys.argv[2])
