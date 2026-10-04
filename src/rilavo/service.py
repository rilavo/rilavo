"""HTTP deployment of the minimal protocol API (P-19).

Wraps exactly the two protocol operations plus operational necessities:

    POST /issue     principal, agent, action_class, audience, ttl -> credential
    POST /verify    credential, request -> accept/reject + reason code
    GET  /directory the published, versioned key-directory entry (P-17/P-32)
    POST /revoke    operational extension (outside the frozen protocol
                    surface): invalidate one credential nonce

Standard library only -- a self-hosted deployment must not require any
infrastructure dependency (Core Spec section 8).
"""

from __future__ import annotations

import base64
import json
import threading
import time
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlparse

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

from .api import Issuer, VerifyResult, do_issue, do_verify
from .credential import DEFAULT_MAX_TTL_SECONDS, Credential
from .keys import KeyDirectory
from .pop import Request
from .receipts import ReceiptLog
from .revocation import REVOKED_BY_ISSUER, REVOKED_BY_PRINCIPAL, RevocationLog
from .verifier import NonceCache


@dataclass
class ServiceState:
    """Shared, process-wide verifier state.

    The NonceCache and ReceiptLog MUST live here -- one cache per process,
    never per request -- so replay detection works across calls.
    """

    issuer: Issuer
    directory: KeyDirectory
    revocations: RevocationLog
    nonces: NonceCache
    receipts: ReceiptLog
    lock: threading.Lock
    verifier_id: str = "verifier:rilavo-self-hosted"
    metrics_sink: object | None = None
    serve_discovery: bool = False


def make_state(issuer: Issuer | None = None,
               verifier_id: str = "verifier:rilavo-self-hosted",
               serve_discovery: bool = False) -> ServiceState:
    issuer = issuer or Issuer()
    directory = KeyDirectory()
    directory.publish(issuer.directory_entry())
    return ServiceState(
        issuer=issuer,
        directory=directory,
        revocations=RevocationLog(),
        nonces=NonceCache(),
        receipts=ReceiptLog(),
        lock=threading.Lock(),
        verifier_id=verifier_id,
        serve_discovery=serve_discovery,
    )


class RilavoHandler(BaseHTTPRequestHandler):
    server_version = "Rilavo/" + __import__("rilavo").__version__

    @property
    def state(self) -> ServiceState:
        return self.server.state  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:  # quiet by default
        pass

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b""
        try:
            parsed = json.loads(raw.decode("utf-8")) if raw else {}
        except json.JSONDecodeError:
            raise _BadRequest("malformed_json")
        if not isinstance(parsed, dict):
            raise _BadRequest("malformed_request")
        return parsed

    # -- routes ---------------------------------------------------------

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/.well-known/rilavo":
            if not getattr(self.state, "serve_discovery", False):
                self._send_json(404, {"error": "not_served"})
                return
            doc = self._build_discovery_document()
            self._send_json(200, doc)
            return
        if path == "/directory":
            entry = self.state.issuer.directory_entry()
            self._send_json(200, {
                "issuer_id": entry.fingerprint_id,
                "public_key_pem": entry.public_key_pem.decode("utf-8"),
                "valid_until": entry.valid_until,
                "verifier_id": self.state.verifier_id,
            })
        elif path == "/health":
            self._send_json(200, {"status": "ok"})
        # OpenAPI endpoints
        elif path == "/openapi.json":
            import rilavo

            from .openapi import generate_openapi_spec
            spec = generate_openapi_spec(
                version=rilavo.__version__,
                server_url=f"http://{self.headers.get('Host', 'localhost:8090')}",
            )
            self._send_json(200, spec)
        elif path == "/docs":
            self._serve_swagger_ui()
        elif path == "/redoc":
            self._serve_redoc()
        else:
            self._send_json(404, {"error": "not_found"})

    def _build_discovery_document(self) -> dict:
        """Builds the P3-A1 discovery document from live directory state."""
        entry = self.state.issuer.directory_entry()
        return {
            "rilavo_discovery_version": 1,
            "entries": [{
                "issuer_id": entry.fingerprint_id,
                "public_key_pem": entry.public_key_pem.decode("utf-8"),
                "valid_until": entry.valid_until,
                "audience_hints": [self.state.verifier_id],
            }],
        }

    def do_POST(self) -> None:
        try:
            body = self._read_json()
        except _BadRequest as exc:
            self._send_json(400, {"accepted": False, "reason_code": str(exc)})
            return

        try:
            if self.path == "/issue":
                self._handle_issue(body)
            elif self.path == "/batch-issue":
                self._handle_batch_issue(body)
            elif self.path == "/verify":
                self._handle_verify(body,
                                    started=time.perf_counter_ns())
            elif self.path == "/revoke":
                self._handle_revoke(body)
            else:
                self._send_json(404, {"error": "not_found"})
        except _BadRequest as exc:
            self._send_json(400, {"accepted": False, "reason_code": str(exc)})


    def _handle_issue(self, body: dict) -> None:
        missing = [k for k in ("principal", "agent", "agent_public_key",
                               "action_class", "audience") if not body.get(k)]
        if missing:
            raise _BadRequest(f"missing_field:{','.join(missing)}")
        ttl = body.get("ttl_seconds", DEFAULT_MAX_TTL_SECONDS)
        from .keys import b64url_decode
        try:
            agent_public_key = Ed25519PublicKey.from_public_bytes(
                b64url_decode(str(body["agent_public_key"])))
        except Exception:
            raise _BadRequest("malformed_field:agent_public_key")
        try:
            with self.state.lock:
                cred = do_issue(
                    self.state.issuer,
                    principal=str(body["principal"]),
                    agent=str(body["agent"]),
                    agent_public_key=agent_public_key,
                    action_class=str(body["action_class"]),
                    audience=str(body["audience"]),
                    ttl_seconds=int(ttl),
                    context=body.get("context"),
                )
        except (ValueError, TypeError) as exc:
            raise _BadRequest(str(exc))
        self._send_json(201, json.loads(cred.to_json()))

    def _handle_batch_issue(self, body: dict) -> None:
        requests_data = body.get("requests", [])
        if not isinstance(requests_data, list):
            raise _BadRequest("requests must be an array")
        creds_out = []
        statuses: list[dict[str, object]] = []
        for i, r in enumerate(requests_data):
            try:
                apk_raw = base64.urlsafe_b64decode(
                    r["agent_public_key"] + "==")
                agent_pub = Ed25519PublicKey.from_public_bytes(apk_raw)
                with self.state.lock:
                    cred = do_issue(
                        self.state.issuer,
                        principal=str(r.get("principal", "")),
                        agent=str(r.get("agent", "")),
                        agent_public_key=agent_pub,
                        action_class=str(r.get("action_class", "")),
                        audience=str(r.get("audience",
                                      self.state.verifier_id)),
                        ttl_seconds=int(r.get("ttl_seconds",
                                        DEFAULT_MAX_TTL_SECONDS)),
                    )
                creds_out.append(json.loads(cred.to_json()))
                statuses.append({"index": i, "ok": True})
            except Exception as exc:
                statuses.append({"index": i, "ok": False,
                                 "error": str(exc)})
        self._send_json(201, {"credentials": creds_out,
                              "status": statuses})

    def _handle_verify(self, body: dict,
                       started: int | None = None) -> None:
        cred_body = body.get("credential")
        req_body = body.get("request")
        if not isinstance(cred_body, dict) or not isinstance(req_body, dict):
            raise _BadRequest("missing_field:credential,request")
        req_keys = {"method", "path", "requested_action", "signature", "request_nonce"}
        if not req_keys <= set(req_body):
            raise _BadRequest("missing_field:request")
        result: VerifyResult = do_verify(
            verifier_id=self.state.verifier_id,
            credential=Credential(fields=cred_body),
            request=Request(
                method=str(req_body["method"]),
                path=str(req_body["path"]),
                requested_action=str(req_body["requested_action"]),
                signature=str(req_body["signature"]),
                request_nonce=str(req_body["request_nonce"]),
            ),
            key_directory=self.state.directory,
            revocation_log=self.state.revocations,
            nonces=self.state.nonces,
            receipts=self.state.receipts,
        )
        sink = getattr(self.state, "metrics_sink", None)
        if sink is not None:
            dt = ((time.perf_counter_ns() - started) / 1e9
                  if started is not None else 0.0)
            try:
                sink.record_count("rilavo_verifications_total",
                                  {"reason": result.reason_code})
                sink.record_duration("rilavo_verify_duration_seconds", dt)
            except Exception:  # noqa: S110
                pass                    # telemetry must never alter outcomes
        self._send_json(200, {"accepted": result.accepted,
                              "reason_code": result.reason_code})

    def _handle_revoke(self, body: dict) -> None:
        nonce = body.get("nonce")
        revoked_by = body.get("revoked_by", REVOKED_BY_ISSUER)
        if not nonce or revoked_by not in (REVOKED_BY_ISSUER, REVOKED_BY_PRINCIPAL):
            raise _BadRequest("invalid_revoke_request")
        with self.state.lock:
            self.state.revocations.append(
                str(nonce), revoked_by=revoked_by,
                reason_code=str(body.get("reason_code", "unspecified")))
        self._send_json(200, {"revoked": True,
                              "head_hash": self.state.revocations.head_hash()})



    def _serve_swagger_ui(self) -> None:
        """Serve Swagger UI."""
        html = self._get_swagger_ui_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        body = html.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_redoc(self) -> None:
        """Serve Redoc."""
        html = self._get_redoc_html()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        body = html.encode("utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _get_swagger_ui_html(self) -> str:
        """Generate Swagger UI HTML."""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Rilavo API - Swagger UI</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
    <style>
        html, body { margin: 0; padding: 0; height: 100%; }
        .swagger-ui .topbar { background-color: #3f51b5; }
        .swagger-ui .topbar .download-url-wrapper { display: none; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
    <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
    <script>
        window.onload = function() {
            window.ui = SwaggerUIBundle({
                url: "/openapi.json",
                dom_id: "#swagger-ui",
                deepLinking: true,
                presets: [
                    SwaggerUIBundle.presets.apis,
                    SwaggerUIStandalonePreset
                ],
                layout: "StandaloneLayout",
                displayRequestDuration: true,
                filter: true,
                showExtensions: true,
                showCommonExtensions: true,
            });
        };
    </script>
</body>
</html>"""

    def _get_redoc_html(self) -> str:
        """Generate Redoc HTML."""
        return """<!DOCTYPE html>
<html>
<head>
    <title>Rilavo API - Redoc</title>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { margin: 0; padding: 0; }
        redoc { height: 100vh; }
    </style>
</head>
<body>
    <redoc spec-url="/openapi.json"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.1.0/bundles/redoc.standalone.js"></script>
</body>
</html>"""


class _BadRequest(Exception):
    pass


class RilavoService:
    """Runnable wrapper. `start()` binds an ephemeral port; `url` gives base."""

    def __init__(self, host: str = "127.0.0.1", port: int = 0,
                 issuer: Issuer | None = None,
                 serve_discovery: bool = False) -> None:
        self.state = make_state(issuer, serve_discovery=serve_discovery)
        self.httpd = ThreadingHTTPServer((host, port), RilavoHandler)
        self.httpd.state = self.state  # type: ignore[attr-defined]
        self.host, self.port = self.httpd.server_address[:2]

    @property
    def url(self) -> str:
        return f"http://{self.host!s}:{self.port!s}"

    def start(self) -> RilavoService:
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()
        return self

    def stop(self) -> None:
        self.httpd.shutdown()
        self.httpd.server_close()


# -- tiny stdlib client used by tests and the pilot harness --------------

import urllib.error
import urllib.request


def post(base_url: str, path: str, payload: dict) -> tuple[int, dict]:
    req = urllib.request.Request(
        base_url + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def get(base_url: str, path: str) -> tuple[int, dict]:
    with urllib.request.urlopen(base_url + path, timeout=10) as resp:
        return resp.status, json.loads(resp.read().decode())
