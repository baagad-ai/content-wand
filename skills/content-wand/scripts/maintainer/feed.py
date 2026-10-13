#!/usr/bin/env python3
"""Publisher tooling for the signed platform-spec feed. Not used at runtime.

    feed.py keygen   --out ~/.content-wand-publisher      # once; keep the secret offline
    feed.py build    [--data-version YYYY.MM.DD] [--summary TEXT]
    feed.py sign     --key <secret-file>                  # writes feed/specs-feed.json.sig
    feed.py verify

`build` snapshots data/platform-specs.json into feed/specs-feed.json. Edit the
facts first (after verifying them against official sources), bump
data_version, then build, sign and commit feed/ and data/updater-pubkey.b64.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from cwlib import ed25519  # noqa: E402

REPO = ROOT.parents[1]
FEED = REPO / "feed" / "specs-feed.json"
SIG = REPO / "feed" / "specs-feed.json.sig"
PUBKEY = ROOT / "data" / "updater-pubkey.b64"
SPECS = ROOT / "data" / "platform-specs.json"
KEEP = {"value", "kind", "verified_at", "source", "source_type", "note"}


def cmd_keygen(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser()
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    secret_file = out / "content-wand-feed.secret"
    if secret_file.exists() and not args.force:
        print(f"refusing to overwrite {secret_file}", file=sys.stderr)
        return 1
    seed = secrets.token_bytes(32)
    fd = os.open(secret_file, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as fh:
        fh.write(base64.b64encode(seed).decode() + "\n")
    PUBKEY.write_text(base64.b64encode(ed25519.public_key(seed)).decode() + "\n", encoding="ascii")
    print(f"secret key: {secret_file} (never commit this)\npublic key: {PUBKEY} (commit this)")
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    data = json.loads(SPECS.read_text(encoding="utf-8"))
    bundle = {
        "feed_version": 1,
        "data_version": args.data_version or data["data_version"],
        "published_at": dt.date.today().isoformat(),
        "platforms": {pid: {"facts": {k: {kk: vv for kk, vv in f.items() if kk in KEEP} for k, f in p["facts"].items()}} for pid, p in data["platforms"].items()},
    }
    if args.summary:
        bundle["summary"] = args.summary
    FEED.parent.mkdir(parents=True, exist_ok=True)
    FEED.write_bytes((json.dumps(bundle, indent=1, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8"))
    print(f"wrote {FEED} (data_version {bundle['data_version']})")
    return 0


def cmd_sign(args: argparse.Namespace) -> int:
    seed = base64.b64decode(Path(args.key).expanduser().read_text().strip())
    payload = FEED.read_bytes()
    SIG.write_text(base64.b64encode(ed25519.sign(seed, payload)).decode() + "\n", encoding="ascii")
    print(f"signed {FEED.name} -> {SIG.name}")
    return 0


def cmd_verify(_: argparse.Namespace) -> int:
    key = base64.b64decode(PUBKEY.read_text().strip())
    sig = base64.b64decode(SIG.read_text().strip())
    ok = ed25519.verify(key, FEED.read_bytes(), sig)
    print("signature OK" if ok else "signature INVALID")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("keygen")
    k.add_argument("--out", required=True)
    k.add_argument("--force", action="store_true")
    b = sub.add_parser("build")
    b.add_argument("--data-version")
    b.add_argument("--summary")
    s = sub.add_parser("sign")
    s.add_argument("--key", required=True)
    sub.add_parser("verify")
    args = ap.parse_args()
    return {"keygen": cmd_keygen, "build": cmd_build, "sign": cmd_sign, "verify": cmd_verify}[args.cmd](args)


if __name__ == "__main__":
    raise SystemExit(main())
