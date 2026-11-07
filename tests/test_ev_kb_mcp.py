"""Testy serwera MCP tools/ev_kb_mcp.py (klient oficjalnego SDK w procesie; pomijane bez pakietu `mcp` 2.x)."""
import asyncio
import sys
import unittest
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

try:
    from mcp import Client
    import ev_kb_mcp
    HAVE_MCP = True
except ImportError:  # pragma: no cover
    HAVE_MCP = False


def run(coro):
    return asyncio.run(coro)


@unittest.skipUnless(HAVE_MCP, "brak pakietu mcp 2.x")
class TestServer(unittest.TestCase):
    def call(self, name, args):
        async def go():
            async with Client(ev_kb_mcp.server) as c:
                return await c.call_tool(name, args)
        return run(go())

    def test_tools_are_read_only_and_instructions_set(self):
        async def go():
            async with Client(ev_kb_mcp.server) as c:
                return c.instructions, (await c.list_tools()).tools
        instructions, tools = run(go())
        self.assertIn("nic z pamięci", instructions)
        self.assertEqual(sorted(t.name for t in tools), ["ev_check", "ev_cite", "ev_confidential_check", "ev_route", "ev_search", "ev_skill"])
        for t in tools:
            self.assertTrue(t.annotations.read_only_hint, t.name)

    def test_instructions_list_all_skills_within_limit(self):
        import ev_kb
        names = [x["skill"] for x in ev_kb.list_skills()]
        text = ev_kb_mcp.INSTRUCTIONS
        self.assertLessEqual(len(text), ev_kb_mcp.INSTRUCTIONS_LIMIT)
        for n in names:
            self.assertIn(n, text)
        self.assertIn("Wersja wiedzy:", text)

    def test_every_skill_is_a_prompt(self):
        import ev_kb
        async def go():
            async with Client(ev_kb_mcp.server) as c:
                prompts = (await c.list_prompts()).prompts
                got = await c.get_prompt("ev-billing-tariff-expert", {"task": "wycena"})
                return prompts, got
        prompts, got = run(go())
        self.assertEqual(sorted(p.name for p in prompts), sorted(x["skill"] for x in ev_kb.list_skills()))
        text = got.messages[0].content.text
        self.assertIn("name: ev-billing-tariff-expert", text)
        self.assertTrue(text.endswith("Zadanie: wycena"))

    def test_route_and_skill(self):
        r = self.call("ev_route", {"task": "wycena sesji z taryfy OCPI, step_size"})
        self.assertEqual(r.structured_content["skills"][0]["skill"], "ev-billing-tariff-expert")
        r = self.call("ev_skill", {"name": "ev-billing-tariff-expert", "file": "taryfy-ocpi.md"})
        self.assertIn("step_size", r.structured_content["content"])

    def test_skill_rejects_paths_outside_references(self):
        r = self.call("ev_skill", {"name": "ev-ocpp-expert", "file": "../../../CLAUDE.md"})
        self.assertIn("error", r.structured_content)
        r = self.call("ev_skill", {"name": "../tools"})
        self.assertIn("error", r.structured_content)

    def test_cite_and_check(self):
        r = self.call("ev_cite", {"tag": "[NOPE §1]"})
        self.assertEqual(r.structured_content["status"], "NIEZNANY_DOKUMENT")
        r = self.call("ev_cite", {"tag": "`[OCPI230 §10.3.1]`"})
        self.assertEqual(r.structured_content["source"]["id"], "OCPI230")
        r = self.call("ev_check", {"text": "x `[NOPE §1]` y `[OCPI230]`"})
        self.assertFalse(r.structured_content["ok"])
        self.assertEqual([x["status"] for x in r.structured_content["results"]], ["NIEZNANY_DOKUMENT", "OK"])

    def test_unavailable_norm_is_flagged_in_search_cite_check(self):
        r = self.call("ev_search", {"query": "parametry styków według EN IEC 62196-2"})
        self.assertIn("unavailable", r.structured_content)
        self.assertIn("pierwszym zdaniu", ev_kb_mcp.INSTRUCTIONS)
        r = self.call("ev_cite", {"tag": "[ISO 15118-20 §8]"})
        self.assertEqual(r.structured_content["status"], "NIEDOSTEPNE")
        r = self.call("ev_check", {"text": "Według ISO 15118-2 `[ISO 15118-2 §7]` …"})
        self.assertFalse(r.structured_content["ok"])
        self.assertIn("notice", r.structured_content)

    def test_search_empty_has_note(self):
        r = self.call("ev_search", {"query": "kwantowy reaktor fuzji"})
        self.assertEqual(r.structured_content["hits"], [])
        self.assertIn("Nie uzupełniaj z pamięci", r.structured_content["note"])


@unittest.skipUnless(HAVE_MCP, "brak pakietu mcp 2.x")
class TestHttpGuard(unittest.TestCase):
    def test_public_host_requires_long_token(self):
        import io
        import os
        from contextlib import redirect_stderr
        old = os.environ.pop("EV_KB_TOKEN", None)
        try:
            with redirect_stderr(io.StringIO()):
                self.assertEqual(ev_kb_mcp.main(["--transport", "http", "--host", "0.0.0.0"]), 2)
                os.environ["EV_KB_TOKEN"] = "short"
                self.assertEqual(ev_kb_mcp.main(["--transport", "http", "--host", "0.0.0.0"]), 2)
        finally:
            os.environ.pop("EV_KB_TOKEN", None)
            if old is not None:
                os.environ["EV_KB_TOKEN"] = old

    def test_transport_security_for_public_host(self):
        import io
        import os
        from contextlib import redirect_stderr
        self.assertIsNone(ev_kb_mcp.transport_security("127.0.0.1"))
        old = {k: os.environ.pop(k, None) for k in ("EV_KB_ALLOWED_HOSTS", "EV_KB_ALLOWED_ORIGINS")}
        try:
            with redirect_stderr(io.StringIO()):
                self.assertFalse(ev_kb_mcp.transport_security("0.0.0.0").enable_dns_rebinding_protection)
            os.environ["EV_KB_ALLOWED_HOSTS"] = "ev-kb.example.com"
            ts = ev_kb_mcp.transport_security("0.0.0.0")
            self.assertTrue(ts.enable_dns_rebinding_protection)
            self.assertEqual(ts.allowed_hosts, ["ev-kb.example.com"])
            self.assertEqual(ts.allowed_origins, ["https://ev-kb.example.com"])
        finally:
            for k, v in old.items():
                os.environ.pop(k, None)
                if v is not None:
                    os.environ[k] = v

    def test_healthz_without_token(self):
        async def app(scope, receive, send):
            raise AssertionError("aplikacja nie powinna obsłużyć /healthz")
        sent = []

        async def send(msg):
            sent.append(msg)
        run(ev_kb_mcp.BearerAuth(app, "t" * 40)({"type": "http", "path": "/healthz", "headers": []}, None, send))
        self.assertEqual(sent[0]["status"], 200)

    def test_bearer_auth_rejects_and_accepts(self):
        seen = []

        async def app(scope, receive, send):
            seen.append(scope["path"])
            await send({"type": "http.response.start", "status": 200, "headers": []})
            await send({"type": "http.response.body", "body": b"ok"})

        guard = ev_kb_mcp.BearerAuth(app, "t" * 40)

        async def request(auth, path="/mcp"):
            sent = []
            headers = [(b"authorization", auth)] if auth else []
            scope = {"type": "http", "path": path, "headers": headers}

            async def send(msg):
                sent.append(msg)
            await guard(scope, None, send)
            return sent[0]["status"]

        self.assertEqual(run(request(None)), 401)
        self.assertEqual(run(request(b"Bearer wrong")), 401)
        self.assertEqual(run(request(b"Bearer " + b"t" * 40)), 200)
        self.assertEqual(run(request(None, "/" + "t" * 40 + "/mcp")), 200)
        self.assertEqual(run(request(None, "/" + "x" * 40 + "/mcp")), 401)
        self.assertEqual(run(request(None, "/mcp")), 401)
        self.assertEqual(seen, ["/mcp", "/mcp"])


if __name__ == "__main__":
    unittest.main()
