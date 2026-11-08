# Changes in EV Intelligence

Format: newest version on top ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), [SemVer](https://semver.org/)).
Entries are generated from Conventional Commits by `scripts/release.py` (docs/RELEASING.md).

## [0.1.5] — 2026-11-08
### Added
- **taxonomy:** resolve open boundaries and add station migration subdomain (1.2.0)
### Fixed
- **ocpp:** fill gaps from the second holdout audit

## [0.1.4] — 2026-11-08
### Added
- **taxonomy:** assign skill owners to subdomains (taxonomy 1.1.0)
### Fixed
- **skills:** fill content gaps found by the holdout audit
- **skills:** split testing scope between integration and diagnostics

## [0.1.3] — 2026-11-08
### Added
- **eval:** add dev set and routing-only mode to the evaluation runner
### Fixed
- **skills:** restore market data phrase in product designer description
- **skills:** widen cpms and product descriptions after the dev routing run

## [0.1.2] — 2026-11-08
### Fixed
- **operations:** add Faulted status as an alarm source in OCPP 2.0.1
- **skills:** fix misrouting and brittle checks from the remaining-skills run

## [0.1.1] — 2026-11-07
### Added
- **eval:** add CLI backend so evaluation runs without an API key
- **eval:** add own model evaluation runner independent of tf
### Fixed
- **skills:** restore description phrases lost in the first fix
- **skills:** widen descriptions that misrouted in the Opus evaluation

## [0.1.0] — 2026-11-07
First versioned release of the knowledge base.
### Added
- 13 skills `ev-*` with citations checked against the source registry (`sources/*.yaml`)
- source registry with SHA-256, licences and the register of unavailable documents (`sources/niedostepne.yaml`)
- `tools/ev_kb.py` (route, search, cite, check, index) and the MCP server `tools/ev_kb_mcp.py` with deployment files
- confidential-source tier with verdict-only checks (`tools/ev_kb_poufne.py`, `ev_confidential_check`)
