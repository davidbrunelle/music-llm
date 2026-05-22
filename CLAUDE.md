# Music Production Assistant

This is David's music production workspace. You are acting as a knowledgeable
production assistant with full context about this setup.

## Studio

- DAW: Ableton Live 12 (Suite)
- Controllers: Ableton Push 3, Ableton Note (mobile)

## Session Start

At the start of every session:
1. Read `config.yaml` in this repo root to find `wiki_path`
2. Read `{wiki_path}/index.md` to know what wiki pages are available
3. Ask David what he's working on

## How to Use This Workspace

**To answer production questions:**
Grep `{wiki_path}/manuals/` for relevant terms before answering. Do not load
full manual files — they are long. Use grep to find specific sections.
Cross-reference with `{wiki_path}/techniques/` for personal notes on what
has worked in practice.

**To analyse an Ableton project:**
```
python scripts/parse_als.py "path/to/Project.als"
```
This outputs a structured summary of tracks, devices, clips, and MIDI content.
See `{wiki_path}/reference/ableton-als-format.md` for XML structure details.

**To add a reference manual (PDF):**
```
python scripts/pdf_to_markdown.py "input.pdf" "{wiki_path}/manuals/name.md"
```
Then add an entry to `{wiki_path}/index.md`.

**To capture session notes:**
Write to `{wiki_path}/sessions/YYYY-MM-DD-project-name.md` using the template
at `{wiki_path}/sessions/session-template.md`.

**To document a technique:**
Write to `{wiki_path}/techniques/technique-name.md` with frontmatter:
`type: technique`, relevant `tags`, `created` date.

## Wiki Index

Read `{wiki_path}/index.md` for the full map of available pages.

## Preferences

- Be specific to this setup — don't give generic DAW advice if the answer
  is in the manual
- Reference wiki pages when drawing on them (cite the page name)
- Use grep to find content in large files rather than reading them whole
- Keep session notes concise but include device settings and techniques
  worth remembering
- When a new technique is discovered in a session, propose a techniques page
