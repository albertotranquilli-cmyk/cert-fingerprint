#!/usr/bin/env python3
"""Step 1: download CT certificate data from crt.sh for the domain panel.

Public JSON API, no key. Rate-limited: sleep between queries, retry on 429/5xx.
Raw JSON cached under data/raw/<domain>.json.

Usage: python src/fetch_ct.py
"""
import json, os, sys, time, urllib.request, urllib.error

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


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "cert-fingerprint/0.1 (research)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def main():
    os.makedirs(RAW, exist_ok=True)
    for domain, region in PANEL.items():
        path = os.path.join(RAW, f"{domain}.json")
        if os.path.exists(path) and os.path.getsize(path) > 100:
            print(f"skip  {domain} ({os.path.getsize(path)/1e6:.1f} MB)")
            continue
        url = BASE.format(domain=domain)
        print(f"get   {domain} ({region}) ...", flush=True)
        for attempt in range(4):
            try:
                b = get(url)
                open(path, "wb").write(b)
                # sanity: must be JSON array
                data = json.loads(b)
                print(f"  -> {len(data)} entries, {len(b)/1e6:.1f} MB")
                break
            except urllib.error.HTTPError as e:
                print(f"  HTTP {e.code}, retry {attempt+1}/4 in {SLEEP*(attempt+1):.0f}s")
                time.sleep(SLEEP * (attempt + 1))
            except Exception as e:
                print(f"  ERR {type(e).__name__}: {e}, retry {attempt+1}/4")
                time.sleep(SLEEP * (attempt + 1))
        time.sleep(SLEEP)
    print("done")


if __name__ == "__main__":
    main()
