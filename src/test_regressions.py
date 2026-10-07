#!/usr/bin/env python3
"""Fail-closed regression tests for the audit of merged PR #1 (no network).

Every fixture is local. fetch_ct.py is exercised in a subprocess where
urllib.request.urlopen is replaced by a function that raises, fetch_ct.get is
replaced by a fixture lookup and time.sleep is a no-op, so no test can reach
crt.sh.

Contract under test:
  * malformed / semantically empty input -> clean non-zero exit, no traceback,
    never a silent success;
  * input bytes are never normalized (cache files are byte-identical to the
    fixture response).
"""
import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
import traceback

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)

from fetch_ct import PANEL  # noqa: E402  (pure import, no side effects)

VALID_ROW = {"id": 1, "serial_number": "0a1b", "not_before": "2024-09-07T10:00:00"}
VALID_BODY = json.dumps([VALID_ROW])

# Malformed JSON arrays and syntactically valid but semantically empty records.
BAD_BODIES = {
    "truncated_array": '[{"id": 1, "serial_number": "0a1b", "not_before": "2024-09-14T00:00:00"}',
    "empty_list": "[]",
    "non_object_rows": "[1, 2, 3]",
    "null_row": "[null]",
    "empty_object_row": "[{}]",
    "empty_not_before": '[{"id": 1, "serial_number": "0a1b", "not_before": ""}]',
    "garbage_not_before": '[{"id": 1, "serial_number": "0a1b", "not_before": "xxxx-xx-xxTgarbage"}]',
    "impossible_date": '[{"id": 1, "serial_number": "0a1b", "not_before": "2024-02-30T00:00:00"}]',
    "empty_serial_no_id": '[{"serial_number": "", "not_before": "2024-09-14T00:00:00"}]',
    "nan_id": '[{"id": NaN, "not_before": "2024-09-14T00:00:00"}]',
    "top_level_object": '{"id": 1, "serial_number": "0a1b", "not_before": "2024-09-14T00:00:00"}',
}

# Official make-up workdays (调休上班), State Council notices:
# 2024: https://www.gov.cn/zhengce/content/202310/content_6911527.htm
# 2025: 国办发明电〔2024〕12号 (12 Nov 2024)
OFFICIAL_MAKEUP_2024_2025 = {
    "2024-02-04", "2024-02-18", "2024-04-07", "2024-04-28", "2024-05-11",
    "2024-09-14", "2024-09-29", "2024-10-12",
    "2025-01-26", "2025-02-08", "2025-04-27", "2025-09-28", "2025-10-11",
}

FETCH_DRIVER = r"""
import json, os, sys, urllib.request
sys.path.insert(0, os.environ["CF_TEST_SRC"])
def _no_network(*a, **k):
    raise AssertionError("network access attempted in test")
urllib.request.urlopen = _no_network
import fetch_ct
fetch_ct.RAW = os.environ["CF_TEST_RAW"]
fetch_ct.time.sleep = lambda s: None
responses = json.load(open(os.environ["CF_TEST_RESPONSES"]))
def fake_get(url, timeout=120):
    domain = url.split("q=", 1)[1].split("&", 1)[0]
    body = responses.get(domain)
    if body is None:
        raise OSError("simulated fetch failure for " + domain)
    return body.encode()
fetch_ct.get = fake_get
fetch_ct.main()
"""


def run_fetch(td, responses, cache=None):
    raw = os.path.join(td, "data", "raw")
    os.makedirs(raw, exist_ok=True)
    for dom, body in (cache or {}).items():
        with open(os.path.join(raw, dom + ".json"), "w") as fh:
            fh.write(body)
    resp = os.path.join(td, "responses.json")
    with open(resp, "w") as fh:
        json.dump(responses, fh)
    env = {**os.environ, "CF_TEST_SRC": SRC, "CF_TEST_RAW": raw, "CF_TEST_RESPONSES": resp}
    r = subprocess.run([sys.executable, "-c", FETCH_DRIVER], capture_output=True,
                       text=True, cwd=td, env=env, timeout=60)
    return r, raw


def run_parse(td, files):
    raw = os.path.join(td, "data", "raw")
    os.makedirs(raw, exist_ok=True)
    for dom, body in files.items():
        with open(os.path.join(raw, dom + ".json"), "w") as fh:
            fh.write(body)
    r = subprocess.run([sys.executable, os.path.join(SRC, "parse_ct.py")],
                       capture_output=True, text=True, cwd=td, timeout=60,
                       env={**os.environ, "CERT_FINGERPRINT_ROOT": td})
    return r


def full_panel(**overrides):
    files = {dom: VALID_BODY for dom in PANEL}
    files.update(overrides)
    return files


def assert_clean_fail(r, label):
    assert r.returncode != 0, f"{label}: silent success (exit 0)\nstdout={r.stdout[-800:]}"
    assert "Traceback" not in r.stderr, f"{label}: traceback instead of clean fail\n{r.stderr[-1500:]}"


# --------------------------------------------------------------------------- fetch

def test_fetch_positive_control_bytes_not_normalized():
    with tempfile.TemporaryDirectory() as td:
        r, raw = run_fetch(td, {dom: VALID_BODY for dom in PANEL})
        assert r.returncode == 0, (r.stdout[-800:], r.stderr[-800:])
        for dom in PANEL:
            assert open(os.path.join(raw, dom + ".json")).read() == VALID_BODY, dom


def test_fetch_rejects_malformed_or_empty_response():
    failures = []
    for name, body in BAD_BODIES.items():
        with tempfile.TemporaryDirectory() as td:
            responses = {dom: VALID_BODY for dom in PANEL}
            responses["baidu.com"] = body
            r, raw = run_fetch(td, responses)
            written = os.path.exists(os.path.join(raw, "baidu.com.json"))
            if r.returncode == 0 or "Traceback" in r.stderr or written \
                    or "FETCH_INCOMPLETE: 1/21" not in r.stderr:
                failures.append(f"{name}: exit={r.returncode} cache_written={written}")
    assert not failures, "bad crt.sh responses accepted:\n  " + "\n  ".join(failures)


def test_fetch_rejects_poisoned_cache():
    failures = []
    for name, body in BAD_BODIES.items():
        with tempfile.TemporaryDirectory() as td:
            responses = {dom: VALID_BODY for dom in PANEL if dom != "baidu.com"}  # baidu refetch fails
            r, _ = run_fetch(td, responses, cache={"baidu.com": body})
            if r.returncode == 0 or "Traceback" in r.stderr or "FETCH_INCOMPLETE: 1/21" not in r.stderr:
                failures.append(f"{name}: exit={r.returncode} skipped_as_valid={'skip  baidu.com' in r.stdout}")
    assert not failures, "poisoned cache accepted:\n  " + "\n  ".join(failures)


def test_fetch_partial_20_of_21_failures():
    with tempfile.TemporaryDirectory() as td:
        r, raw = run_fetch(td, {"baidu.com": VALID_BODY})
        assert_clean_fail(r, "20/21 fetch failures")
        assert "FETCH_INCOMPLETE: 20/21 domains failed" in r.stderr, r.stderr[-800:]
        assert sorted(os.listdir(raw)) == ["baidu.com.json"], os.listdir(raw)


# --------------------------------------------------------------------------- parse

def test_parse_rejects_malformed_or_empty_records():
    failures = []
    for name, body in BAD_BODIES.items():
        with tempfile.TemporaryDirectory() as td:
            r = run_parse(td, full_panel(**{"baidu.com": body}))
            if r.returncode == 0 or "Traceback" in r.stderr:
                tb = r.stderr.strip().splitlines()[-1] if "Traceback" in r.stderr else ""
                failures.append(f"{name}: exit={r.returncode} {tb}".rstrip())
    assert not failures, "parse_ct did not fail closed:\n  " + "\n  ".join(failures)


def test_parse_partial_raw_set_fails():
    with tempfile.TemporaryDirectory() as td:
        r = run_parse(td, {"baidu.com": VALID_BODY})  # 20 of 21 panel domains missing
        assert_clean_fail(r, "1/21 raw files present")


def test_parse_hand_derived_ground_truth():
    """Ground truth computed by hand from the documented statistic, not from the code.

    makeup days: 2024-09-14 (Sat) 6 unique (+1 duplicate serial), 2024-10-12 (Sat) 4
      -> makeup median = (6+4)/2 = 5
    ordinary weekend days: 2024-09-07 Sat 1, 2024-09-08 Sun 2, 2024-09-21 Sat 3 -> median 2
    weekday 2024-09-10 (Tue) 50 -> must be ignored by the statistic
    uplift = 5/2 = 2.5 ; unique certs = 6+4+1+2+3+50 = 66
    """
    rows, n = [], 0
    for day, count in [("2024-09-14", 6), ("2024-10-12", 4), ("2024-09-07", 1),
                       ("2024-09-08", 2), ("2024-09-21", 3), ("2024-09-10", 50)]:
        for _ in range(count):
            n += 1
            rows.append({"id": n, "serial_number": f"{n:04x}", "not_before": day + "T08:00:00"})
    rows.append({"id": 999, "serial_number": "0001", "not_before": "2024-09-14T09:00:00"})  # dup serial
    with tempfile.TemporaryDirectory() as td:
        r = run_parse(td, full_panel(**{"baidu.com": json.dumps(rows)}))
        assert r.returncode == 0, (r.stdout[-800:], r.stderr[-800:])
        got = json.load(open(os.path.join(td, "results", "daily_counts.json")))["domains"]["baidu.com"]
        assert got["unique_certs"] == 66, got
        assert got["makeup_median_daily"] == 5, got
        assert got["ordinary_weekend_median_daily"] == 2, got
        assert got["makeup_uplift"] == 2.5, got


def test_makeup_dates_are_official_weekend_workdays():
    from parse_ct import MAKEUP
    wrong = sorted(d for d in MAKEUP if d not in OFFICIAL_MAKEUP_2024_2025
                   or dt.date.fromisoformat(d).weekday() < 5)
    assert not wrong, f"MAKEUP contains dates that are not official make-up workdays: {wrong}"


TESTS = [v for k, v in list(globals().items()) if k.startswith("test_") and callable(v)]

if __name__ == "__main__":
    failed = 0
    for t in TESTS:
        try:
            t()
            print(f"PASS {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL {t.__name__}: {e}")
        except Exception:
            failed += 1
            print(f"ERROR {t.__name__}:\n{traceback.format_exc()}")
    print(f"{len(TESTS) - failed}/{len(TESTS)} passed")
    sys.exit(1 if failed else 0)
