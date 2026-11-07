#!/usr/bin/env python3
"""Ewaluacja skilli EV Intelligence na modelu Claude (płatna — tylko za zgodą człowieka; docs/SKILLS-WORKFLOW.md).

Dla każdego scenariusza z evals/skill_evals/<skill>.json (albo holdout/ z --holdout):
  1. routing — model dostaje katalog skilli (nazwa + description) i pytanie; wybiera jeden skill albo „none”
     (structured output). trigger: oczekiwany ten skill; no-trigger: każdy inny wybór niż ten skill.
  2. odpowiedź — tylko dla trigger: system = treść SKILL.md + references/ skilla, użytkownik = prompt.
     Sprawdzenia: każda grupa z checks.all musi mieć dopasowanie (dowolny wzorzec z grupy), żaden wzorzec
     z checks.none nie może pasować (wyrażenia regularne, bez rozróżniania wielkości liter).

  python3 tools/skill_eval.py --dry-run [--skills a,b]                    # bez API: liczba wywołań, rozmiar promptów
  python3 tools/skill_eval.py --model sonnet --budget 5 --yes [--skills a,b] [--holdout] [--label opis]
        [--backend cli|sdk]   # cli (domyślnie): `claude -p` z logowaniem użytkownika, bez klucza API; sdk: klucz API

Wynik: docs/evals/<data>-<model>-<label>.jsonl (rekord na scenariusz) i .md (podsumowanie). Budżet w USD liczony z
`usage` odpowiedzi i cennika niżej; przebieg zatrzymuje się, gdy go przekroczy. Zależność backendu sdk: requirements-eval.txt.
Bez fallbacku na inny model: odmowa (`stop_reason == "refusal"`) to wynik scenariusza, a nie powód zmiany modelu.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
EVALS = ROOT / "evals" / "skill_evals"
OUT = ROOT / "docs" / "evals"

MODELS = {"opus": "claude-opus-5-5", "sonnet": "claude-sonnet-5-5", "haiku": "claude-haiku-5-5"}
# USD za 1M tokenów (wejście, wyjście); zapis do cache ×1,25 ceny wejścia, odczyt ×0,1. Cennik z 2026-10-06.
PRICES = {"claude-opus-5-5": (4.00, 20.00), "claude-sonnet-5-5": (2.00, 10.00), "claude-haiku-5-5": (0.10, 0.50)}

ROUTER_SYSTEM = ("Jesteś routerem skilli bazy wiedzy EV Intelligence. Na podstawie katalogu wybierz jeden skill, który "
                 "należy wczytać, żeby odpowiedzieć na zadanie użytkownika, albo \"none\", gdy żaden skill z katalogu "
                 "nie jest właściwy. Nie odpowiadaj na samo zadanie.\n\nKatalog skilli:\n")
ANSWER_RULES = ("\n\nOdpowiadasz po polsku, zgodnie z procedurą skilla. Fakty tylko z treści skilla i jego references, "
                "ze znacznikami źródeł; czego treść nie obejmuje, mówisz wprost.")


def frontmatter(text: str) -> dict:
    import yaml
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    return (yaml.safe_load(m.group(1)) or {}) if m else {}


def catalog() -> list[dict]:
    out = []
    for p in sorted(SKILLS.glob("*/SKILL.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        out.append({"name": fm.get("name", p.parent.name), "description": str(fm.get("description", ""))})
    return out


def skill_context(name: str) -> str:
    parts = [(SKILLS / name / "SKILL.md").read_text(encoding="utf-8")]
    for ref in sorted((SKILLS / name / "references").glob("*.md")):
        parts.append(f"\n\n--- references/{ref.name} ---\n" + ref.read_text(encoding="utf-8"))
    return "".join(parts)


def scenarios(names: list[str], holdout: bool) -> list[tuple[str, dict]]:
    base = EVALS / "holdout" if holdout else EVALS
    out = []
    for n in names:
        f = base / f"{n}.json"
        if f.exists():
            out += [(n, s) for s in json.loads(f.read_text(encoding="utf-8")).get("scenarios", [])]
    return out


def grade(answer: str, checks: dict) -> dict:
    """Wynik sprawdzeń: brakujące grupy checks.all i trafione wzorce checks.none."""
    missing = [g for g in checks.get("all", []) or []
               if not any(re.search(rx, answer, re.I) for rx in (g if isinstance(g, list) else [g]))]
    forbidden = [rx for rx in checks.get("none", []) or [] if re.search(rx, answer, re.I)]
    return {"ok": not missing and not forbidden, "missing": missing, "forbidden": forbidden}


def cost(model: str, usage) -> float:
    inp, out = PRICES[model]
    u = lambda k: getattr(usage, k, 0) or 0  # noqa: E731
    return (u("input_tokens") * inp + u("cache_creation_input_tokens") * inp * 1.25
            + u("cache_read_input_tokens") * inp * 0.1 + u("output_tokens") * out) / 1e6


def text_of(response) -> str:
    return "".join(b.text for b in response.content if b.type == "text")


class SdkBackend:
    """Claude API przez SDK anthropic (klucz API: ANTHROPIC_API_KEY albo profil `ant auth login`)."""

    def __init__(self, client, model: str, effort: str | None = None):
        self.client, self.model, self.effort = client, model, effort

    def __call__(self, system: str, prompt: str, schema: dict | None) -> tuple[str, str, float]:
        kwargs: dict = {"model": self.model, "max_tokens": 16000, "cache_control": {"type": "ephemeral"},
                        "system": system, "messages": [{"role": "user", "content": prompt}]}
        oc: dict = {}
        if self.effort:
            oc["effort"] = self.effort
        if schema:
            oc["format"] = {"type": "json_schema", "schema": schema}
        if oc:
            kwargs["output_config"] = oc
        r = self.client.messages.create(**kwargs)
        text = "" if r.stop_reason == "refusal" else text_of(r)
        return text, r.stop_reason, cost(self.model, r.usage)


class CliBackend:
    """Claude Code CLI (`claude -p`) z logowaniem użytkownika — bez klucza API. Bez narzędzi, z własnym promptem
    systemowym, w pustym katalogu (żeby nie wczytać CLAUDE.md tego repozytorium). Koszt: total_cost_usd z CLI
    (wycena cennikowa; przy subskrypcji to zużycie limitu planu, a nie faktura)."""

    def __init__(self, model: str, effort: str | None = None, exe: str = "claude", timeout: int = 600):
        self.model, self.effort, self.exe, self.timeout = model, effort, exe, timeout

    def __call__(self, system: str, prompt: str, schema: dict | None) -> tuple[str, str, float]:
        import subprocess
        import tempfile
        cmd = [self.exe, "-p", prompt, "--model", self.model, "--output-format", "json", "--tools", "",
               "--no-session-persistence", "--system-prompt", system]
        if self.effort:
            cmd += ["--effort", self.effort]
        if schema:
            cmd += ["--json-schema", json.dumps(schema)]
        with tempfile.TemporaryDirectory() as cwd:
            r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=self.timeout)
        try:
            d = json.loads(r.stdout)
        except json.JSONDecodeError as exc:
            raise BackendError(f"CLI: {(r.stderr or r.stdout)[-300:]}") from exc
        if d.get("is_error"):
            raise BackendError(f"CLI: {str(d.get('result'))[:300]}")
        text = json.dumps(d["structured_output"]) if schema and d.get("structured_output") else str(d.get("result") or "")
        stop = "refusal" if d.get("stop_reason") == "refusal" else "end_turn"
        return ("" if stop == "refusal" else text), stop, float(d.get("total_cost_usd") or 0.0)


class Runner:
    def __init__(self, backend, budget: float):
        self.backend, self.budget, self.spent = backend, budget, 0.0

    def call(self, system: str, prompt: str, schema: dict | None = None) -> tuple[str, str]:
        if self.spent >= self.budget:
            raise BudgetExceeded(f"budżet {self.budget:.2f} USD wyczerpany")
        text, stop, usd = self.backend(system, prompt, schema)
        self.spent += usd
        return text, stop

    def route(self, cat: list[dict], prompt: str) -> tuple[str, str]:
        names = [c["name"] for c in cat] + ["none"]
        system = ROUTER_SYSTEM + "\n".join(f"- {c['name']}: {c['description']}" for c in cat)
        schema = {"type": "object", "properties": {"skill": {"type": "string", "enum": names}},
                  "required": ["skill"], "additionalProperties": False}
        text, stop = self.call(system, prompt, schema)
        if stop == "refusal":
            return "", stop
        return json.loads(text).get("skill", ""), stop

    def answer(self, skill: str, prompt: str) -> tuple[str, str]:
        return self.call(skill_context(skill) + ANSWER_RULES, prompt)


class BackendError(Exception):
    pass


class BudgetExceeded(Exception):
    pass


def _api_errors():
    """Klasy błędów SDK (rate limit, status HTTP, połączenie); puste krotki, gdy SDK nie ma (testy z atrapą)."""
    try:
        import anthropic
        return anthropic.RateLimitError, anthropic.APIStatusError, anthropic.APIConnectionError
    except ImportError:
        return (), (), ()


def evaluate(runner: Runner, items: list[tuple[str, dict]], cat: list[dict]) -> list[dict]:
    rate_err, status_err, conn_err = _api_errors()
    results = []
    for skill, s in items:
        rec = {"skill": skill, "id": s.get("id"), "expect": s.get("expect")}
        try:
            chosen, stop = runner.route(cat, s["prompt"])
            rec["routed_to"], rec["route_stop"] = chosen, stop
            rec["route_ok"] = chosen == skill if s.get("expect") == "trigger" else chosen != skill
            if s.get("expect") == "trigger":
                answer, stop = runner.answer(skill, s["prompt"])
                rec["answer_stop"] = stop
                rec["checks"] = grade(answer, s.get("checks") or {})
                rec["answer"] = answer
            rec["ok"] = rec["route_ok"] and rec.get("checks", {"ok": True})["ok"]
        except BudgetExceeded as exc:
            rec["error"] = str(exc)
            results.append(rec)
            break
        except BackendError as exc:
            rec["error"], rec["ok"] = str(exc), False
        except rate_err as exc:
            rec["error"], rec["ok"] = f"429 rate limit ({exc.message})", False
        except status_err as exc:
            rec["error"], rec["ok"] = f"HTTP {exc.status_code}: {exc.message}", False
        except conn_err as exc:
            rec["error"], rec["ok"] = f"połączenie: {exc}", False
        rec["spent_usd"] = round(runner.spent, 4)
        results.append(rec)
        print(f"{'✓' if rec.get('ok') else '✗'} {skill}/{rec['id']} → {rec.get('routed_to', '?')}"
              f"{'' if rec.get('ok') else '  ' + json.dumps(rec.get('checks') or rec.get('error'), ensure_ascii=False)[:200]}")
    return results


def summary(results: list[dict], model: str, spent: float, label: str) -> str:
    rows = {}
    for r in results:
        rows.setdefault(r["skill"], []).append(r)
    lines = [f"# Ewaluacja skilli — {model} — {label}", "", f"Data: {dt.date.today().isoformat()} · koszt: "
             f"{spent:.2f} USD · scenariusze: {len(results)} · zaliczone: {sum(1 for r in results if r.get('ok'))}", "",
             "| Skill | Scenariusze | Routing OK | Sprawdzenia OK | Zaliczone |", "|---|---|---|---|---|"]
    for skill, rs in sorted(rows.items()):
        trig = [r for r in rs if r["expect"] == "trigger" and "checks" in r]
        lines.append(f"| {skill} | {len(rs)} | {sum(1 for r in rs if r.get('route_ok'))}/{len(rs)} | "
                     f"{sum(1 for r in trig if r['checks']['ok'])}/{len(trig)} | {sum(1 for r in rs if r.get('ok'))}/{len(rs)} |")
    fails = [r for r in results if not r.get("ok")]
    if fails:
        lines += ["", "## Niezaliczone", ""]
        for r in fails:
            why = r.get("error") or ("routing → " + str(r.get("routed_to")) if not r.get("route_ok") else
                                     f"brak: {r['checks']['missing']}; zakazane: {r['checks']['forbidden']}")
            lines.append(f"- `{r['skill']}/{r['id']}`: {why}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--model", default="", help="opus | sonnet | haiku albo pełne ID modelu")
    ap.add_argument("--skills", default="", help="skille po przecinku (domyślnie wszystkie)")
    ap.add_argument("--holdout", action="store_true", help="scenariusze z evals/skill_evals/holdout/")
    ap.add_argument("--budget", type=float, default=1.0, help="limit kosztu w USD")
    ap.add_argument("--effort", default=None, choices=["low", "medium", "high", "xhigh", "max"])
    ap.add_argument("--label", default="run", help="opis przebiegu w nazwie pliku wyniku")
    ap.add_argument("--backend", default="cli", choices=["cli", "sdk"],
                    help="cli: `claude -p` z logowaniem użytkownika (bez klucza); sdk: SDK anthropic z kluczem API")
    ap.add_argument("--yes", action="store_true", help="potwierdzenie płatnego przebiegu (po zgodzie człowieka)")
    ap.add_argument("--dry-run", action="store_true", help="bez API: plan przebiegu")
    a = ap.parse_args(argv)

    all_names = sorted(p.parent.name for p in SKILLS.glob("*/SKILL.md"))
    names = [s.strip() for s in a.skills.split(",") if s.strip()] or all_names
    items = scenarios(names, a.holdout)
    trig = sum(1 for _, s in items if s.get("expect") == "trigger")
    if a.dry_run or not a.model:
        chars = sum(len(skill_context(n)) for n, s in items if s.get("expect") == "trigger")
        print(f"Scenariusze: {len(items)} ({trig} trigger) · wywołania API: {len(items) + trig} · "
              f"kontekst skilli w odpowiedziach: ~{chars // 1000} tys. znaków (z cache dla kolejnych scenariuszy)")
        if not a.model:
            print("Płatny przebieg: --model <opus|sonnet|haiku> --budget <USD> --yes (tylko za zgodą człowieka)")
        return 0
    if not a.yes:
        print("✗ płatny przebieg wymaga --yes (po zgodzie człowieka na koszt)")
        return 1
    model = MODELS.get(a.model, a.model)
    if model not in PRICES:
        print(f"✗ brak cennika dla {model}; dopisz go w PRICES")
        return 1
    if a.backend == "sdk":
        import anthropic
        backend = SdkBackend(anthropic.Anthropic(), model, a.effort)
    else:
        backend = CliBackend(model, a.effort)
    runner = Runner(backend, a.budget)
    results = evaluate(runner, items, catalog())
    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / f"{dt.date.today().isoformat()}-{a.model}-{a.label}"
    stem.with_suffix(".jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in results),
                                          encoding="utf-8")
    stem.with_suffix(".md").write_text(summary(results, model, runner.spent, a.label), encoding="utf-8")
    print(f"\nKoszt: {runner.spent:.2f} USD · wynik: {stem}.md")
    return 0 if all(r.get("ok") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
