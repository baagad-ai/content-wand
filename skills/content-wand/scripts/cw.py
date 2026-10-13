#!/usr/bin/env python3
"""content-wand command line: the deterministic half of the skill.

The model writes. This program counts, checks, stores and guards. Every
command prints one JSON document on stdout. Exit codes:

    0  success
    1  usage error or failed operation
    3  content failed a compliance check (nothing was saved)
    4  needs a human decision (for example a suspicious URL)

Standard library only. Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from cwlib import __version__, claims, hooks, ingest, links, output, paths, scan, session, specs, styles, updater, urlguard, validate  # noqa: E402
from cwlib.jsonio import emit  # noqa: E402

MAX_INPUT = 4_000_000


def read_input(arg: str | None) -> str:
    if arg and arg != "-":
        p = Path(arg).expanduser()
        if p.stat().st_size > MAX_INPUT:
            raise ValueError("input file is larger than 4 MB")
        return p.read_text(encoding="utf-8", errors="replace")
    data = sys.stdin.read(MAX_INPUT + 1)
    if len(data) > MAX_INPUT:
        raise ValueError("stdin input is larger than 4 MB")
    return data


def done(obj: Any, code: int = 0) -> int:
    emit(obj)
    return code


def parse_jsonish(raw: str) -> Any:
    try:
        return json.loads(raw)
    except ValueError:
        return raw


def cwd_of(args: argparse.Namespace) -> Path:
    return Path(getattr(args, "cwd", None) or os.getcwd()).resolve()


def cmd_version(_: argparse.Namespace) -> int:
    data = specs.load_base()
    return done({"ok": True, "version": __version__, "specs_data_version": data.get("data_version"), "python": sys.version.split()[0], "state_dir": str(paths.state_dir())})


def cmd_preflight(args: argparse.Namespace) -> int:
    notices: list[str] = []
    sid = args.session or ""
    guards = "prompt-only"
    if sid and session.SESSION_ID_RE.match(sid):
        prior = session.info(sid)
        if prior and prior.get("via") == "hook":
            guards = "hooks"
        else:
            session.activate(sid, str(cwd_of(args)), via="agent")
    elif sid:
        notices.append("session id was not substituted by the host; guard hooks cannot be confirmed")
    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()] if args.platforms else None
    spec_status = specs.status(platforms)
    state = styles.setup_state()
    pending = updater.pending_path().exists()
    if spec_status["unknown_platforms"]:
        notices.append("unknown platforms: " + ", ".join(spec_status["unknown_platforms"]))
    stale_hard = [pid for pid, e in spec_status["platforms"].items() if any(s["kind"] in ("hard", "policy") for s in e["stale_facts"])]
    if stale_hard:
        notices.append("platform limits not re-verified within their review window: " + ", ".join(stale_hard))
    if state.get("legacy_found") and state["count"] == 0:
        notices.append("Writing Styles from an earlier version were found and can be migrated")
    cfg = styles.load_config()
    return done({
        "ok": True,
        "version": __version__,
        "guards": guards,
        "style": state,
        "specs": {
            "data_version": spec_status["data_version"],
            "stale_platforms": spec_status["stale_platforms"],
            "stale_hard_or_policy": stale_hard,
            "unknown_platforms": spec_status["unknown_platforms"],
            "pending_update": pending,
        },
        "updates": {"opted_in": updater.user_opted_in(), "feed_available": updater.public_key() is not None},
        "preferences": cfg.get("preferences", {}),
        "notices": notices,
    })


def cmd_session(args: argparse.Namespace) -> int:
    if args.action == "start":
        res = session.activate(args.id, str(cwd_of(args)), via="agent")
        return done(res, 0 if res["ok"] else 1)
    return done(session.info(args.id) or {"active": False})


def cmd_check_url(args: argparse.Namespace) -> int:
    res = urlguard.check_url(args.url, resolve=not args.no_resolve)
    return done(res, {"allow": 0, "ask": 4, "deny": 1}[res["decision"]])


def cmd_ingest(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser().resolve() if args.out else None
    if out is not None and not output._inside_root(out.parent, cwd_of(args)):
        return done({"ok": False, "error": "--out must be inside content-output/"}, 1)
    if args.url:
        res = ingest.ingest_url(args.url, out, confirmed=args.confirmed)
        code = 0 if res["ok"] else (4 if res.get("fetch_status") == "needs-confirmation" else 1)
    elif args.file:
        res = ingest.ingest_file(Path(args.file), out)
        code = 0 if res["ok"] else 1
    else:
        res = ingest.ingest_text(read_input(None), out)
        code = 0 if res["ok"] else 1
    return done(res, code)


def cmd_scan(args: argparse.Namespace) -> int:
    text = read_input(args.file)
    res = scan.scan_text(text)
    if args.sanitize:
        cleaned, report = scan.sanitise_source(text)
        res["sanitised"] = cleaned
        res["sanitise_report"] = report
    return done(res)


def cmd_validate(args: argparse.Namespace) -> int:
    res = validate.validate_text(args.platform, read_input(args.file))
    return done(res, 3 if res["compliance"] == "fail" else 0)


def cmd_validate_dir(args: argparse.Namespace) -> int:
    res = validate.validate_dir(Path(args.dir))
    return done(res, 3 if res["compliance"] == "fail" else 0)


def cmd_lint_ai(args: argparse.Namespace) -> int:
    return done(validate.lint_ai_patterns(read_input(args.file)))


def cmd_claims(args: argparse.Namespace) -> int:
    src = Path(args.source).expanduser().read_text(encoding="utf-8", errors="replace")
    out = read_input(args.output)
    return done(claims.check_claims(src, out, args.allow_url or []))


def cmd_utm(args: argparse.Namespace) -> int:
    res = links.add_utm(args.url, args.platform, args.campaign, args.content or "")
    return done(res, 0 if res["ok"] else 1)


def cmd_style(args: argparse.Namespace) -> int:
    a = args.action
    if a == "list":
        return done(styles.list_styles())
    if a == "state":
        return done(styles.setup_state())
    if a == "read":
        res = styles.read_style(args.name)
        return done(res, 0 if res["ok"] else 1)
    if a == "write":
        raw = read_input(args.file)
        style = json.loads(raw)
        res = styles.write_style(style, make_default=True if args.default else None)
        return done(res, 0 if res["ok"] else 1)
    if a == "validate":
        return done(styles.validate_style(json.loads(read_input(args.file))))
    if a == "delete":
        res = styles.delete_style(args.name)
        return done(res, 0 if res["ok"] else 1)
    if a == "rename":
        res = styles.rename_style(args.name, args.new_name)
        return done(res, 0 if res["ok"] else 1)
    if a == "decline":
        return done(styles.decline_setup())
    if a == "migrate-legacy":
        return done(styles.migrate_legacy())
    if a == "reset":
        if not args.yes:
            return done({"ok": False, "error": "pass --yes to erase all saved settings and styles"}, 1)
        return done(styles.reset_all())
    return done({"ok": False, "error": "unknown style action"}, 1)


def cmd_pref(args: argparse.Namespace) -> int:
    if args.action == "get":
        return done({"ok": True, "preferences": styles.load_config().get("preferences", {})})
    res = styles.set_preference(args.key, parse_jsonish(args.value))
    return done(res, 0 if res["ok"] else 1)


def cmd_output(args: argparse.Namespace) -> int:
    cwd = cwd_of(args)
    a = args.action
    if a == "new":
        res = output.create_run_dir(cwd, args.title)
        if res["ok"]:
            output.update_manifest_create(Path(res["dir"]), {"title": args.title, "specs_data_version": specs.load_base().get("data_version")})
        return done(res, 0 if res["ok"] else 1)
    run_dir = Path(args.dir).expanduser().resolve()
    if not output._inside_root(run_dir, cwd):
        return done({"ok": False, "error": "directory is outside content-output/"}, 1)
    if a == "save":
        text = read_input(args.file)
        if scan.SECRET_TOKEN_RE.search(text):
            return done({"ok": False, "error": "the text contains something that looks like an API key or private key; it was not saved"}, 3)
        pid = specs.canonical_platform(args.name)
        validation = validate.validate_text(pid, text) if pid in validate.DEFAULTS else None
        claim_result = None
        if args.source:
            src = Path(args.source).expanduser().read_text(encoding="utf-8", errors="replace")
            claim_result = claims.check_claims(src, text, args.allow_url or [])
        res = output.save_file(cwd, run_dir, pid, text, validation, claim_result)
        res["validation"] = validation
        res["claims"] = claim_result
        return done(res, 0 if res["ok"] else 3)
    if a == "meta":
        res = output.update_manifest(run_dir, json.loads(args.json))
        return done(res, 0 if res["ok"] else 1)
    if a == "review":
        names = ["all"] if args.names == "all" else [n.strip() for n in args.names.split(",") if n.strip()]
        res = output.review(run_dir, names, args.status, args.note or "", accept_unsupported_claims=args.accept_unsupported_claims)
        session.audit("review", args.status, "", "cw.py", ",".join(names)[:100])
        return done(res, 0 if res["ok"] else 1)
    if a == "status":
        return done(output.run_status(run_dir))
    if a == "packet":
        res = output.packet(run_dir)
        return done(res, 0 if res["ok"] else 1)
    return done({"ok": False, "error": "unknown output action"}, 1)


def cmd_specs(args: argparse.Namespace) -> int:
    a = args.action
    if a == "status":
        return done(specs.status([p.strip() for p in args.platforms.split(",")] if args.platforms else None))
    if a == "show":
        res = specs.show(args.platform)
        return done(res, 0 if res["ok"] else 1)
    if a == "sources":
        pid = specs.canonical_platform(args.platform)
        data = specs.merged()
        p = data["platforms"].get(pid)
        if p is None:
            return done({"ok": False, "error": "unknown platform"}, 1)
        stale = specs.status([pid])["platforms"][pid]["stale_facts"]
        return done({
            "ok": True,
            "platform": pid,
            "official_domains": p.get("primary_domains", []),
            "official_url_prefixes": p.get("primary_url_prefixes", []),
            "stale_facts": stale,
            "facts": {k: {"value": f["value"], "kind": f["kind"], "source": f.get("source", ""), "verified_at": f.get("verified_at")} for k, f in p["facts"].items()},
            "rule": "Only official domains or prefixes may support hard or policy facts. Quote the exact sentence containing the value.",
        })
    if a in ("validate-proposal", "apply"):
        proposal = json.loads(read_input(args.file))
        res = specs.validate_proposal(proposal) if a == "validate-proposal" else specs.apply_proposal(proposal)
        return done(res, 0 if res["ok"] else 1)
    if a == "rollback":
        res = specs.rollback()
        return done(res, 0 if res["ok"] else 1)
    if a == "check-remote":
        res = updater.check_remote(force=args.force)
        return done(res, 0 if res["ok"] else 1)
    if a == "pending":
        res = updater.pending_summary()
        return done(res, 0 if res["ok"] else 1)
    if a == "apply-remote":
        res = updater.apply_pending()
        return done(res, 0 if res["ok"] else 1)
    if a == "discard-remote":
        return done(updater.discard_pending())
    return done({"ok": False, "error": "unknown specs action"}, 1)


def cmd_audit(args: argparse.Namespace) -> int:
    return done({"ok": True, "entries": session.audit_tail(args.n)})


def cmd_hook(args: argparse.Namespace) -> int:
    code, out = hooks.run(args.event, sys.stdin.read(MAX_INPUT))
    if out:
        sys.stdout.write(out + "\n")
    return code


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(prog="cw.py", description="content-wand deterministic toolkit")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sub.add_parser("version").set_defaults(fn=cmd_version)

    p = sub.add_parser("preflight", help="one call that reports everything needed before starting")
    p.add_argument("--session", default="")
    p.add_argument("--platforms", default="")
    p.add_argument("--cwd")
    p.set_defaults(fn=cmd_preflight)

    p = sub.add_parser("session")
    p.add_argument("action", choices=["start", "info"])
    p.add_argument("--id", required=True)
    p.add_argument("--cwd")
    p.set_defaults(fn=cmd_session)

    p = sub.add_parser("check-url")
    p.add_argument("url")
    p.add_argument("--no-resolve", action="store_true")
    p.set_defaults(fn=cmd_check_url)

    p = sub.add_parser("ingest", help="fetch a URL or read a file into clean, scanned source text")
    g = p.add_mutually_exclusive_group()
    g.add_argument("--url")
    g.add_argument("--file")
    p.add_argument("--out", help="write the cleaned text here (must be inside content-output/)")
    p.add_argument("--confirmed", action="store_true", help="the user approved a flagged URL")
    p.add_argument("--cwd")
    p.set_defaults(fn=cmd_ingest)

    p = sub.add_parser("scan")
    p.add_argument("file", nargs="?")
    p.add_argument("--sanitize", action="store_true")
    p.set_defaults(fn=cmd_scan)

    p = sub.add_parser("validate")
    p.add_argument("platform")
    p.add_argument("file", nargs="?")
    p.set_defaults(fn=cmd_validate)

    p = sub.add_parser("validate-dir")
    p.add_argument("dir")
    p.set_defaults(fn=cmd_validate_dir)

    p = sub.add_parser("lint-ai")
    p.add_argument("file", nargs="?")
    p.set_defaults(fn=cmd_lint_ai)

    p = sub.add_parser("claims")
    p.add_argument("--source", required=True)
    p.add_argument("--output", default="-")
    p.add_argument("--allow-url", action="append")
    p.set_defaults(fn=cmd_claims)

    p = sub.add_parser("utm")
    p.add_argument("url")
    p.add_argument("--platform", required=True)
    p.add_argument("--campaign", required=True)
    p.add_argument("--content")
    p.set_defaults(fn=cmd_utm)

    p = sub.add_parser("style")
    p.add_argument("action", choices=["list", "state", "read", "write", "validate", "delete", "rename", "decline", "migrate-legacy", "reset"])
    p.add_argument("name", nargs="?")
    p.add_argument("new_name", nargs="?")
    p.add_argument("--file")
    p.add_argument("--default", action="store_true")
    p.add_argument("--yes", action="store_true")
    p.set_defaults(fn=cmd_style)

    p = sub.add_parser("pref")
    p.add_argument("action", choices=["get", "set"])
    p.add_argument("key", nargs="?")
    p.add_argument("value", nargs="?")
    p.set_defaults(fn=cmd_pref)

    p = sub.add_parser("output")
    p.add_argument("action", choices=["new", "save", "meta", "review", "status", "packet"])
    p.add_argument("--title")
    p.add_argument("--dir")
    p.add_argument("--name")
    p.add_argument("--file")
    p.add_argument("--source")
    p.add_argument("--allow-url", action="append")
    p.add_argument("--json")
    p.add_argument("--names", default="all")
    p.add_argument("--status", choices=["approved", "rejected", "draft"])
    p.add_argument("--note")
    p.add_argument("--accept-unsupported-claims", action="store_true")
    p.add_argument("--cwd")
    p.set_defaults(fn=cmd_output)

    p = sub.add_parser("specs")
    p.add_argument("action", choices=["status", "show", "sources", "validate-proposal", "apply", "rollback", "check-remote", "pending", "apply-remote", "discard-remote"])
    p.add_argument("platform", nargs="?")
    p.add_argument("--platforms")
    p.add_argument("--file")
    p.add_argument("--force", action="store_true")
    p.set_defaults(fn=cmd_specs)

    p = sub.add_parser("audit")
    p.add_argument("action", choices=["tail"])
    p.add_argument("-n", type=int, default=20)
    p.set_defaults(fn=cmd_audit)

    p = sub.add_parser("hook")
    p.add_argument("event", choices=sorted(hooks.HANDLERS))
    p.set_defaults(fn=cmd_hook)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.cmd == "hook":
        return args.fn(args)
    try:
        return args.fn(args)
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        return done({"ok": False, "error": f"{type(exc).__name__}: {exc}"}, 1)


if __name__ == "__main__":
    raise SystemExit(main())
