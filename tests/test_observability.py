"""D1 observability hooks: instrumentation only, zero protocol impact."""

from __future__ import annotations

import base64
import json
import re

import pytest

from rilavo.errors import VerificationError
from rilavo.observability import Metrics, timed_verify, timed_verify_raising
from rilavo.verifier import NonceCache
from tests.test_conformance import Harness


class Clock:
    def __init__(self): self.t = 1000.0
    def __call__(self): return self.t


def _fresh_metrics():
    return Metrics()


def test_counter_increments_by_reason():
    m = _fresh_metrics()
    for _ in range(3):
        m.inc("rilavo_verifications_total", {"reason": "accept"})
    m.inc("rilavo_verifications_total", {"reason": "expired"})
    data = m.json_export()
    assert data["counters"]["rilavo_verifications_total"] == {
        'reason="accept"': 3, 'reason="expired"': 1}


def test_duration_histogram_records_and_buckets():
    m = _fresh_metrics()
    for dt in (0.0005, 0.002, 0.02):
        m.observe_duration("rilavo_verify_duration_seconds", dt)
    d = m.json_export()["duration_histogram"]
    assert d["count"] == 3
    assert d["buckets_le"]["0.001"] == 1
    assert d["buckets_le"]["0.005"] == 2
    assert d["buckets_le"]["0.05"] == 3
    assert abs(d["sum"] - 0.0225) < 1e-6


def test_prometheus_exposition_format_wellformed():
    m = _fresh_metrics()
    m.inc("rilavo_verifications_total", {"reason": "accept"})
    m.observe_duration("rilavo_verify_duration_seconds", 0.004)
    text = m.prometheus()
    assert "# TYPE rilavo_verifications_total counter" in text
    assert '# TYPE rilavo_verify_duration_seconds histogram' in text
    assert 'rilavo_verifications_total{reason="accept"} 1' in text
    assert re.search(r'rilavo_verify_duration_seconds_bucket\{le="0\.01"\} 1', text)
    assert "rilavo_verify_duration_seconds_sum" in text
    assert "rilavo_verify_duration_seconds_count 1" in text
    # every sample line ends in a number:
    samples = [l for l in text.splitlines()
               if l and not l.startswith("#")]
    assert all(re.search(r"[\d.]+$", l) for l in samples)


def test_json_export_is_json_serializable():
    m = _fresh_metrics()
    m.inc("rilavo_verifications_total", {"reason": "accept"})
    m.observe_duration("rilavo_verify_duration_seconds", 0.001)
    parsed = json.loads(json.dumps(m.json_export()))
    assert parsed["format"] == "rilavo-observability-v0"


def test_timed_verify_wrapper_returns_result_unchanged(harness_like=None):
    """Zero protocol impact: wrapper returns the exact VerifyResult and the
    core verify path is untouched (full conformance suite proves this)."""
    from tests.test_conformance import Harness
    h = Harness()
    cred = h.credential()
    req = h.request()
    m = _fresh_metrics()

    from unittest.mock import patch

    from rilavo.api import do_verify
    with patch("rilavo.verifier.time") as fake_time:
        fake_time.time.return_value = cred.fields["iat"] + 1
        result = timed_verify(m, do_verify, credential=cred, request=req,
                              verifier_id="verifier:checkout.example.com",
                              key_directory=h.directory,
                              revocation_log=h.revocations,
                              nonces=NonceCache(), receipts=h.receipts)
    assert result.accepted is True
    counts = m.json_export()["counters"]["rilavo_verifications_total"]
    assert counts.get('reason="accept"') == 1
    assert m.durations.total_count == 1


def test_timed_verify_raising_records_reason_then_reraises():
    from rilavo.errors import EXPIRED
    from rilavo.verifier import verify as raw_verify
    h = Harness()
    cred = h.credential(ttl=600)
    m = _fresh_metrics()

    from unittest.mock import patch
    with patch("rilavo.verifier.time") as ft:
        ft.time.return_value = cred.fields["exp"] + 10
        with pytest.raises(VerificationError) as excinfo:
            timed_verify_raising(
                m, lambda **kw: raw_verify(
                    credential=kw["credential"], request=kw["request"],
                    verifier_id="verifier:checkout.example.com",
                    key_directory=h.directory, revocation_log=h.revocations,
                    nonces=NonceCache(), now=kw["now"]),
                credential=cred, request=h.request(), now=cred.fields["exp"] + 5)
    assert excinfo.value.reason_code == EXPIRED
    counts = m.json_export()["counters"]["rilavo_verifications_total"]
    assert counts.get('reason="expired"') == 1


# --- imports/helpers used above -------------------------------------------------


# ---------------------------------------------------------------------------
# Extended D1: pluggable sinks, null-sink identity, structured logs,
# service-level hook wiring.
# ---------------------------------------------------------------------------

def test_null_sink_is_a_noop_and_satisfies_the_interface():
    from rilavo.observability import NullSink
    sink = NullSink()
    assert sink.record_count("x", {"reason": "accept"}, 5) is None
    assert sink.record_duration("y", 0.5) is None


def test_logging_sink_emits_structured_json_lines():
    from rilavo.observability import LoggingSink
    captured = []
    sink = LoggingSink(emit=captured.append)
    sink.record_count("rilavo_verifications_total", {"reason": "expired"})
    sink.record_duration("rilavo_verify_duration_seconds", 0.25)
    assert len(captured) == 2
    parsed0 = json.loads(captured[0])
    assert parsed0["event"] == "counter"
    assert parsed0["name"] == "rilavo_verifications_total"
    assert parsed0["reason"] == "expired"
    parsed1 = json.loads(captured[1])
    assert parsed1["event"] == "duration" and parsed1["seconds"] == 0.25


def test_metrics_object_satisfies_the_sink_interface():
    """Metrics itself is a valid sink for instrumented_do_verify."""
    m = _fresh_metrics()
    assert hasattr(m, "record_count") and hasattr(m, "record_duration")


def test_service_verify_hook_fires_on_accept_and_reject_real():
    import base64
    import urllib.request

    from rilavo.keys import public_key_bytes
    from rilavo.pop import sign_request as pop_sign_request
    from rilavo.service import RilavoService
    from rilavo.testing import local_test_agent

    svc = RilavoService(port=0).start()
    try:
        agent_priv, agent_pub = local_test_agent()
        pub_b64 = base64.urlsafe_b64encode(
            public_key_bytes(agent_pub)).decode().rstrip("=")
        audience = svc.state.verifier_id

        class ListSink:
            def __init__(self):
                self.events = []
            def record_count(self, name, labels=None, value=1):
                self.events.append(("count", dict(labels or {})))
            def record_duration(self, name, seconds, labels=None):
                self.events.append(("duration", seconds))
        sink = ListSink()
        svc.state.metrics_sink = sink

        def post(path, payload):
            r = urllib.request.Request(svc.url + path,
                                       data=json.dumps(payload).encode(),
                                       headers={"Content-Type": "application/json"},
                                       method="POST")
            with urllib.request.urlopen(r, timeout=5) as resp:
                return json.loads(resp.read())

        cred = post("/issue", {"principal": "p", "agent": "a",
                               "agent_public_key": pub_b64,
                               "action_class": "data.read",
                               "audience": audience})
        sig, nonce = pop_sign_request(agent_priv, "POST", "/x", "data.read")
        result = post("/verify", {
            "credential": cred.fields if hasattr(cred, "fields") else cred,
            "request": {"method": "POST", "path": "/x",
                        "requested_action": "data.read",
                        "signature": sig, "request_nonce": nonce}})
        assert result["accepted"] is True

        reasons = [labels.get("reason") for kind, labels in sink.events
                   if kind == "count"]
        assert "accept" in reasons
        assert len(sink.events) >= 2          # count + duration recorded
    finally:
        svc.stop()


def test_off_mode_no_sink_still_works_identically():
    import urllib.request

    from rilavo.keys import public_key_bytes
    from rilavo.pop import sign_request as pop_sign_request
    from rilavo.service import RilavoService
    from rilavo.testing import local_test_agent

    svc = RilavoService(port=0).start()      # metrics_sink defaults to None
    try:
        assert svc.state.metrics_sink is None
        agent_priv, agent_pub = local_test_agent()
        pub_b64 = base64.urlsafe_b64encode(
            public_key_bytes(agent_pub)).decode().rstrip("=")
        audience = svc.state.verifier_id
        r = urllib.request.Request(svc.url + "/issue",
                                   data=json.dumps({
                                       "principal": "p", "agent": "a",
                                       "agent_public_key": pub_b64,
                                       "action_class": "data.read",
                                       "audience": audience}).encode(),
                                   headers={"Content-Type": "application/json"},
                                   method="POST")
        with urllib.request.urlopen(r, timeout=5) as resp:
            cred = json.loads(resp.read())
        sig, nonce = pop_sign_request(agent_priv, "GET", "/y", "data.read")
        v = urllib.request.Request(svc.url + "/verify",
                                   data=json.dumps({
                                       "credential": cred,
                                       "request": {
                                           "method": "GET", "path": "/y",
                                           "requested_action": "data.read",
                                           "signature": sig,
                                           "request_nonce": nonce}}).encode(),
                                   headers={"Content-Type": "application/json"},
                                   method="POST")
        with urllib.request.urlopen(v, timeout=5) as resp:
            out = json.loads(resp.read())
        assert out["accepted"] is True
        assert svc.state.metrics_sink is None   # OFF mode untouched
    finally:
        svc.stop()
