"""Safe source intake: URLs, local files and transcripts become clean text.

Why this exists in code and not in prose: fetching a web page and handing it to
a model is the riskiest thing a content skill does. Doing it here gives
guarantees a prompt cannot:

- SSRF-safe. Every hop (including redirects) passes `urlguard`, and the socket
  is connected to the exact IP that was validated, so DNS rebinding between
  "check" and "fetch" cannot swap in an internal address.
- Bounded. Size cap, time cap, redirect cap, no cookies, no credentials, only
  text-like content types.
- Hidden-text-aware. Text hidden from human readers (display:none, aria-hidden,
  zero font size, HTML comments, off-screen positioning) is dropped, because it
  is where page-level prompt injection lives.
- Scanned and sanitised. The result is run through the injection scanner, has
  invisible Unicode removed, and has fake structural delimiters neutralised.
- Written to a file. The agent reads the file, and the same file anchors the
  claims check later, so quotes and numbers can be traced to exactly what was
  ingested.
"""

from __future__ import annotations

import http.client
import ipaddress
import re
import socket
import ssl
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlsplit

from . import urlguard
from .jsonio import write_text_atomic
from .scan import invisible_report, sanitise_source, scan_text

MAX_BYTES = 3_000_000
MAX_TEXT_CHARS = 600_000
MAX_REDIRECTS = 4
TIMEOUT = 12.0
USER_AGENT = "Mozilla/5.0 (compatible; content-wand/2.0; +source-intake)"
TEXT_TYPES = {"text/html", "application/xhtml+xml", "text/plain", "text/markdown", "text/x-markdown", "text/vtt", "application/x-subrip"}
LOCAL_SUFFIXES = {".txt", ".md", ".markdown", ".html", ".htm", ".srt", ".vtt", ".rtf", ".text", ""}

SKIP_TAGS = {"script", "style", "noscript", "template", "svg", "canvas", "iframe", "object", "embed", "nav", "footer", "aside", "form", "button", "select", "dialog", "head"}
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}
BLOCK = {"p", "div", "section", "article", "li", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "blockquote", "pre", "ul", "ol", "table", "figure", "figcaption", "header", "main", "dd", "dt"}
HIDDEN_STYLE = re.compile(r"(display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(?![.\d])|opacity\s*:\s*0(?![.\d])|(?:left|top|text-indent)\s*:\s*-\d{3,}|clip\s*:\s*rect\(0|height\s*:\s*0(?:px)?\s*;?[^\"']*overflow\s*:\s*hidden)", re.IGNORECASE)


class IngestError(Exception):
    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


class _Extractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool]] = []
        self.chunks: list[str] = []
        self.article_chunks: list[str] = []
        self.article_depth = 0
        self.title = ""
        self.og_title = ""
        self.in_title = False
        self.hidden_chars = 0
        self.comments: list[str] = []

    def _skipped(self) -> bool:
        return bool(self.stack) and self.stack[-1][1]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "meta" and a.get("property", "").lower() == "og:title":
            self.og_title = a.get("content", "")
        if tag == "title":
            self.in_title = True
        if tag in VOID:
            if tag == "br" and not self._skipped():
                self._emit("\n")
            return
        hidden = "hidden" in a or a.get("aria-hidden", "").lower() == "true" or bool(HIDDEN_STYLE.search(a.get("style", "")))
        skip = self._skipped() or tag in SKIP_TAGS or hidden
        self.stack.append((tag, skip))
        if tag in ("article", "main") and not skip:
            self.article_depth += 1
        if tag in BLOCK and not skip:
            self._emit("\n\n" if tag.startswith("h") or tag in ("p", "blockquote") else "\n")
            if tag.startswith("h") and len(tag) == 2:
                self._emit("## ")

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        for i in range(len(self.stack) - 1, -1, -1):
            if self.stack[i][0] == tag:
                for name, skip in self.stack[i:]:
                    if name in ("article", "main") and not skip:
                        self.article_depth = max(0, self.article_depth - 1)
                del self.stack[i:]
                break
        if tag in BLOCK and not self._skipped():
            self._emit("\n")

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data
            return
        if self._skipped():
            tag_names = {t for t, s in self.stack if s}
            if not (tag_names & SKIP_TAGS):
                self.hidden_chars += len(data.strip())
            return
        self._emit(data)

    def handle_comment(self, data: str) -> None:
        if data.strip():
            self.comments.append(data)

    def _emit(self, text: str) -> None:
        self.chunks.append(text)
        if self.article_depth:
            self.article_chunks.append(text)


def _tidy(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def html_to_text(html: str) -> dict[str, Any]:
    parser = _Extractor()
    parser.feed(html)
    parser.close()
    full = _tidy("".join(parser.chunks))
    article = _tidy("".join(parser.article_chunks))
    body = article if len(article.split()) >= 0.4 * max(1, len(full.split())) and len(article.split()) >= 80 else full
    flagged = [c for c in parser.comments if scan_text(c)["severity"] != "none"]
    return {
        "title": _tidy(parser.og_title or parser.title)[:200],
        "text": body,
        "hidden_text_dropped_chars": parser.hidden_chars,
        "html_comments": len(parser.comments),
        "html_comments_flagged": len(flagged),
    }


_TS = re.compile(r"(?:(\d{1,2}):)?(\d{2}):(\d{2})[.,](\d{3})\s*-->\s*")


def timed_text_to_transcript(raw: str, bucket_seconds: int = 20) -> str:
    """Turn SRT/VTT into '[hh:mm:ss] text' paragraphs, copying timestamps verbatim."""
    out: list[str] = []
    cur_ts = ""
    cur: list[str] = []
    last_start = -999.0
    for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        lines = [ln for ln in block.split("\n") if ln.strip()]
        for i, ln in enumerate(lines):
            m = _TS.match(ln.strip())
            if not m:
                continue
            h, mi, s = int(m.group(1) or 0), int(m.group(2)), int(m.group(3))
            start = h * 3600 + mi * 60 + s
            text = " ".join(re.sub(r"<[^>]+>", "", t).strip() for t in lines[i + 1 :]).strip()
            if not text:
                break
            if start - last_start >= bucket_seconds or not cur:
                if cur:
                    out.append(f"[{cur_ts}] {' '.join(cur)}")
                cur_ts = f"{h:02d}:{mi:02d}:{s:02d}"
                cur = []
                last_start = start
            cur.append(text)
            break
    if cur:
        out.append(f"[{cur_ts}] {' '.join(cur)}")
    return "\n".join(out)


class _PinnedHTTP(http.client.HTTPConnection):
    def __init__(self, host: str, port: int, ip: str, timeout: float):
        super().__init__(host, port, timeout=timeout)
        self._ip = ip

    def connect(self) -> None:
        self.sock = socket.create_connection((self._ip, self.port), self.timeout)


class _PinnedHTTPS(http.client.HTTPSConnection):
    def __init__(self, host: str, port: int, ip: str, timeout: float):
        super().__init__(host, port, timeout=timeout, context=ssl.create_default_context())
        self._ip = ip

    def connect(self) -> None:
        raw = socket.create_connection((self._ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw, server_hostname=self.host)


def _resolve_public(host: str, port: int, allow_loopback: bool) -> str:
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise IngestError("dns-error", f"could not resolve {host}") from exc
    chosen: str | None = None
    for info in infos:
        addr = info[4][0].split("%", 1)[0]
        ip = ipaddress.ip_address(addr)
        if not (allow_loopback and ip.is_loopback) and not urlguard._ip_is_public(ip):
            raise IngestError("rejected-unsafe-url", f"host resolves to a non-public address ({ip})")
        chosen = chosen or addr
    if chosen is None:
        raise IngestError("dns-error", f"no address for {host}")
    return chosen


def fetch_url(url: str, confirmed: bool = False, _allow_loopback: bool = False, max_bytes: int = MAX_BYTES) -> dict[str, Any]:
    current = url.strip()
    for _ in range(MAX_REDIRECTS + 1):
        verdict = urlguard.check_url(current, resolve=False) if not _allow_loopback else {"decision": "allow", "reason": "test"}
        if verdict["decision"] == "deny":
            raise IngestError("rejected-unsafe-url", verdict["reason"])
        if verdict["decision"] == "ask" and not confirmed:
            raise IngestError("needs-confirmation", verdict["reason"])
        parts = urlsplit(current)
        port = parts.port or (443 if parts.scheme == "https" else 80)
        host = parts.hostname or ""
        ip = _resolve_public(host, port, _allow_loopback)
        conn_cls = _PinnedHTTPS if parts.scheme == "https" else _PinnedHTTP
        conn = conn_cls(host, port, ip, TIMEOUT)
        path = (parts.path or "/") + (f"?{parts.query}" if parts.query else "")
        try:
            conn.request("GET", path, headers={"User-Agent": USER_AGENT, "Accept": "text/html,text/plain,text/markdown;q=0.9,*/*;q=0.1", "Accept-Encoding": "identity", "Connection": "close"})
            resp = conn.getresponse()
            status = resp.status
            if status in (301, 302, 303, 307, 308):
                loc = resp.getheader("Location")
                if not loc:
                    raise IngestError("fetch-failed", "redirect without a Location header")
                current = urljoin(current, loc)
                continue
            if status in (401, 403):
                raise IngestError("login-required" if status == 401 else "forbidden", f"HTTP {status}: the page is not publicly readable. Ask the user to paste the text.")
            if status == 404 or status == 410:
                raise IngestError("not-found", f"HTTP {status}")
            if status == 429:
                raise IngestError("rate-limited", "HTTP 429: the site is rate limiting requests. Ask the user to paste the text.")
            if status >= 500:
                raise IngestError("server-error", f"HTTP {status}")
            if status >= 400:
                raise IngestError("fetch-failed", f"HTTP {status}")
            ctype = (resp.getheader("Content-Type") or "").split(";")[0].strip().lower()
            if ctype and ctype not in TEXT_TYPES:
                raise IngestError("unsupported-content-type", f"content type '{ctype}' is not text. Ask the user to paste the text or provide a transcript.")
            body = resp.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise IngestError("too-large", f"page exceeds {max_bytes // 1_000_000} MB")
            charset = "utf-8"
            m = re.search(r"charset=([\w-]+)", resp.getheader("Content-Type") or "", re.IGNORECASE)
            if m:
                charset = m.group(1)
            try:
                decoded = body.decode(charset, errors="replace")
            except LookupError:
                decoded = body.decode("utf-8", errors="replace")
            return {"final_url": current, "content_type": ctype or "text/html", "body": decoded}
        except (socket.timeout, TimeoutError) as exc:
            raise IngestError("timeout", "the request timed out. Ask the user to paste the text.") from exc
        except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
            raise IngestError("fetch-failed", f"{type(exc).__name__}: could not fetch the page") from exc
        finally:
            conn.close()
    raise IngestError("too-many-redirects", f"more than {MAX_REDIRECTS} redirects")


def _finish(raw_text: str, meta: dict[str, Any], out: Path | None) -> dict[str, Any]:
    text = raw_text[:MAX_TEXT_CHARS]
    scan = scan_text(text)
    cleaned, san = sanitise_source(text)
    words = len(re.findall(r"\S+", cleaned))
    warnings: list[str] = []
    if words < 50:
        warnings.append("short-input")
    if words > 8000:
        warnings.append("very-long-input")
    if san["fences_escaped"]:
        warnings.append("delimiter-in-source")
    if scan["severity"] != "none":
        warnings.append(f"injection-{scan['severity']}")
    if meta.get("hidden_text_dropped_chars"):
        warnings.append("hidden-text-dropped")
    result: dict[str, Any] = {
        "ok": True,
        **meta,
        "word_count": words,
        "warnings": warnings,
        "injection": {
            "severity": scan["severity"],
            "findings": [{"id": f["id"], "severity": f["severity"], "snippet": f["snippet"][:100]} for f in scan["findings"][:6]],
        },
        "invisible_removed": san["invisible_removed"],
        "preview": cleaned[:400],
    }
    if out is not None:
        write_text_atomic(out, cleaned.rstrip("\n") + "\n")
        result["source_file"] = str(out)
    else:
        result["text"] = cleaned
    return result


def ingest_url(url: str, out: Path | None, confirmed: bool = False, _allow_loopback: bool = False) -> dict[str, Any]:
    try:
        page = fetch_url(url, confirmed=confirmed, _allow_loopback=_allow_loopback)
    except IngestError as err:
        return {"ok": False, "fetch_status": err.status, "error": err.message}
    body = page["body"]
    meta: dict[str, Any] = {"source_type": "url", "fetch_status": "ok", "final_url": page["final_url"]}
    if page["content_type"] in ("text/html", "application/xhtml+xml"):
        extracted = html_to_text(body)
        text = extracted.pop("text")
        meta.update(extracted)
    elif page["content_type"] in ("text/vtt", "application/x-subrip"):
        text = timed_text_to_transcript(body)
        meta["source_type"] = "transcript"
    else:
        text = body
        meta["title"] = ""
    if not text.strip():
        return {"ok": False, "fetch_status": "empty", "error": "no readable text was found on the page (it may be rendered by JavaScript). Ask the user to paste the text."}
    return _finish(text, meta, out)


def ingest_file(path: Path, out: Path | None) -> dict[str, Any]:
    from .hooks import SENSITIVE_RE

    p = Path(path).expanduser()
    norm = str(p.resolve()).replace("\\", "/")
    if any(rx.search(norm) for rx in SENSITIVE_RE):
        return {"ok": False, "error": "that path looks like a credential, key or configuration file; it will not be read"}
    if not p.is_file():
        return {"ok": False, "error": "file not found"}
    if p.suffix.lower() not in LOCAL_SUFFIXES:
        return {"ok": False, "error": f"unsupported file type '{p.suffix}'. Supported: text, markdown, HTML, SRT and VTT. Paste the text for other formats."}
    if p.stat().st_size > MAX_BYTES:
        return {"ok": False, "error": "file is larger than 3 MB"}
    raw = p.read_bytes()
    if b"\x00" in raw[:4096]:
        return {"ok": False, "error": "file looks binary, not text"}
    text = raw.decode("utf-8", errors="replace")
    meta: dict[str, Any] = {"source_type": "file", "file_name": p.name}
    suffix = p.suffix.lower()
    if suffix in (".srt", ".vtt"):
        text = timed_text_to_transcript(text)
        meta["source_type"] = "transcript"
    elif suffix in (".html", ".htm"):
        extracted = html_to_text(text)
        text = extracted.pop("text")
        meta.update(extracted)
    elif re.search(r"(?m)^\s*(\[?\d{1,2}:\d{2}(:\d{2})?\]?)\s+\S", text) or re.search(r"(?m)^[A-Z][\w .'-]{1,30}:\s", text[:3000]):
        meta["transcript_like"] = True
    if not text.strip():
        return {"ok": False, "error": "the file contains no readable text"}
    return _finish(text, meta, out)


def ingest_text(text: str, out: Path | None) -> dict[str, Any]:
    if not text.strip():
        return {"ok": False, "error": "no text provided"}
    return _finish(text, {"source_type": "paste"}, out)


__all__ = ["ingest_url", "ingest_file", "ingest_text", "html_to_text", "timed_text_to_transcript", "fetch_url", "IngestError", "invisible_report"]
