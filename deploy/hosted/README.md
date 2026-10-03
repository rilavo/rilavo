# Hosted issuance (P-31 path 3)

For teams without dedicated security engineering capacity who'd rather not
own key custody and uptime — the operator runs the service; you point your
SDK at it and use the standard two-call API.

## Run it with Docker (on any docker host)

```bash
cd deploy/hosted
docker compose up --build
```

Expected output includes `hosted issuer live on http://<host>:8090`.
Then check health:

```bash
curl -s http://127.0.0.1:8090/health
# -> {"status": "ok"}
```

And fetch the issuer's published key-directory entry:

```bash
curl -s http://127.0.0.1:8090/directory
```

## No-docker fallback (identical service, run directly)

```bash
uv run python -c "from rilavo.service import RilavoService; import threading; s = RilavoService(port=8090).start(); print('hosted issuer live on', s.url, flush=True); threading.Event().wait()"
```

## Choosing this path

Pick hosted if you lack security engineering capacity or don't want custody
and uptime obligations. You can migrate to self-hosted later — the managed-
to-self-hosted migration mechanism is specified at E-08 and applies
symmetrically regardless of which path you start on.

## Honesty note

The compose file here is validated structurally; executing it requires a
Docker host, which this reference environment does not include. The
underlying service itself (`rilavo.service`) is exercised continuously by
the automated test suite, including over live HTTP.
