from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
STATIC_URL_SUFFIXES = (
    "/",
    "/compare.html",
    "/underwrite.html",
    "/account.html",
    "/privacy.html",
    "/terms.html",
)


def validate_sitemap(
    sitemap_path: Path,
    robots_path: Path,
    agents: list[dict[str, Any]],
    public_base: str,
) -> None:
    """Fail closed when generated SEO files omit or mis-scope published URLs."""
    base = public_base.rstrip("/")
    parsed_base = urlsplit(base)
    if parsed_base.scheme != "https" or not parsed_base.netloc:
        raise ValueError("public base must be an absolute HTTPS URL")

    expected_urls = {f"{base}{suffix}" for suffix in STATIC_URL_SUFFIXES}
    for agent in agents:
        metadata = agent.get("metadata")
        slug = metadata.get("slug") if isinstance(metadata, dict) else None
        if not isinstance(slug, str) or not slug:
            raise ValueError("generated agent is missing its profile slug")
        expected_urls.add(f"{base}/agents/{slug}/")

    try:
        root = ET.parse(sitemap_path).getroot()
    except (OSError, ET.ParseError) as exc:
        raise ValueError(f"sitemap is not well-formed XML: {exc}") from exc

    expected_root = f"{{{SITEMAP_NAMESPACE}}}urlset"
    if root.tag != expected_root:
        raise ValueError("sitemap root or namespace is invalid")

    url_tag = f"{{{SITEMAP_NAMESPACE}}}url"
    loc_tag = f"{{{SITEMAP_NAMESPACE}}}loc"
    urls: list[str] = []
    for entry in root.findall(url_tag):
        location = entry.find(loc_tag)
        value = (location.text or "").strip() if location is not None else ""
        if not value:
            raise ValueError("sitemap contains a URL without a loc value")
        parsed_url = urlsplit(value)
        if parsed_url.scheme != "https" or parsed_url.netloc != parsed_base.netloc:
            raise ValueError("sitemap contains a URL outside the public site")
        urls.append(value)

    if not urls:
        raise ValueError("sitemap contains no URLs")
    if len(urls) != len(set(urls)):
        raise ValueError("sitemap contains duplicate URLs")

    actual_urls = set(urls)
    missing = sorted(expected_urls - actual_urls)
    unexpected = sorted(actual_urls - expected_urls)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing={missing[:5]}")
        if unexpected:
            details.append(f"unexpected={unexpected[:5]}")
        raise ValueError("sitemap URL set does not match generated profiles: " + "; ".join(details))

    expected_sitemap_url = f"{base}/sitemap.xml"
    try:
        robot_lines = robots_path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ValueError(f"robots.txt could not be read: {exc}") from exc
    sitemap_directives = [
        line.split(":", 1)[1].strip()
        for line in robot_lines
        if line.strip().lower().startswith("sitemap:")
    ]
    if expected_sitemap_url not in sitemap_directives:
        raise ValueError("robots.txt does not declare the generated sitemap URL")
