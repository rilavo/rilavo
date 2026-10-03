"""Rilavo CLI entry point."""

from __future__ import annotations

import argparse
import sys
import sys as _sys
import socket

from . import __version__


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else _sys.argv[1:]
    parser = argparse.ArgumentParser(
        prog="rilavo",
        description=f"Rilavo Protocol v{__version__} — CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # keygen
    p_keygen = sub.add_parser("keygen", help="generate Ed25519 keypair + directory entry")
    p_keygen.add_argument("--out", required=True, help="output private key path (PEM)")
    p_keygen.set_defaults(func=cmd_keygen)

    # issue
    p_issue = sub.add_parser("issue", help="issue a credential")
    p_issue.add_argument("--key", required=True, help="issuer private key (PEM)")
    p_issue.add_argument("--principal", required=True)
    p_issue.add_argument("--agent", required=True)
    p_issue.add_argument("--agent-key", required=True, help="agent public key (base64url, no padding)")
    p_issue.add_argument("--action-class", required=True)
    p_issue.add_argument("--audience", required=True)
    p_issue.add_argument("--ttl", type=int, default=14400)
    p_issue.set_defaults(func=cmd_issue)

    # conformance
    p_conformance = sub.add_parser("conformance", help="run local conformance self-check")
    p_conformance.add_argument("--json", action="store_true", help="output as JSON")
    p_conformance.set_defaults(func=cmd_conformance)

    # explain
    p_explain = sub.add_parser("explain", help="explain a rejection reason code")
    p_explain.add_argument("code")
    p_explain.set_defaults(func=cmd_explain)

    # init (scaffold)
    p_init = sub.add_parser("init", help="scaffold a framework integration")
    p_init.add_argument("--framework", required=True, choices=["fastapi", "express", "nextjs", "go", "wordpress"])
    p_init.add_argument("--dir", required=True)
    p_init.add_argument("--project-name", required=True)
    p_init.set_defaults(func=cmd_init)

    # smoke
    p_smoke = sub.add_parser("smoke", help="run end-to-end smoke test")
    p_smoke.set_defaults(func=cmd_smoke)

    # doctor
    p_doctor = sub.add_parser("doctor", help="check install health (CLI on PATH, imports, smoke, optional online)")
    p_doctor.add_argument("--online", action="store_true")
    p_doctor.set_defaults(func=cmd_doctor)

    # openapi
    p_openapi = sub.add_parser("openapi", help="generate OpenAPI 3.1 spec")
    p_openapi.add_argument("--output", help="output file (default: stdout)")
    p_openapi.set_defaults(func=cmd_openapi)

    # service - THE MAIN FIX
    p_service = sub.add_parser("service", help="run the rilavo service with HTTP endpoints")
    p_service.add_argument("--port", type=int, default=8090, help="service port")
    p_service.add_argument("--metrics-port", type=int, default=9090, help="metrics endpoint port")
    p_service.add_argument("--metrics-host", default="127.0.0.1", help="metrics bind address")
    p_service.add_argument("--otel-endpoint", default=None, help="OTLP endpoint for tracing")
    p_service.add_argument("--otel-sampling", type=float, default=0.01, help="trace sampling rate")
    p_service.add_argument("--issuer-key", help="path to issuer private key (PEM)")
    p_service.add_argument("--verifier-id", default="verifier:rilavo-self-hosted", help="verifier identifier")
    p_service.add_argument("--serve-discovery", action="store_true", help="serve /.well-known/rilavo discovery endpoint")
    p_service.set_defaults(func=cmd_service)

    # completion
    p_completion = sub.add_parser("completion", help="generate shell completion scripts")
    p_completion.add_argument("shell", choices=["bash", "zsh", "fish", "powershell"])
    p_completion.set_defaults(func=cmd_completion)

    args = parser.parse_args(argv)
    return args.func(args)


# =============================================================================
# Command implementations
# =============================================================================

def cmd_keygen(args):
    """Generate Ed25519 keypair + directory entry."""
    from .keys import generate_keypair
    from .keys import b64url_encode, public_key_bytes
    from cryptography.hazmat.primitives import serialization

    priv, pub = generate_keypair()
    with open(args.out, "wb") as f:
        f.write(priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ))

    # Compute issuer ID
    from .keys import fingerprint
    issuer_id = fingerprint(pub)
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    import json
    import time
    entry = {
        "issuer_id": issuer_id,
        "public_key_pem": pub_pem,
        "valid_until": 253370764800,  # year 2050
    }
    print(json.dumps(entry, indent=2))


def cmd_issue(args):
    """Issue a credential using the provided issuer private key."""
    from .api import Issuer, do_issue
    from .keys import Ed25519PublicKey, b64url_decode
    from cryptography.hazmat.primitives import serialization
    import json

    # Load issuer private key
    with open(args.key, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    issuer = Issuer(private_key=private_key)

    # Load agent public key from base64url (as documented in quickstart)
    agent_pub_b64 = args.agent_key
    padding = "=" * (-len(agent_pub_b64) % 4)
    agent_pub_bytes = b64url_decode(agent_pub_b64 + padding)
    agent_pub = Ed25519PublicKey.from_public_bytes(agent_pub_bytes)

    cred = do_issue(
        issuer=issuer,
        principal=args.principal,
        agent=args.agent,
        agent_public_key=agent_pub,
        action_class=args.action_class,
        audience=args.audience,
        ttl_seconds=args.ttl,
    )

    print(json.dumps(cred.fields, indent=2))


def cmd_conformance(args):
    """Run cross-SDK conformance check."""
    from .conformance_cli import run_local_checks, render_report
    import json
    report = run_local_checks()
    if args.json:
        # Convert report to dict for JSON output
        result = {
            "target": report.target,
            "results": [
                {"check_id": r.check_id, "title": r.title, "passed": r.passed, "detail": r.detail}
                for r in report.results
            ],
            "summary": {
                "passed": sum(1 for r in report.results if r.passed is True),
                "failed": sum(1 for r in report.results if r.passed is False),
                "skipped": sum(1 for r in report.results if r.passed is None),
            }
        }
        print(json.dumps(result, indent=2))
    else:
        print(render_report(report))


def cmd_explain(args):
    """Explain a rejection reason code."""
    import sys
    from .errors import EXPLANATIONS
    if args.code in EXPLANATIONS:
        exp = EXPLANATIONS[args.code]
        print(f"Code: {args.code}")
        print(f"Summary: {exp.summary}")
        print(f"Likely causes: {', '.join(exp.likely_causes)}")
        print(f"Remediation: {', '.join(exp.remediation)}")
        print(f"Doc: {exp.doc_pointer}")
    else:
        print(f"Unknown reason code: {args.code}", file=sys.stderr)
        return 1


def cmd_init(args):
    """Scaffold a framework-specific integration."""
    from .init_scaffold import scaffold
    from pathlib import Path
    scaffold(args.framework, Path(args.dir), project_name=args.project_name)
    print(f"Scaffolded {args.framework} project in {args.dir}")


def cmd_smoke(args):
    """Run end-to-end smoke test."""
    from .smoke import run_smoke
    result = run_smoke()
    if result:
        print("Smoke test: PASS")
    else:
        print("Smoke test: FAIL")
        return 1


def cmd_doctor(args):
    """Check install health."""
    from .doctor import run_doctor
    ok = run_doctor(online=args.online)
    if ok:
        print("Doctor: OK")
    else:
        print("Doctor: FAIL")
        return 1


def cmd_openapi(args):
    """Generate OpenAPI 3.1 spec."""
    from .openapi import generate_openapi_spec
    import rilavo
    import json
    spec = generate_openapi_spec(
        version=rilavo.__version__,
        server_url="http://localhost:8090",
    )
    if args.output:
        with open(args.output, "w") as f:
            json.dump(spec, f, indent=2)
    else:
        print(json.dumps(spec, indent=2))


def cmd_service(args):
    """Run the rilavo service with HTTP endpoints."""
    import signal
    import sys
    import threading
    import socket
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse
    import json
    import base64

    from .api import Issuer, do_issue, do_verify
    from .keys import KeyDirectory, Ed25519PublicKey, b64url_decode
    from .credential import Credential
    from .pop import Request
    from .revocation import RevocationLog
    from .verifier import NonceCache
    from .observability import get_metrics, start_metrics_server
    from .tracing import init_tracing

    # Initialize tracing once
    init_tracing(
        service_name="rilavo-service",
        endpoint=args.otel_endpoint,
        sampling_rate=args.otel_sampling,
    )

    # Load issuer key if provided
    if args.issuer_key:
        from cryptography.hazmat.primitives import serialization
        with open(args.issuer_key, "rb") as f:
            private_key = serialization.load_pem_private_key(f.read(), password=None)
        issuer = Issuer(private_key=private_key)
    else:
        issuer = Issuer()

    # Create key directory and publish issuer
    directory = KeyDirectory()
    directory.publish(issuer.directory_entry())

    # Create shared nonce cache and revocation log for the service
    nonce_cache = NonceCache()
    revocation_log = RevocationLog()

    # Start metrics server
    metrics = get_metrics()
    metrics_server = start_metrics_server(metrics, host=args.metrics_host, port=args.metrics_port)
    print(f"Metrics server listening on http://{args.metrics_host}:{args.metrics_port}/metrics")

    class RilavoHandler:
        """HTTP request handler for Rilavo service endpoints."""
        def __init__(self, issuer, directory, verifier_id, nonce_cache, revocation_log):
            self.issuer = issuer
            self.directory = directory
            self.verifier_id = verifier_id
            self.nonce_cache = nonce_cache
            self.revocation_log = revocation_log

        def handle_request(self, method, path, headers, body):
            parsed = urlparse(path)

            if method == "GET":
                if parsed.path == "/directory":
                    entry = self.issuer.directory_entry()
                    return 200, {"Content-Type": "application/json"}, {
                        "issuer_id": entry.fingerprint_id,
                        "public_key_pem": entry.public_key_pem.decode("utf-8"),
                        "valid_until": entry.valid_until,
                        "verifier_id": self.verifier_id,
                    }
                elif parsed.path == "/healthz":
                    return 200, {"Content-Type": "application/json"}, {"status": "ok"}
                else:
                    return 404, {"Content-Type": "application/json"}, {"error": "not_found"}

            elif method == "POST":
                if parsed.path == "/issue":
                    try:
                        data = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        return 400, {"Content-Type": "application/json"}, {"error": "Invalid JSON"}

                    # Extract parameters
                    principal = data.get("principal")
                    agent = data.get("agent")
                    agent_pub = data.get("agent_pub")
                    action_class = data.get("action_class")
                    audience = data.get("audience")
                    ttl_seconds = data.get("ttl_seconds")
                    context = data.get("context")

                    if not all([principal, agent, agent_pub, action_class, audience]):
                        return 400, {"Content-Type": "application/json"}, {"error": "Missing required fields: principal, agent, agent_pub, action_class, audience"}

                    try:
                        # Parse agent public key from base64url
                        agent_pub_b64 = data.get("agent_pub", "")
                        agent_pub_bytes = b64url_decode(agent_pub_b64)
                        agent_pub = Ed25519PublicKey.from_public_bytes(agent_pub_bytes)

                        cred = do_issue(
                            issuer=self.issuer,
                            principal=principal,
                            agent=agent,
                            agent_public_key=agent_pub,
                            action_class=action_class,
                            audience=audience,
                            ttl_seconds=ttl_seconds,
                            context=context,
                        )

                        return 201, {"Content-Type": "application/json"}, {
                            "credential": cred.fields
                        }

                    except Exception as e:
                        return 400, {"Content-Type": "application/json"}, {"error": str(e)}

                elif parsed.path == "/verify":
                    try:
                        data = json.loads(body) if body else {}
                    except json.JSONDecodeError:
                        return 400, {"Content-Type": "application/json"}, {"error": "Invalid JSON"}

                    credential_data = data.get("credential")
                    request_data = data.get("request")

                    if not credential_data or not request_data:
                        return 400, {"Content-Type": "application/json"}, {"error": "Missing credential or request"}

                    try:
                        credential = Credential(fields=credential_data)
                        request = Request(
                            method=request_data.get("method", ""),
                            path=request_data.get("path", ""),
                            requested_action=request_data.get("requested_action", ""),
                            signature=request_data.get("signature", ""),
                            request_nonce=request_data.get("request_nonce", ""),
                        )

                        result = do_verify(
                            verifier_id=self.verifier_id,
                            credential=credential,
                            request=request,
                            key_directory=self.directory,
                            revocation_log=self.revocation_log,
                            nonces=self.nonce_cache,
                        )

                        return 200, {"Content-Type": "application/json"}, {
                            "accepted": result.accepted,
                            "reason_code": result.reason_code,
                        }

                    except Exception as e:
                        return 400, {"Content-Type": "application/json"}, {"error": str(e)}

                return 404, {"Content-Type": "application/json"}, {"error": "not_found"}

    def make_handler(issuer, directory, verifier_id, nonce_cache, revocation_log):
        handler = RilavoHandler(issuer, directory, verifier_id, nonce_cache, revocation_log)

        class Handler(BaseHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                self.handler = handler
                super().__init__(*args, **kwargs)

            def do_GET(self):
                parsed = urlparse(self.path)
                status, headers, body = self.handler.handle_request("GET", parsed.path, dict(self.headers), "")
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(json.dumps(body).encode())

            def do_POST(self):
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8') if content_length else ""
                status, headers, body = self.handler.handle_request("POST", self.path, dict(self.headers), body)
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(json.dumps(body).encode())

            def log_message(self, format, *args):
                pass

        return Handler

    # Create HTTP server with SO_REUSEADDR
    class ReuseAddrHTTPServer(HTTPServer):
        def server_bind(self):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            super().server_bind()

    Handler = make_handler(issuer, directory, args.verifier_id, nonce_cache, revocation_log)
    server = ReuseAddrHTTPServer(("0.0.0.0", args.port), Handler)

    # Start HTTP server in a thread
    def run_server():
        server.serve_forever()

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    print(f"Rilavo service ready on http://0.0.0.0:{args.port}")
    print("Endpoints:")
    print(f"  GET  /directory  - Key directory")
    print(f"  POST /issue      - Issue credential")
    print(f"  POST /verify     - Verify credential")
    print(f"  GET  /healthz    - Health check")
    print(f"  GET  /metrics    - Prometheus metrics (port {args.metrics_port})")
    print("Press Ctrl+C to stop")

    def signal_handler(signum, frame):
        print("\nShutting down...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Keep running
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)
def cmd_completion(args):
    """Generate shell completion scripts."""
    shells = {
        "bash": "_RILAVO_COMPLETE=bash_source rilavo",
        "zsh": "_RILAVO_COMPLETE=zsh_source rilavo",
        "fish": "_RILAVO_COMPLETE=fish_source rilavo",
        "powershell": "_RILAVO_COMPLETE=powershell_source rilavo",
    }
    print(shells[args.shell])


if __name__ == "__main__":
    raise SystemExit(main())

