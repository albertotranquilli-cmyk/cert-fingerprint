# cert-fingerprint test log — 2026-10-05

## What was tested

1. **Grok code-execution sandbox**: 15+ TCP probes (crt.sh, example.com, 1.1.1.1, 8.8.8.8, github.com, yahoo finance, coingecko). DNS resolves on all; every TCP connect is `Connection refused` (2ms-2s). Confirmed: **no outbound network** from this runtime. See Q359 in grok-archive/DOMANDE.md.
2. **GitHub Actions**: 6 workflow runs triggered by pushes. All 6 concluded `failure`, but **zero jobs were ever scheduled** (API returns `total_count: 0` jobs per run; log URL 404). Runs complete in <1 second. This is the signature of the workflow file failing at the *workflow level* before any job starts — most commonly a YAML syntax error in the `run: |` block (the inline Python heredoc) or an invalid workflow definition.
3. **Local re-validation of fetch_ct.py logic**: syntax and structure confirmed correct (PANEL defined, get() defined, retry loop, JSON sanity check). The script itself is sound; the failure is in how GitHub parses the workflow.

## What was NOT tested

- crt.sh API from a networked host (pending a working Actions run).
- The parse/summarize step (depends on raw data from step above).
- mirror-signal and commit-hours (scaffolded, CI not yet triggered).

## Next step

Rewrite fetch.yml and ci.yml with the inline Python moved to separate scripts (src/parse_ct.py, src/test_fetch_ct.py) so the YAML contains no heredocs. Then re-trigger and verify jobs actually start.
