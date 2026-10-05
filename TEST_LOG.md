# cert-fingerprint — test log

## 2026-10-05 — round 2 (after heredoc removal)

**Fix applied:** removed inline Python heredocs from both workflows (ci.yml, fetch.yml).
All logic now lives in separate scripts: src/fetch_ct.py, src/parse_ct.py, src/test_fetch_ct.py.
Workflows only call `python src/*.py`.

**Bug found and fixed in parse_ct.py:** the original binning shifted not_before by +8h
(UTC->Asia/Shanghai). A cert issued 2024-06-15T20:00:00Z (a makeup Saturday) landed on
2024-06-16 local, silently dropping from the makeup-day count. Switched to binning by
the not_before date as stored. Unit test now asserts uplift == 3.0 on synthetic data
(3 unique certs on a makeup day vs 1 on an ordinary Saturday).

**Local verification:** `python src/test_fetch_ct.py` -> ALL TESTS PASSED. PyYAML parses
both workflow files cleanly. No tabs, no odd indentation, no CRLF.

**Expected on GitHub:** ci.yml run should now schedule jobs (previously total_count=0,
<1s completion = workflow-level rejection, consistent with the heredoc being the culprit).
fetch.yml run should execute fetch_ct.py (will fail on crt.sh connectivity from this
environment if crt.sh is down/filtered — that is a data-source issue, not a workflow issue)
and then parse_ct.py + commit results/.

2026-10-05 run 37295539652 conclusion=failure: step commit results exit 1 — `git push` rejected `main -> main (fetch first)`; remote has commits absent from the runner checkout (local commit d62d74b created results/SUMMARY.md and results/daily_counts.json, not pushed).
