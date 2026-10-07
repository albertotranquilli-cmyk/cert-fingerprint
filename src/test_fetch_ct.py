#!/usr/bin/env python3
"""Unit tests for cert-fingerprint (no network)."""
import json, os, subprocess, sys, tempfile, shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
sys.path.insert(0, SRC)


def test_fetch_ct_structure():
    src = open(os.path.join(SRC, "fetch_ct.py")).read()
    assert "PANEL" in src and "crt.sh" in src
    assert "SLEEP" in src
    print("fetch_ct.py: structure OK")


def test_bin_day():
    from parse_ct import bin_day
    assert bin_day("2024-06-15T12:00:00") == "2024-06-15"
    assert bin_day("") is None
    assert bin_day(None) is None
    print("bin_day: OK")


def test_parse_ct_empty_raw():
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "data", "raw")
        os.makedirs(raw)
        r = subprocess.run([sys.executable, os.path.join(SRC, "parse_ct.py")],
                           capture_output=True, text=True, cwd=td,
                           env={**os.environ, "CERT_FINGERPRINT_ROOT": td})
        assert r.returncode == 2, r.stderr
        assert "no .json files in data/raw/" in r.stdout, (r.stdout, r.stderr)
        print("parse_ct.py: empty-raw OK")


def test_parse_ct_synthetic():
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "data", "raw")
        os.makedirs(raw)
        # 2024-09-14 (Sat) is an official make-up workday; 2024-06-15 is not.
        # Hand-derived: 13 certs on 2024-09-14, 1 on Sun 2024-09-15, Mon/Tue ignored -> 13/1 = 13.0
        synth = [{"serial_number": f"s{i}", "not_before": f"2024-09-14T{i%24:02d}:00:00"} for i in range(12)]
        synth += [{"serial_number": f"w{i}", "not_before": f"2024-09-1{4+i}T{i%24:02d}:00:00"} for i in range(4)]
        json.dump(synth, open(os.path.join(raw, "baidu.com.json"), "w"))
        # Full panel present so the run is not a partial-input run.
        from fetch_ct import PANEL
        for dom in PANEL:
            if dom != "baidu.com":
                json.dump([{"id": 1, "serial_number": "01", "not_before": "2024-09-07T10:00:00"}],
                          open(os.path.join(raw, dom + ".json"), "w"))
        r = subprocess.run([sys.executable, os.path.join(SRC, "parse_ct.py")],
                           capture_output=True, text=True, cwd=td,
                           env={**os.environ, "CERT_FINGERPRINT_ROOT": td})
        assert r.returncode == 0, r.stderr
        result = json.load(open(os.path.join(td, "results", "daily_counts.json")))
        assert result["domains"]["baidu.com"]["makeup_uplift"] == 13.0, result
        print("parse_ct.py: synthetic OK")
        print(r.stdout)


if __name__ == "__main__":
    test_fetch_ct_structure()
    test_bin_day()
    test_parse_ct_empty_raw()
    test_parse_ct_synthetic()
    # Fail-closed regressions (PR #1 audit). Run from this entrypoint so the
    # existing CI step executes them without a workflow change.
    sys.stdout.flush()
    r = subprocess.run([sys.executable, os.path.join(SRC, "test_regressions.py")])
    if r.returncode != 0:
        print("REGRESSION TESTS FAILED")
        sys.exit(r.returncode)
    print("ALL TESTS PASSED")
