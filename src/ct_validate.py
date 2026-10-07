#!/usr/bin/env python3
"""Strict, non-normalizing validation of crt.sh JSON (shared by fetch and parse).

Structural/semantic checks only, not cryptographic. Any violation raises
InvalidCTData; callers must treat that as a failure, never as data.
"""
import datetime as dt
import json
import re


class InvalidCTData(ValueError):
    pass


_NOT_BEFORE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?")


def _reject_constant(name):
    raise InvalidCTData(f"non-standard JSON constant {name}")


def strict_loads(raw):
    """json.loads that rejects NaN/Infinity/-Infinity instead of accepting them."""
    return json.loads(raw, parse_constant=_reject_constant)


def validate_records(data):
    if not isinstance(data, list):
        raise InvalidCTData("top-level JSON value is not a list")
    if not data:
        raise InvalidCTData("empty certificate list")
    for i, row in enumerate(data):
        if not isinstance(row, dict):
            raise InvalidCTData(f"row {i}: not a JSON object")
        nb = row.get("not_before")
        if not isinstance(nb, str) or not _NOT_BEFORE.fullmatch(nb):
            raise InvalidCTData(f"row {i}: invalid not_before {nb!r}")
        try:
            dt.datetime.strptime(nb[:19], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise InvalidCTData(f"row {i}: impossible not_before {nb!r}") from None
        ser, cid = row.get("serial_number"), row.get("id")
        has_serial = isinstance(ser, str) and ser != ""
        has_id = isinstance(cid, int) and not isinstance(cid, bool)
        if not (has_serial or has_id):
            raise InvalidCTData(f"row {i}: no usable serial_number or id")
    return data


def load_records(raw):
    return validate_records(strict_loads(raw))
