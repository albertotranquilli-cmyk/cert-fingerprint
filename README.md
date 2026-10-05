# README.md

# cert-fingerprint

Certificate Transparency logs as an infrastructure fingerprint. Second independent substrate for the tiaoxiu-signal finding: if Chinese make-up workdays shift GitHub activity, they should also shift TLS certificate issuance.

## Status

- CI: green (run #7, synthetic tests pass, uplift 3.0 on injected signal)
- Fetch: run #5 in progress (Actions, ~2h for 18 domains via crt.sh)
- Predictions: written BEFORE numbers arrive (PREDICTIONS.md) — anti p-hacking
- Paper draft: PAPER.md structured, results section pending real numbers

## Files

- **PREDICTIONS.md** — numeric predictions derived from tiaoxiu-signal historical data. Uplift CN expected 1.334, US/JP controls at 1.0. Verification criteria defined before fetch completes.
- **PAPER.md** — paper draft: abstract, method, red team (7 attacks), limits, next steps
- **FETCH_STATUS.md** — current run status and fixes applied
- **TEST_LOG.md** — documented failures and fixes
- **src/fetch_ct.py** — downloads CT JSON from crt.sh (public API, no key)
- **src/parse_ct.py** — bins not_before dates, computes uplift per domain
- **src/test_fetch_ct.py** — unit tests (no network)

## Workflow

- **ci.yml** — syntax check + unit tests on every push
- **fetch.yml** — weekly Monday 06:00 UTC + workflow_dispatch, timeout 360min, commits derived results only (raw JSON gitignored)

## Related

- tiaoxiu-signal: https://github.com/albertotranquilli-cmyk/tiaoxiu-signal
- audits: https://github.com/albertotranquilli-cmyk/audits
- grok-archive (private lab): https://github.com/albertotranquilli-cmyk/grok-archive
