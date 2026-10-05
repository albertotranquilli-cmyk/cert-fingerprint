# cert-fingerprint

**TLS certificate issuance timestamps as a location-free measurement instrument.**

Status: scaffold 2026-10-05. No results yet — the code execution environment used to build this has no outbound network, so `fetch_ct.py` must be run on a machine with internet access (your laptop, a VPS, or GitHub Actions).

## The idea

Every publicly trusted TLS certificate is logged in **Certificate Transparency (CT)** logs. crt.sh exposes them as a public JSON API with `not_before` timestamps. For any domain you can compute:

- daily issuance counts
- issuance by hour-of-day (UTC)
- issuance spikes on specific calendar days

Mainland China turns a few Saturdays/Sundays a year into official working days (调休, make-up workdays). No other country works those days. If certificate issuance for Chinese domains spikes on those days — while Western domains stay flat — you have a **location-free fingerprint of where infrastructure lives**, derived only from public CT data. No personal data, no geolocation, no contributor attributes.

This is the same natural-experiment logic as tiaoxiu-signal, applied to a different substrate: **infrastructure timestamps instead of human activity**. The two signals are independent and can be combined.

## Why this is different from tiaoxiu-signal

| | tiaoxiu-signal | cert-fingerprint |
|---|---|---|
| Substrate | human activity (GH Archive) | infrastructure (CT logs) |
| Data | per-repo daily actor counts | per-domain daily issuance counts |
| What it measures | calendar adherence of people | calendar adherence of certificate authorities / domain operators |
| Prior art | holiday dips known since 2018 | none found (checked 2026-10-02) |
| Failure mode | GH Archive capture loss | CT log gaps, CAA, multi-domain certs |

## Method

1. **Fetch**: query crt.sh for a panel of domains (Chinese: baidu.com, alibaba.com, tencent.com, bytedance.com, jd.com, netease.com; Western controls: amazon.com, google.com, microsoft.com, apple.com, github.com). Pin queries, cache raw JSON.
2. **Parse**: extract `not_before` per certificate, dedupe by serial number (one cert, many SANs), bin by Asia/Shanghai calendar day.
3. **Estimate**: for each domain, compute the make-up-day uplift: (issuance on makeup day) / (median issuance on matched ordinary weekends). Same estimator family as tiaoxiu-signal's s.
4. **Validate**: placebo on ordinary weekends; negative control = Japanese domains (UTC+9, no make-up days); leave-one-out; two-way bootstrap.
5. **Combine**: cross-correlate with tiaoxiu-signal's per-org s values where the domain maps to a known org (e.g., alibaba.com ↔ Alibaba org s=0.59).

## Data sources

- crt.sh public JSON API: `https://crt.sh/?q=<domain>&output=json` (no key, rate-limited)
- Alternative: download CT log snapshots from Google's CT logs (https://www.certificate-transparency.org/log-list) — heavier but no rate limits.
- Chinese calendar: NateScarlet/holiday-cn (already pinned in tiaoxiu-signal).

## Ethics / privacy

CT logs are public by design (RFC 6962). This project never touches personal data: no names, emails, IPs, or user attributes. It measures domain-level infrastructure timestamps only.

## Reproducibility

`./run_all.sh` regenerates everything. No keys. License: MIT.

## Next steps

1. Run `fetch_ct.py` on a networked machine (see PLAN.md).
2. Extend to more domains and to the 2024-2026 window.
3. Cross-correlate with tiaoxiu-signal org scores.
4. If the signal is real and stable: paper, then monetization angle (domain risk scoring, supply-chain monitoring).
