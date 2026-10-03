from __future__ import annotations

import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

BASE = "https://2nedimucrs-by.github.io/agent-underwriting-network"
SITEMAP_URL = f"{BASE}/sitemap.xml"
ROBOTS_URL = f"{BASE}/robots.txt"
SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
MAX_BODY_BYTES = 2_000_000


def fetch(url: str) -> tuple[int, str, str, bytes]:
    last_error: Exception | None = None
    for attempt in range(3):
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "AUN-public-seo-probe/1.0"},
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                body = response.read(MAX_BODY_BYTES + 1)
                final_url = response.geturl()
                content_type = response.headers.get("Content-Type", "")
                status = response.status
            if len(body) > MAX_BODY_BYTES:
                raise ValueError(f"response exceeds {MAX_BODY_BYTES} bytes")
            print(f"URL={url}")
            print(f"STATUS={status}")
            print(f"FINAL_URL={final_url}")
            print(f"CONTENT_TYPE={content_type or '(missing)'}")
            print(f"BODY_BYTES={len(body)}")
            if status != 200:
                raise ValueError(f"unexpected HTTP status {status} for {url}")
            if final_url != url:
                raise ValueError(f"unexpected final URL {final_url} for {url}")
            return status, final_url, content_type, body
        except urllib.error.HTTPError as exc:
            last_error = exc
            body = exc.read(512)
            print(f"URL={url}")
            print(f"STATUS={exc.code}")
            print(f"CONTENT_TYPE={exc.headers.get('Content-Type', '')}")
            print(f"ERROR_BODY_PREFIX={body[:160]!r}")
        except (urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            print(f"URL={url}")
            print(f"ATTEMPT={attempt + 1}")
            print(f"ERROR={type(exc).__name__}: {exc}")
        if attempt < 2:
            time.sleep(attempt + 1)
    assert last_error is not None
    raise SystemExit(f"live SEO endpoint unavailable: {last_error}")


_, _, _, sitemap_body = fetch(SITEMAP_URL)
try:
    root = ET.fromstring(sitemap_body)
except ET.ParseError as exc:
    raise SystemExit(f"SITEMAP_XML_PARSE=FAIL: {exc}") from exc

expected_root = f"{{{SITEMAP_NS}}}urlset"
if root.tag != expected_root:
    raise SystemExit(f"SITEMAP_XML_ROOT=FAIL: {root.tag!r}")
loc_tag = f"{{{SITEMAP_NS}}}loc"
urls = []
for entry in root.findall(f"{{{SITEMAP_NS}}}url"):
    location = entry.find(loc_tag)
    value = (location.text or "").strip() if location is not None else ""
    if not value:
        raise SystemExit("SITEMAP_XML_PARSE=FAIL: URL entry has no loc")
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.netloc != urlsplit(BASE).netloc:
        raise SystemExit(f"SITEMAP_URL_SCOPE=FAIL: {value}")
    urls.append(value)

if not urls:
    raise SystemExit("SITEMAP_URL_COUNT=0")
if len(urls) != len(set(urls)):
    raise SystemExit("SITEMAP_DUPLICATES=FAIL")
print("SITEMAP_XML_PARSE=PASS")
print(f"SITEMAP_URL_COUNT={len(urls)}")

_, _, _, robots_body = fetch(ROBOTS_URL)
try:
    robots = robots_body.decode("utf-8")
except UnicodeDecodeError as exc:
    raise SystemExit(f"ROBOTS_UTF8=FAIL: {exc}") from exc
directives = [
    line.split(":", 1)[1].strip()
    for line in robots.splitlines()
    if line.strip().lower().startswith("sitemap:")
]
if SITEMAP_URL not in directives:
    raise SystemExit("ROBOTS_SITEMAP_DIRECTIVE=FAIL")
print("ROBOTS_SITEMAP_DIRECTIVE=PASS")
