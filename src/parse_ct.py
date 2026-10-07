#!/usr/bin/env python3
"""Parse raw CT JSON from data/raw/ into results/daily_counts.json and results/SUMMARY.md.

Binning: not_before date as stored (no timezone shift) to avoid off-by-one on
late-UTC issuances. Dedupes by serial number.
"""
import json, os, datetime as dt
from collections import defaultdict

from ct_validate import InvalidCTData, load_records
from fetch_ct import PANEL

ROOT = os.environ.get("CERT_FINGERPRINT_ROOT", os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
RAW = os.path.join(ROOT, "data", "raw")
OUT = os.path.join(ROOT, "results")

# Official make-up workdays only (State Council notices). 2024-06-15 and 2025-05-05
# were removed: neither is a make-up workday (2025-05-05 is a Labor Day holiday).
MAKEUP = {"2024-09-14", "2024-10-12", "2025-01-26", "2025-02-08"}


def bin_day(ts):
    """Return the calendar date of not_before as stored (YYYY-MM-DD)."""
    if not ts:
        return None
    return ts[:10] if len(ts) >= 10 else None


def main():
    os.makedirs(OUT, exist_ok=True)
    summary = {"domains": {}, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "binning": "not_before date as stored (no timezone shift)"}
    if not os.path.isdir(RAW):
        summary["error"] = "no data/raw/ directory"
    else:
        files = [fn for fn in os.listdir(RAW) if fn.endswith(".json")]
        if not files:
            summary["error"] = "no .json files in data/raw/"
        for fn in sorted(files):
            domain = fn[:-5]
            path = os.path.join(RAW, fn)
            try:
                with open(path, "rb") as fh:
                    data = load_records(fh.read())
            except (InvalidCTData, ValueError, OSError) as e:
                summary["domains"][domain] = {"error": f"{type(e).__name__}: {e}"}
                continue
            seen = set()
            days = defaultdict(int)
            for e in data:
                ser = e.get("serial_number") or e.get("id")
                if ser in seen:
                    continue
                seen.add(ser)
                d = bin_day(e.get("not_before") or "")
                if d:
                    days[d] += 1
            vals = [days[d] for d in MAKEUP if d in days]
            if vals:
                import statistics
                makeup_med = statistics.median(vals)
                base = []
                for d, c in days.items():
                    if d in MAKEUP:
                        continue
                    try:
                        wd = dt.date.fromisoformat(d).weekday()
                    except Exception:
                        continue
                    if wd >= 5:
                        base.append(c)
                base_med = statistics.median(base) if base else 0
                uplift = (makeup_med / base_med) if base_med > 0 else None
            else:
                makeup_med = base_med = uplift = None
            summary["domains"][domain] = {
                "unique_certs": len(seen),
                "days_with_data": len(days),
                "makeup_median_daily": makeup_med,
                "ordinary_weekend_median_daily": base_med,
                "makeup_uplift": round(uplift, 3) if uplift is not None else None,
            }
    if "error" not in summary:
        missing = sorted(set(PANEL) - set(summary["domains"]))
        invalid = sorted(d for d, s in summary["domains"].items() if "error" in s)
        if missing:
            summary["missing_domains"] = missing
        if missing or invalid:
            summary["error"] = (f"incomplete or invalid input: {len(invalid)} invalid, "
                                f"{len(missing)}/{len(PANEL)} panel domains missing")
    json.dump(summary, open(os.path.join(OUT, "daily_counts.json"), "w"), indent=1, allow_nan=False)
    lines = ["# cert-fingerprint — results summary", "", "fetched_at: " + summary["fetched_at"], "",
             "binning: not_before date as stored", ""]
    if "error" in summary:
        lines.append("**" + summary["error"] + "**")
        lines.append("")
    lines += ["| domain | unique certs | makeup-day median/day | weekend median/day | uplift |",
              "|---|---:|---:|---:|---:|"]
    for dom, s in summary["domains"].items():
        if "error" in s:
            lines.append("| " + dom + " | ERR " + s["error"] + " | | | |")
        else:
            lines.append("| " + dom + " | " + str(s["unique_certs"]) + " | " + str(s["makeup_median_daily"]) + " | " + str(s["ordinary_weekend_median_daily"]) + " | " + str(s["makeup_uplift"]) + " |")
    open(os.path.join(OUT, "SUMMARY.md"), "w").write("\n".join(lines) + "\n")
    print(open(os.path.join(OUT, "SUMMARY.md")).read())
    if "error" in summary:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
