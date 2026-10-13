"""URL safety checks for anything the skill (or a hook) is about to fetch.

Goals
- Block SSRF: loopback, private, link-local, CGNAT, cloud metadata, reserved
  ranges, in every spelling an attacker might use (decimal, hex, octal, short
  forms, IPv4-mapped IPv6, bracketed IPv6, trailing dots, userinfo tricks).
- Flag likely data-exfiltration URLs (long/high-entropy query strings, secret
  look-alikes) so a human can approve them.

DNS rebinding cannot be fully solved by a pre-flight check because the fetch
itself happens later in another process. Resolution is therefore best effort
and every resolved address must be globally routable.
"""

from __future__ import annotations

import ipaddress
import math
import re
import socket
from typing import Any
from urllib.parse import parse_qsl, urlsplit

MAX_URL_LENGTH = 2048
ALLOWED_SCHEMES = {"http", "https"}
STANDARD_PORTS = {None, 80, 443}

BLOCKED_HOST_SUFFIXES = (
    ".localhost",
    ".local",
    ".internal",
    ".intranet",
    ".lan",
    ".home",
    ".corp",
    ".private",
    ".home.arpa",
    ".localdomain",
)
BLOCKED_HOSTS = {
    "localhost",
    "metadata",
    "metadata.google.internal",
    "instance-data",
    "kubernetes.default.svc",
}

SECRET_PATTERNS = [
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{10,}"),
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"),
]

_NUMERIC_HOST = re.compile(r"^[0-9a-fA-FxX.]+$")
_CONTROL = re.compile(r"[\x00-\x20\x7f\\]")


def _entropy(s: str) -> float:
    if not s:
        return 0.0
    counts: dict[str, int] = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


def _result(decision: str, reason: str, **extra: Any) -> dict[str, Any]:
    out = {"decision": decision, "ok": decision != "deny", "reason": reason}
    out.update(extra)
    return out


def _ip_is_public(ip: ipaddress._BaseAddress) -> bool:
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.ipv4_mapped is not None:
            return _ip_is_public(ip.ipv4_mapped)
        if ip.sixtofour is not None:
            return _ip_is_public(ip.sixtofour)
        if ip.teredo is not None:
            return False
        # NAT64 well-known prefix embeds an IPv4 address in the low 32 bits.
        if ip in ipaddress.ip_network("64:ff9b::/96"):
            return _ip_is_public(ipaddress.IPv4Address(int(ip) & 0xFFFFFFFF))
    if str(ip) == "169.254.169.254":
        return False
    return bool(ip.is_global) and not ip.is_multicast


def parse_host_ip(host: str) -> ipaddress._BaseAddress | None:
    """Return an IP object if `host` is an IP literal in any common spelling."""
    h = host.strip("[]")
    try:
        return ipaddress.ip_address(h)
    except ValueError:
        pass
    if ":" in h:
        try:
            return ipaddress.ip_address(h.split("%", 1)[0])
        except ValueError:
            return None
    if _NUMERIC_HOST.match(h) and (h[0].isdigit()):
        try:
            return ipaddress.IPv4Address(socket.inet_ntoa(socket.inet_aton(h)))
        except (OSError, ValueError):
            pass
        try:
            if h.lower().startswith("0x"):
                return ipaddress.IPv4Address(int(h, 16))
            if h.isdigit():
                return ipaddress.IPv4Address(int(h, 10))
        except ValueError:
            return None
    return None


def check_url(url: str, resolve: bool = True) -> dict[str, Any]:
    """Classify a URL as allow / ask / deny.

    deny: unsafe (SSRF or malformed) - never fetch.
    ask:  fetchable but suspicious - needs a human decision.
    allow: safe to fetch.
    """
    if not isinstance(url, str) or not url.strip():
        return _result("deny", "empty url")
    url = url.strip()
    if len(url) > MAX_URL_LENGTH:
        return _result("deny", "url too long")
    if _CONTROL.search(url):
        return _result("deny", "url contains whitespace, control characters or backslashes")

    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError:
        return _result("deny", "malformed url")

    scheme = (parts.scheme or "").lower()
    if scheme not in ALLOWED_SCHEMES:
        return _result("deny", f"scheme '{scheme or 'none'}' not allowed (http/https only)")
    if parts.username is not None or parts.password is not None or "@" in (parts.netloc or ""):
        return _result("deny", "credentials or userinfo in url are not allowed")

    host = (parts.hostname or "").rstrip(".").lower()
    if not host:
        return _result("deny", "missing host")

    if host in BLOCKED_HOSTS or any(host.endswith(s) for s in BLOCKED_HOST_SUFFIXES):
        return _result("deny", f"internal hostname '{host}'")

    ip = parse_host_ip(host)
    if ip is not None:
        if not _ip_is_public(ip):
            return _result("deny", f"non-public address {ip}")
        return _result("ask", f"url uses a raw IP address ({ip}) instead of a hostname", host=host)

    if "." not in host:
        return _result("deny", f"single-label hostname '{host}' (likely internal)")

    try:
        host.encode("idna")
    except UnicodeError:
        return _result("deny", "host is not valid IDNA")

    if resolve:
        try:
            infos = socket.getaddrinfo(host, port or (443 if scheme == "https" else 80), proto=socket.IPPROTO_TCP)
        except socket.gaierror:
            infos = []
        for info in infos:
            addr = info[4][0]
            try:
                resolved = ipaddress.ip_address(addr.split("%", 1)[0])
            except ValueError:
                continue
            if not _ip_is_public(resolved):
                return _result("deny", f"host '{host}' resolves to non-public address {resolved}")

    reasons: list[str] = []
    if port not in STANDARD_PORTS:
        reasons.append(f"non-standard port {port}")

    query = parts.query or ""
    for key, value in parse_qsl(query, keep_blank_values=True):
        if len(value) >= 80 and _entropy(value) > 4.0:
            reasons.append(f"long high-entropy query value for '{key[:20]}'")
            break
    blob = url
    for pat in SECRET_PATTERNS:
        if pat.search(blob):
            reasons.append("url contains something that looks like a secret or token")
            break
    if len(query) > 600:
        reasons.append("unusually long query string")
    if reasons:
        return _result("ask", "; ".join(reasons), host=host)

    return _result("allow", "ok", host=host)
