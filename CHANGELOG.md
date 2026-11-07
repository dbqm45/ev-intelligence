# Changes in EV Intelligence

Format: newest version on top ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), [SemVer](https://semver.org/)).
Entries are generated from Conventional Commits by `scripts/release.py` (docs/RELEASING.md).

## [0.1.0] — 2026-11-07
First versioned release of the knowledge base.
### Added
- 13 skills `ev-*` with citations checked against the source registry (`sources/*.yaml`)
- source registry with SHA-256, licences and the register of unavailable documents (`sources/niedostepne.yaml`)
- `tools/ev_kb.py` (route, search, cite, check, index) and the MCP server `tools/ev_kb_mcp.py` with deployment files
- confidential-source tier with verdict-only checks (`tools/ev_kb_poufne.py`, `ev_confidential_check`)
