---
name: process-reference
description: Use this skill when the user runs /process-reference or asks to process, convert, or import PDFs from the wiki inbox into the wiki. Handles PDF-to-markdown conversion, front-matter, index.md, and log.md updates.
version: 0.1.0
---

# Process Reference PDFs

You are helping David convert PDF reference manuals from the wiki inbox into indexed wiki pages.

## Step 1 — Locate the inbox

Read `config.yaml` in the repo root to get `wiki_path`. The inbox is at `{wiki_path}/inbox/`.

List all `.pdf` files in the inbox:
```bash
find "{wiki_path}/inbox" -maxdepth 1 -iname "*.pdf" | sort
```

If no PDFs are found, tell the user the inbox is empty and show the path. Stop.

Before listing the PDFs to the user, filter out any that have already been processed. A PDF is considered already processed if its inferred slug already appears as a wikilink in `{wiki_path}/index.md` (i.e. `[[manuals/{slug}]]` is present in that file). Derive the slug from each PDF filename the same way Step 2 does — strip the extension and convert to kebab-case.

Read `{wiki_path}/index.md` and check each PDF's slug against the wikilinks present under `## Manuals`. Silently exclude already-processed PDFs from the candidate list (do not mention them unless the user asks).

If all PDFs in the inbox are already processed, tell the user the inbox has no new manuals to import and stop.

If some PDFs are new, list only those and confirm with the user which ones to process. Default is all new ones.

## Step 2 — For each PDF, gather metadata

For each PDF to process, present what you can infer from the filename, then ask the user to confirm or override:

- **Title** — human-readable, e.g. "Komplete Kontrol Manual"
- **Slug** — kebab-case filename without extension, e.g. `komplete-kontrol` (this becomes the output file name under `{wiki_path}/manuals/`)
- **Description** — one line for the index entry, e.g. "Native Instruments Komplete Kontrol hardware manual"
- **Tags** — comma-separated, e.g. `native-instruments, hardware, keyboard`

Batch these into a single message per PDF rather than asking one question at a time. Show your inferred values so the user only needs to correct what's wrong.

## Step 3 — Run the conversion

For each PDF, run:
```bash
python scripts/pdf_to_markdown.py "{wiki_path}/inbox/filename.pdf" "{wiki_path}/manuals/{slug}.md"
```

Run from the music-llm repo root (where `scripts/` lives).

If the script fails, show the error and ask the user whether to skip or retry with a different output path.

## Step 4 — Fix up front-matter

The script writes basic front-matter. Open the generated `.md` file and update the front-matter to match the confirmed metadata:

```yaml
---
title: {confirmed title}
type: manual
tags: [{tag1}, {tag2}, ...]
source_pdf: {original pdf filename}
created: {today's date YYYY-MM-DD}
updated: {today's date YYYY-MM-DD}
---
```

Preserve the rest of the file content exactly.

## Step 5 — Update index.md

Read `{wiki_path}/index.md`. Add a new line under the `## Manuals` section:

```
- [[manuals/{slug}]] — {description}
```

Keep the list alphabetical within the section if possible.

## Step 6 — Update log.md

Read `{wiki_path}/log.md`. Append a new entry above the closing comment line (or at the end if no comment exists):

```markdown
## {today's date YYYY-MM-DD}

- **{title}** (`manuals/{slug}`) — {description}
  - Source: `inbox/{original filename}`
  - Tags: {tags}
```

Update the `updated:` field in the log.md front-matter to today's date.

## Step 7 — Report and suggest cleanup

After all PDFs are processed:
1. Show a summary table: PDF → wiki page → index entry added
2. Ask the user if they want to delete the source PDFs from the inbox now, or keep them

If they say yes to deletion, run:
```bash
rm "{wiki_path}/inbox/{filename}.pdf"
```
One file at a time, confirming each if there are more than 3.

## Notes

- Never truncate or summarize the converted markdown content — the full text is needed for future grep searches
- If a manual for the same slug already exists, warn the user before overwriting
- The output path is always `{wiki_path}/manuals/{slug}.md` — never put it elsewhere
