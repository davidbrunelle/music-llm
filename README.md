# Music Production Wiki LLM

A personal knowledge system for music production and DJing. Claude acts as an informed assistant across sessions, drawing on a structured wiki of reference material, personal gear notes, session logs, and technique documentation.

Inspired by [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): rather than re-retrieving raw sources on every query, Claude maintains a structured, interlinked wiki that compounds over time.

---

## How It Works

- The **wiki** is a folder of Obsidian-compatible markdown files stored separately from this repo
- This repo contains the **scripts** that operate on the wiki and the **CLAUDE.md** that orients Claude at the start of each session
- Claude reads `config.yaml` to find the wiki, then reads `wiki/index.md` to know what's available before answering questions

---

## Setup

1. Copy the example config and set your wiki path:
   ```bash
   cp config.example.yaml config.yaml
   # edit config.yaml and set wiki_path
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Open Claude Code in this directory. Claude will read `CLAUDE.md` automatically.

---

## Directory Structure

```
music-llm/                        ← This repo
├── CLAUDE.md                     ← Session orientation for Claude
├── config.yaml                   ← Git-ignored; sets wiki_path
├── config.example.yaml           ← Tracked template
├── requirements.txt              ← pymupdf
├── scripts/
│   ├── parse_als.py              ← Ableton project parser
│   └── pdf_to_markdown.py        ← PDF to wiki markdown converter
└── .claude/
    ├── settings.json             ← Project permissions and hooks
    ├── skills/                   ← Custom slash commands
    ├── rules/                    ← Path-scoped session instructions
    ├── agents/                   ← Subagent definitions
    └── output-styles/            ← Custom response modes

music-wiki/                       ← Wiki vault (separate, set in config.yaml)
├── index.md                      ← Master index — Claude checks this first
├── manuals/                      ← Converted PDF reference manuals
├── reference/                    ← Technical docs (ALS format, etc.)
├── gear/                         ← Studio setup and hardware inventory
├── techniques/                   ← Production techniques and lessons learned
└── sessions/                     ← Per-session notes and project logs
```

---

## Scripts

### `parse_als.py` — Ableton project parser

Parses a `.als` file and prints a structured project summary: tempo, key, time signature, track listing with device chains, Drum Rack pad contents, MIDI clips, and audio clips.

```bash
python scripts/parse_als.py "path/to/Project.als"
```

### `pdf_to_markdown.py` — PDF to wiki markdown

Converts a PDF manual to clean markdown with YAML frontmatter, suitable for dropping into `wiki/manuals/`.

```bash
python scripts/pdf_to_markdown.py "input.pdf" "/path/to/wiki/manuals/name.md"
```

---

## Typical Workflows

**Starting a session**
Open Claude Code here. Claude reads `CLAUDE.md`, loads `config.yaml` to find the wiki, then reads `wiki/index.md`. Describe what you're working on.

**Answering a production question**
Claude greps `wiki/manuals/` for relevant terms, cross-references `wiki/techniques/`, and gives advice specific to your gear — not generic DAW advice.

**Analysing an Ableton project**
Ask Claude to run `parse_als.py` on your `.als` file. It will output a structural summary of the set that Claude can reason about.

**Adding a reference manual**
Drop the PDF into the vault folder, run `pdf_to_markdown.py`, then ask Claude to add an entry to `wiki/index.md`.

**After a session**
Ask Claude to write a session note. It will run `parse_als.py` to capture project state and write `wiki/sessions/YYYY-MM-DD-project-name.md` using the template at `wiki/sessions/session-template.md`.

---

## Wiki Page Types

| Directory | Contents |
|---|---|
| `manuals/` | Converted PDF reference docs — grep, don't read whole files |
| `reference/` | Technical documentation (file formats, XML structure, gotchas) |
| `gear/` | Hardware inventory, signal flow, software versions |
| `techniques/` | Production techniques in first person — the why alongside the how |
| `sessions/` | Per-session notes with project state, what worked, what didn't |
