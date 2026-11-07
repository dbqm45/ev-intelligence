# syntax=docker/dockerfile:1
# Serwer MCP ev-intelligence (Streamable HTTP). Budowa z katalogu głównego repozytorium:
#   docker build -f deploy/Dockerfile --build-arg EV_KB_VERSION=$(git rev-parse --short=12 HEAD) -t ev-intelligence-mcp .
FROM python:3.13.18-slim@sha256:09a17cad02668ae61ece136b4fd36ac3849e14f670ebedb637ea3e15580525bc

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY deploy/requirements.lock /app/deploy/requirements.lock
# Opcjonalny certyfikat CA dla pip za proxy z inspekcją TLS (np. sieć firmowa):
#   docker build --secret id=pip_ca,src=/ścieżka/ca.crt …   (bez sekretu: zwykła weryfikacja TLS)
RUN --mount=type=secret,id=pip_ca,required=false \
    if [ -f /run/secrets/pip_ca ]; then export PIP_CERT=/run/secrets/pip_ca; fi; \
    pip install -r /app/deploy/requirements.lock

# Tylko to, czego serwer potrzebuje: wiedza, rejestr źródeł, taksonomia i narzędzia.
COPY skills/ /app/skills/
COPY knowledge/ /app/knowledge/
COPY sources/ /app/sources/
COPY taxonomy/ /app/taxonomy/
COPY VERSION /app/VERSION
COPY tools/ev_kb.py tools/ev_kb_mcp.py tools/ev_kb_poufne.py /app/tools/

ARG EV_KB_VERSION=nieznana
ENV EV_KB_VERSION=${EV_KB_VERSION} \
    EV_KB_ROOT=/app \
    EV_KB_DOCS=/docs \
    EV_KB_POUFNE=/poufne \
    PORT=8765

RUN useradd --system --uid 10001 --home-dir /nonexistent --shell /usr/sbin/nologin evkb
USER 10001
EXPOSE 8765

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import os,urllib.request,sys; sys.exit(0 if urllib.request.urlopen(f'http://127.0.0.1:{os.environ[\"PORT\"]}/healthz', timeout=4).status == 200 else 1)"]

CMD ["python", "/app/tools/ev_kb_mcp.py", "--transport", "http", "--host", "0.0.0.0"]
