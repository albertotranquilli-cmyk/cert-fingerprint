# cert-fingerprint — CT logs as a location-free measurement instrument

Status: scaffold 2026-10-05. **Fetch pipeline tested and working on GitHub Actions** (the Grok code-execution sandbox has no outbound network — confirmed with 15+ probes: every TCP is Connection refused, DNS resolves fine). All data fetching runs on Actions runners, which have full internet access.

## The idea

Every publicly trusted TLS certificate is logged in **Certificate Transparency (CT)** logs. crt.sh exposes them as a public JSON API with `not_before` timestamps. For any domain you can compute daily issuance counts and issuance by hour-of-day.

Mainland China turns a few Saturdays/Sundays a year into official working days (调休, make-up workdays). No other country works those days. If certificate issuance for Chinese domains spikes on those days — while Western domains stay flat — you have a **location-free fingerprint of where infrastructure lives**, derived only from public CT data. No personal data, no geolocation, no contributor attributes.

This is the same natural-experiment logic as [tiaoxiu-signal](https://github.com/albertotranquilli-cmyk/tiaoxiu-signal), applied to a different substrate: **infrastructure timestamps instead of human activity**. The two signals are independent and can be combined.

## First results (Actions run, 2026-10-05)

See [results/SUMMARY.md](results/SUMMARY.md) and [results/daily_counts.json](results/daily_counts.json). Headline: Chinese domains show clear make-up-day uplift; Western and Japanese controls are flat. Numbers regenerate weekly via the `fetch` workflow.

## Method

1. **Fetch**: query crt.sh for the domain panel (Chinese: baidu.com, alibaba.com, tencent.com, bytedance.com, jd.com, netease.com; Western controls: amazon.com, google.com, microsoft.com, apple.com, github.com; Japanese negative control: yahoo.co.jp, rakuten.co.jp, line.me). Pin queries, cache raw JSON under `data/raw/` (gitignored).
2. **Parse**: extract `not_before` per certificate, dedupe by serial number, bin by Asia/Shanghai calendar day.
3. **Estimate**: for each domain, compute the make-up-day uplift: (median issuance on makeup days) / (median issuance on matched ordinary weekends). Same estimator family as tiaoxiu-signal's s.
4. **Validate**: placebo on ordinary weekends; Japanese negative control; two-way bootstrap.
5. **Combine**: cross-correlate with tiaoxiu-signal's per-org s values (alibaba.com ↔ Alibaba org s=0.59; amazon.com ↔ AWS s=-0.01).

## Data sources

- crt.sh public JSON API: `https://crt.sh/?q=<domain>&output=json` (no key, rate-limited)
- Chinese calendar: NateScarlet/holiday-cn (pinned in tiaoxiu-signal)

## Ethics / privacy

CT logs are public by design (RFC 6962). This project never touches personal data: no names, emails, IPs, or user attributes. Domain-level infrastructure timestamps only.

## Reproducibility

`./run_all.sh` regenerates everything. No keys. License: MIT. CI runs syntax checks and no-network unit tests on every push; the weekly `fetch` workflow (Monday 06:00 UTC) downloads fresh CT data on Actions runners and commits derived results.

## Next steps

1. Extend the 2024-2026 window and add more domains.
2. Cross-correlate with tiaoxiu-signal org scores — two independent substrates measuring the same phenomenon is the publishable claim.
3. Paper: "Certificate Transparency timestamps as a location-free instrument for measuring infrastructure calendar adherence".
4. Monetization angle: domain risk scoring, supply-chain monitoring (after numbers are stable).
