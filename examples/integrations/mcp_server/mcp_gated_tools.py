"""MCP-server integration SKETCH (P-18's named first integration surface).

The Model Context Protocol treats authentication as optional; most real
servers skip it. This sketch shows where Rilavo slots in: a `@gated` wrapper
around tool handlers that verifies a Rilavo credential (carried by the agent)
before the tool executes. It is a SKETCH of the integration shape -- the MCP
wire protocol itself is represented by a plain function call, so this file
runs standalone with no MCP dependency.

Run:  uv run python ../../examples/mcp_server/mcp_gated_tools.py
(from rilavo-protocol/, or set PYTHONPATH to the protocol src).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "rilavo-protocol" / "src"))

from rilavo.testing import offline_test_kit, local_test_agent  # noqa: E402
from rilavo.pop import sign_request, Request                   # noqa: E402
from rilavo.verifier import NonceCache                         # noqa: E402

VERIFIER_ID = "verifier:mcp-demo.example"


class McpToolServer:
    """Sketch of an MCP server whose TOOLS are gated by credential checks."""

    def __init__(self) -> None:
        kit = offline_test_kit()      # stand-in for fetched issuer keys
        self.kit = kit
        self.nonces = NonceCache()    # ONE cache per server process
        self.tools: dict[str, callable] = {}

    def tool(self, name: str, action_class: str):
        """Decorator: registers a handler bound to an exact action-class.
        Exact-match scope semantics per P-07 -- no wildcards at v0."""
        def decorator(fn):
            self.tools[name] = {"handler": fn, "action_class": action_class}
            return fn
        return decorator

    def call_tool(self, name: str, credential,
                  pop_signature: str, pop_nonce: str) -> dict:
        """What the MCP layer would do on a tools/call request:
        verify the credential against THIS server, then dispatch."""
        if name not in self.tools:
            return {"ok": False, "error": "unknown_tool"}
        spec = self.tools[name]
        request = Request("TOOLS/CALL", f"tools/{name}",
                          spec["action_class"], pop_signature, pop_nonce)
        result = __import__("rilavo.api", fromlist=["do_verify"]).do_verify(
            VERIFIER_ID, credential, request, self.kit.key_directory,
            self.kit.revocation_log, nonces=self.nonces)
        if not result.accepted:
            return {"ok": False, "error": "unauthorized",
                    "reason_code": result.reason_code}
        return {"ok": True, "result": spec["handler"]()}


# --- demo server with two gated tools ----------------------------------------
server = McpToolServer()

@server.tool(name="read_file", action_class="fs.read")
def read_file():
    return "file contents"

@server.tool(name="send_payment", action_class="payments.initiate")
def send_payment():
    return "payment sent"


if __name__ == "__main__":
    agent_priv, agent_pub = local_test_agent()
    from rilavo.api import do_issue
    cred = do_issue(server.kit.issuer, principal="agent-host:01",
                    agent="mcp-client-01", agent_public_key=agent_pub, action_class="fs.read",
                    audience=VERIFIER_ID)

    # authorized tool call:
    sig, nonce = sign_request(agent_priv, "TOOLS/CALL", "tools/read_file",
                              "fs.read")
    print("read_file:", server.call_tool("read_file", cred, sig, nonce))

    # NOTE (v0 semantics): a credential's nonce is SINGLE-USE per verifier,
    # so each tool call needs its own credential. Agents request a fresh one
    # per action -- that is by design, bounding any stolen credential's
    # blast radius to exactly one call.
    cred2 = do_issue(server.kit.issuer, principal="agent-host:01",
                     agent="mcp-client-01", agent_public_key=agent_pub,
                     action_class="payments.initiate", audience=VERIFIER_ID)

    # authorized for its own action class:
    sig2, nonce2 = sign_request(agent_priv, "TOOLS/CALL",
                                "tools/send_payment", "payments.initiate")
    print("send_payment:", server.call_tool("send_payment", cred2, sig2, nonce2))

    # scope violation -- a FRESH fs.read credential still cannot call
    # send_payment: exact-match scope, no wildcards at v0:
    cred3 = do_issue(server.kit.issuer, principal="agent-host:01",
                     agent="mcp-client-01", agent_public_key=agent_pub,
                     action_class="fs.read", audience=VERIFIER_ID)
    sig3, nonce3 = sign_request(agent_priv, "TOOLS/CALL",
                                "tools/send_payment", "payments.initiate")
    print("scope violation:", server.call_tool("send_payment", cred3, sig3, nonce3))
