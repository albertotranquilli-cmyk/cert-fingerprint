#!/usr/bin/env python3
"""Unit tests for fetch_ct.py and parse_ct.py — no network required."""
import importlib.util, os, pathlib, sys, json, datetime as dt, tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "src" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def test_fetch_ct_structure():
    src = (ROOT / "src" / "fetch_ct.py").read_text()
    assert "PANEL" in src and "def get(" in src
    assert "crt.sh" in src
    print("fetch_ct.py: structure OK")

def test_bin_day():
    pc = load("parse_ct")
    assert pc.bin_day("2024-06-15T00:00:00Z") == "2024-06-15"
    assert pc.bin_day("2024-06-15T23:59:59Z") == "2024-06-15"
    assert pc.bin_day("") is None
    print("bin_day: OK")

def test_parse_ct_empty_raw():
    pc = load("parse_ct")
    with tempfile.TemporaryDirectory() as td:
        old_raw, old_out = pc.RAW, pc.OUT
        pc.RAW = os.path.join(td, "raw")
        pc.OUT = os.path.join(td, "out")
        os.makedirs(pc.RAW)
        pc.main()
        s = json.load(open(os.path.join(pc.OUT, "daily_counts.json")))
        assert "error" in s
        pc.RAW, pc.OUT = old_raw, old_out
    print("parse_ct.py: empty-raw OK")

def test_parse_ct_synthetic():
    pc = load("parse_ct")
    with tempfile.TemporaryDirectory() as td:
        old_raw, old_out = pc.RAW, pc.OUT
        pc.RAW = os.path.join(td, "raw")
        pc.OUT = os.path.join(td, "out")
        os.makedirs(pc.RAW)
        certs = [
            {"serial_number": "1", "not_before": "2024-06-15T10:00:00Z"},
            {"serial_number": "2", "not_before": "2024-06-15T14:00:00Z"},
            {"serial_number": "3", "not_before": "2024-06-15T20:00:00Z"},
            {"serial_number": "4", "not_before": "2024-06-08T10:00:00Z"},
            {"serial_number": "1", "not_before": "2024-06-15T10:00:00Z"},
        ]
        json.dump(certs, open(os.path.join(pc.RAW, "baidu.com.json"), "w"))
        pc.main()
        s = json.load(open(os.path.join(pc.OUT, "daily_counts.json")))
        d = s["domains"]["baidu.com"]
        assert d["unique_certs"] == 4, d
        assert d["makeup_median_daily"] == 3, d
        assert d["ordinary_weekend_median_daily"] == 1, d
        assert d["makeup_uplift"] == 3.0, d
        pc.RAW, pc.OUT = old_raw, old_out
    print("parse_ct.py: synthetic OK")

if __name__ == "__main__":
    test_fetch_ct_structure()
    test_bin_day()
    test_parse_ct_empty_raw()
    test_parse_ct_synthetic()
    print("ALL TESTS PASSED")
