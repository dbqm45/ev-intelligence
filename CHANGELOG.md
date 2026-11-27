# Changes in EV Intelligence

Format: newest version on top ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/), [SemVer](https://semver.org/)).
Entries are generated from Conventional Commits by `scripts/release.py` (docs/RELEASING.md).

## [0.1.16] — 2026-11-27
### Added
- **hardware:** add connector types across OCPP 2.1 and OCPI, Device Model components

## [0.1.15] — 2026-11-27
### Added
- **compliance:** add USA NEVI 23 CFR 680 and NIST HB44 3.40

## [0.1.14] — 2026-11-27
### Added
- **taxonomy:** add USA scope (NEVI, NIST HB44) to D12.06 in 1.3.0

## [0.1.13] — 2026-11-18
### Fixed
- **kb:** scope OCPP block-letter section tags to their block

## [0.1.12] — 2026-11-18
### Added
- **integration:** add end-to-end OCPP transaction to OCPI Session and CDR

## [0.1.11] — 2026-11-18
### Added
- **integration:** add what does not move by itself in CSMS migration

## [0.1.10] — 2026-11-18
### Added
- **compliance:** add Polish electromobility act articles and AFIR targets

## [0.1.9] — 2026-11-18
### Added
- **ocpi:** add Sessions, CDR, Tokens and Payments module mechanics

## [0.1.8] — 2026-11-15
### Added
- **billing:** add OCPI tariff calculator and pack-ev pricing knowledge
- **ocpi:** merge pack-ev OCPI and OICP knowledge into ev-ocpi-roaming-expert
- **diagnostics:** add OCPP log sequence and timing analyzer
- **ocpp:** add 1.6 status transitions, boot and stop rules, Device Model reports
### Fixed
- **sources:** PSD2 is registered, keep only PCI DSS as unavailable

## [0.1.7] — 2026-11-08
### Fixed
- **billing:** name TxResumed in interrupted session reference

## [0.1.6] — 2026-11-08
### Added
- **billing:** add ad hoc payment and interrupted session references

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
