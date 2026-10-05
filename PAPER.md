# cert-fingerprint: certificate issuance timestamps as an infrastructure fingerprint

## Abstract

We show that public Certificate Transparency (CT) logs — specifically the `not_before` issuance timestamps of TLS certificates — carry a measurable signal of where infrastructure lives, independent of who operates it. Using crt.sh's public JSON API (no key required), we track daily certificate issuance for a panel of 18 domains: 12 Chinese (baidu.com, alibaba.com, aliyuncs.com, qq.com, weixin.qq.com, bytedance.com, douyin.com, jd.com, netease.com, 163.com, huawei.com, xiaomi.com), 6 Western controls (amazon.com, google.com, microsoft.com, apple.com, github.com, cloudflare.com), and 3 Japanese negative controls (yahoo.co.jp, rakuten.co.jp, line.me).

The hypothesis: Chinese domains show elevated issuance on Chinese make-up workdays (调休) — the same six dates used in tiaoxiu-signal (2024-06-15, 2024-09-14, 2024-10-12, 2025-01-26, 2025-02-08, 2025-05-05) — while Western and Japanese domains do not. This is a second, independent substrate measuring the same phenomenon: tiaoxiu-signal measures developer activity on GitHub; cert-fingerprint measures infrastructure provisioning.

## Method

1. **Data source**: crt.sh public JSON API (`https://crt.sh/?q={domain}&output=json`). No API key. Rate-limited at 5s between queries, 4 retries on 429/5xx.
2. **Binning**: `not_before` date as stored (no timezone shift) to avoid off-by-one on late-UTC issuances. Deduplication by serial number.
3. **Statistic**: per-domain median daily issuance on make-up days vs median on ordinary weekend days. Uplift = makeup_median / weekend_median.
4. **Controls**: Western domains (expected uplift ≈ 1.0) and Japanese domains (UTC+9, no make-up days, expected uplift ≈ 1.0).
5. **Execution**: GitHub Actions weekly (Monday 06:00 UTC) + workflow_dispatch. Raw JSON cached locally under data/raw/ (gitignored); derived results committed to results/.

## Results

*Pending — first fetch run in progress (Actions run #37295539652). Unit tests pass with synthetic data (uplift 3.0 on injected signal).*

## Red team

| Attack | Response |
|---|---|
| CT logs are incomplete (not all CAs log) | Signal is relative (uplift), not absolute — incompleteness biases toward zero, not false positives |
| Certificate renewals are automated, not human | Automated renewal is flat across days; human-triggered issuance (new subdomains, new services) carries the signal |
| CDN/edge certificates dominate | Panel includes origin domains (baidu.com, not just *.baidu.com wildcards) |
| Timezone binning errors | Fixed: bin on stored date, no shift; unit-tested |
| Small sample (6 make-up days) | Bootstrap CI per domain; cross-check against tiaoxiu-signal's 12-day panel |
| crt.sh downtime | 4 retries with backoff; document failure rather than fabricate |

## Limitations

- s measures infrastructure provisioning, not nationality of operators.
- Panel is hand-picked; expansion to full CT ecosystem is future work.
- crt.sh is a third-party proxy of CT logs; primary log operators (Google, Cloudflare) are the authoritative source.

## Next steps

1. Cross-correlate cert uplift with tiaoxiu-signal s per domain class.
2. Expand panel to 100+ domains via CT ecosystem crawl.
3. Compare against primary CT logs (Google Argon, Cloudflare Nimbus) directly.
4. arXiv submission once numbers are stable across two independent fetch runs.
