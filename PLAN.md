# PLAN.md — cert-fingerprint roadmap

Status: 2026-10-05.

## Step 0 — scaffold (done)

README, this plan, `src/fetch_ct.py`.

## Step 1 — fetch CT data (BLOCKED in Grok code-execution: no outbound network)

Run on any machine with internet:

```
python src/fetch_ct.py
```

Downloads crt.sh JSON for the domain panel into `data/raw/`. ~50-200 MB. Rate-limited; the script sleeps between queries and retries on 429/5xx. Estimated runtime: 30-90 min for the full panel.

**Important**: crt.sh is a single point of failure and is rate-limited. If it blocks, fall back to downloading CT log files directly from certificate-transparency.org log list (Google Argon/Xenon, Cloudflare Nimbus). That path is heavier (TB-scale) but has no rate limits — for v1, crt.sh is enough.

## Step 2 — parse and bin

`src/parse_ct.py` (to write after Step 1 produces data): dedupe by serial, bin `not_before` by Asia/Shanghai day, output `data/derived/daily_<domain>.csv`.

## Step 3 — estimate

`src/analyze.py`: make-up-day uplift per domain, placebo, Japanese negative control, two-way bootstrap. Output `results/results.json`.

## Step 4 — cross-correlate with tiaoxiu-signal

Join domain uplift with org-level s from tiaoxiu-signal (Alibaba 0.59, Baidu PaddlePaddle 0.59, AWS -0.01, Mozilla 0.02). If domains and orgs agree, the two instruments measure the same underlying phenomenon from independent substrates — that is the publishable claim.

## Step 5 — paper

Same structure as tiaoxiu-signal/PAPER.md. Title draft: "Certificate Transparency timestamps as a location-free instrument for measuring infrastructure calendar adherence".

## Risks

- crt.sh downtime/rate limits → fallback to raw CT logs.
- Multi-domain certs (SANs) → dedupe by serial, attribute to all listed domains or to the primary CN only; disclose the choice.
- CAA / short-lived certs (Let's Encrypt 90-day) → issuance is bursty; use median baselines and wide windows.
- Some Chinese domains use domestic CAs not always in public CT logs → coverage gap; disclose.
- Timezone: bin at Asia/Shanghai midnight; test UTC binning as sensitivity (same as tiaoxiu-signal row 23).
