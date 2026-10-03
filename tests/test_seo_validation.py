import tempfile
import unittest
from pathlib import Path

from aun.seo_validation import SITEMAP_NAMESPACE, validate_sitemap


PUBLIC_BASE = "https://example.github.io/agent-underwriting-network"
AGENTS = [{"metadata": {"slug": "sample-agent"}}]


def _xml(urls: list[str], namespace: str = SITEMAP_NAMESPACE) -> str:
    entries = "".join(f"<url><loc>{url}</loc></url>" for url in urls)
    return f'<urlset xmlns="{namespace}">{entries}</urlset>'


def _expected_urls() -> list[str]:
    return [
        f"{PUBLIC_BASE}/",
        f"{PUBLIC_BASE}/compare.html",
        f"{PUBLIC_BASE}/underwrite.html",
        f"{PUBLIC_BASE}/account.html",
        f"{PUBLIC_BASE}/privacy.html",
        f"{PUBLIC_BASE}/terms.html",
        f"{PUBLIC_BASE}/agents/sample-agent/",
    ]


class SitemapValidationTests(unittest.TestCase):
    def _run(self, xml: str, robots: str) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            sitemap = root / "sitemap.xml"
            robots_path = root / "robots.txt"
            sitemap.write_text(xml, encoding="utf-8")
            robots_path.write_text(robots, encoding="utf-8")
            validate_sitemap(sitemap, robots_path, AGENTS, PUBLIC_BASE)

    def test_accepts_complete_namespaced_sitemap_and_robots_declaration(self):
        robots = f"User-agent: *\nAllow: /\nSitemap: {PUBLIC_BASE}/sitemap.xml\n"
        self._run(_xml(_expected_urls()), robots)

    def test_rejects_wrong_namespace(self):
        robots = f"Sitemap: {PUBLIC_BASE}/sitemap.xml\n"
        with self.assertRaisesRegex(ValueError, "root or namespace"):
            self._run(_xml(_expected_urls(), namespace="https://wrong.example/ns"), robots)

    def test_rejects_duplicate_urls(self):
        urls = _expected_urls()
        urls.append(urls[0])
        robots = f"Sitemap: {PUBLIC_BASE}/sitemap.xml\n"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            self._run(_xml(urls), robots)

    def test_rejects_missing_profile_and_missing_robots_directive(self):
        urls = _expected_urls()[:-1]
        with self.assertRaisesRegex(ValueError, "missing="):
            self._run(_xml(urls), "User-agent: *\nAllow: /\n")


if __name__ == "__main__":
    unittest.main()
