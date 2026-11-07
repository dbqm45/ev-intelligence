# EV Intelligence — Knowledge & Engineering Framework

Wersjonowany, opisany źródłami system wiedzy o elektromobilności i infrastrukturze ładowania EV,
przeznaczony dla agentów AI (Claude Skills, docelowo MCP/API) i zespołów projektujących
CPMS/CSMS, integracje OCPP/OCPI, roaming, operacje CPO i rozliczenia.

Kluczowe założenia:

- **Knowledge ≠ Skills** — baza wiedzy mówi *co wiemy*, skille mówią *jak tego użyć*.
- **Każdy fakt ma źródło, wersję i poziom wiarygodności** (klasy źródeł A–D).
- **Modularne skille** ładowane kontekstowo zamiast jednego wielkiego skilla.
- **Wiedza praktyczna** (edge cases, vendor quirks, mapowania między protokołami) jako główny wyróżnik.

📄 Podsumowanie koncepcji i plan realizacji: [docs/PLAN.md](docs/PLAN.md)
📚 Mapa wiedzy (taksonomia v1.0): [taxonomy/TAXONOMY.md](taxonomy/TAXONOMY.md) · [pełne drzewo](taxonomy/TAXONOMY-TREE.md)
🧪 Budowa i walidacja skilli: [docs/SKILLS-WORKFLOW.md](docs/SKILLS-WORKFLOW.md) — `python3 tools/factory_check.py --tf ../tf`
