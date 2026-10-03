import re
from pathlib import Path
import rilavo.conformance_cli as cc

py = (Path("src/rilavo/verifier.py").read_text()
      + Path("src/rilavo/credential.py").read_text())
ts = Path("../packages/rilavo-ts/src/index.ts").read_text()

checks = []
def c(n_, ok): checks.append((n_, bool(ok)))

# Gate order from Python's actual comment style "# N. ...":
py_order = re.findall(r"^\s*# (\d+(?:[ab])?)\.", py, flags=re.M)
ts_order = re.findall(r"// step (\d+[ab]?):", ts)
c("gate order: TS sequence matches Python prefix",
  ts_order == py_order[:len(ts_order)])
c("python continues past SDK scope to #10 audit receipt",
  "10" in py_order)

PAIRS = [("missing_field","MISSING_FIELD"),("malformed_credential","MALFORMED_CREDENTIAL"),
 ("delegation_not_permitted","delegation_not_permitted"),
 ("unrecognized_version","UNRECOGNIZED_VERSION"),("audience_mismatch","AUDIENCE_MISMATCH"),
 ("expired","EXPIRED"),("not_yet_valid","NOT_YET_VALID"),("unknown_issuer","UNKNOWN_ISSUER"),
 ("key_not_valid_at_issuance","KEY_NOT_VALID_AT_ISSUANCE"),("invalid_signature","INVALID_SIGNATURE"),
 ("replay_detected","REPLAY_DETECTED"),("revoked","REVOKED"),
 ("proof_of_possession_failed","PROOF_OF_POSSESSION_FAILED"),("scope_mismatch","SCOPE_MISMATCH")]
for reason, marker in PAIRS:
    c(f"parity {reason}", marker in py and f'"{reason}"' in ts)

r_local = cc.run_local_checks()
c("local target exit 0", r_local.exit_code() == 0)
dead = cc.run_http_checks("http://127.0.0.1:1")
c("dead target exit 1 with reasons", dead.exit_code() == 1
  and all((r.detail or r.passed is None) for r in dead.results if r.passed is False))
rendered = cc.render_report(cc.run_local_checks()).lower()
c("informational posture, no certification language",
  "not conformance certification" in rendered
  and not any(w in rendered for w in ("certified","approved","compliant")))
cli_src = Path("src/rilavo/cli.py").read_text()
c("CLI subcommand wired", '"conformance"' in cli_src and "--target" in cli_src)
c("no disclosure-window numbers hardcoded",
  not re.search(r"disclosure[_ ]window[:\s]*\d+", Path("src/rilavo/conformance_cli.py").read_text().lower()))

passed = sum(ok for _, ok in checks)
for n_, ok in checks: print(("PASS " if ok else "FAIL ") + n_)
print(f"SECOND PASS (D2): {passed}/{len(checks)}")
assert passed == len(checks)
