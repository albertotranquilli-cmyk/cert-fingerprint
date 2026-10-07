#!/usr/bin/env python3
"""Step 1: download CT certificate data from crt.sh for the domain panel.

Public JSON API, no key. Rate-limited: sleep between queries, retry on 429/5xx.
Raw JSON cached under data/raw/<domain>.json.

Usage: python src/fetch_ct.py
"""
import json, os, sys, time, urllib.request, urllib.error

from ct_validate import InvalidCTData, load_records

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw")
BASE = "https://crt.sh/?q={domain}&output=json"

PANEL = {
    # Chinese domains (expected: makeup-day spikes)
    "baidu.com": "cn",
    "alibaba.com": "cn",
    "aliyuncs.com": "cn",
    "qq.com": "cn",
    "weixin.qq.com": "cn",
    "bytedance.com": "cn",
    "douyin.com": "cn",
    "jd.com": "cn",
    "netease.com": "cn",
    "163.com": "cn",
    "huawei.com": "cn",
    "xiaomi.com": "cn",
    # Western controls (expected: flat on makeup days)
    "amazon.com": "us",
    "google.com": "us",
    "microsoft.com": "us",
    "apple.com": "us",
    "github.com": "us",
    "cloudflare.com": "us",
    # Japanese negative control (UTC+9, no make-up days)
    "yahoo.co.jp": "jp",
    "rakuten.co.jp": "jp",
    "line.me": "jp",
}

SLEEP = 5.0  # seconds between queries


def get(url, timeout=120):
    req = urllib.request.Request(url, headers={"User-Agent": "cert-fingerprint/0.1 (research)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    os.makedirs(RAW, exist_ok=True)
    ok = fail = 0
    for domain, region in PANEL.items():
        path = os.path.join(RAW, f"{domain}.json")
        if os.path.exists(path):
            try:
                with open(path, "rb") as fh:
                    load_records(fh.read())
                print(f"skip  {domain} ({os.path.getsize(path)/1e6:.1f} MB, validated)", flush=True)
                ok += 1
                continue
            except (InvalidCTData, ValueError, OSError) as e:
                print(f"invalid cache {domain} ({type(e).__name__}: {e}); refetching", flush=True)
        url = BASE.format(domain=domain)
        print(f"get   {domain} ({region}) ...", flush=True)
        success = False
        for attempt in range(4):
            try:
                b = get(url)
                data = load_records(b)  # raises on malformed/empty; never written to cache
                tmp = path + ".tmp"
                with open(tmp, "wb") as fh:
                    fh.write(b)
                    fh.flush()
                    os.fsync(fh.fileno())
                os.replace(tmp, path)
                print(f"  -> {len(data)} entries, {len(b)/1e6:.1f} MB", flush=True)
                ok += 1
                success = True
                break
            except urllib.error.HTTPError as e:
                print(f"  HTTP {e.code}, retry {attempt+1}/4 in {SLEEP*(attempt+1):.0f}s", flush=True)
                time.sleep(SLEEP * (attempt + 1))
            except Exception as e:
                print(f"  ERR {type(e).__name__}: {e}, retry {attempt+1}/4", flush=True)
                time.sleep(SLEEP * (attempt + 1))
        if not success:
            fail += 1
            print(f"  FAILED {domain} after 4 attempts", flush=True)
        time.sleep(SLEEP)
    print(f"done: {ok} ok, {fail} failed", flush=True)
    if fail:
        print(f"FETCH_INCOMPLETE: {fail}/{len(PANEL)} domains failed (cause may be environment or upstream)", file=sys.stderr, flush=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
