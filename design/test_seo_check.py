#!/usr/bin/env python3
"""Regression tests for indexability, sitemap freshness and search icons."""

import struct
import tempfile
import unittest
from pathlib import Path

from seo_check import (
    favicon_crawl_errors,
    favicon_file_errors,
    favicon_link_errors,
    indexability_meta_errors,
    meta_blocks_indexing,
    parse_sitemap_lastmod,
    robots_blocks_indexing,
    robots_explicitly_allows_indexing,
)


class RobotsDirectiveTests(unittest.TestCase):
    def test_explicit_index_is_allowed(self):
        self.assertTrue(robots_explicitly_allows_indexing("index, follow"))
        self.assertTrue(robots_explicitly_allows_indexing("ALL"))
        self.assertFalse(robots_blocks_indexing("index, follow"))

    def test_noindex_is_not_mistaken_for_index(self):
        # Regression: the word "noindex" contains the substring "index".
        self.assertFalse(robots_explicitly_allows_indexing("noindex, follow"))
        self.assertTrue(robots_blocks_indexing("noindex, follow"))

    def test_none_also_blocks_indexing(self):
        self.assertTrue(robots_blocks_indexing("NONE"))
        self.assertFalse(robots_explicitly_allows_indexing("index, none"))

    def test_indexability_meta_requires_general_robots_and_checks_bot_overrides(self):
        allowed = [{"name": "robots", "content": "index, follow"}]
        self.assertEqual(indexability_meta_errors(allowed), [])

        for bot in ("googlebot", "bingbot"):
            with self.subTest(bot=bot):
                override = allowed + [{"name": bot, "content": "noindex"}]
                self.assertTrue(indexability_meta_errors(override))
                self.assertTrue(meta_blocks_indexing(override))

        bot_only = [{"name": "googlebot", "content": "index"}]
        self.assertTrue(indexability_meta_errors(bot_only))

    def test_directive_names_are_case_insensitive_and_tokenized(self):
        self.assertTrue(robots_blocks_indexing("FOLLOW, NoIndex"))
        self.assertFalse(robots_blocks_indexing("max-image-preview:large, index"))


class SitemapLastmodTests(unittest.TestCase):
    def test_iso_date_and_datetime_are_supported(self):
        self.assertEqual(str(parse_sitemap_lastmod("2026-10-28")), "2026-10-28")
        self.assertEqual(
            str(parse_sitemap_lastmod("2026-10-28T12:30:00Z")),
            "2026-10-28",
        )

    def test_invalid_sitemap_date_is_rejected(self):
        self.assertIsNone(parse_sitemap_lastmod("2026-02-30"))
        self.assertIsNone(parse_sitemap_lastmod("not-a-date"))


class FaviconTests(unittest.TestCase):
    def links(self):
        return [
            {"rel": "icon", "type": "image/png", "sizes": "96x96",
             "href": "/favicon-96x96.png"},
            {"rel": "icon", "sizes": "16x16 32x32 48x48", "href": "/favicon.ico"},
            {"rel": "apple-touch-icon", "sizes": "180x180",
             "href": "/assets/just-apps-icon-180.png"},
        ]

    def test_complete_search_icon_declarations_pass(self):
        self.assertEqual(favicon_link_errors(self.links()), [])

    def test_png_and_multisize_ico_are_required(self):
        for index in (0, 1):
            with self.subTest(index=index):
                links = self.links()
                del links[index]
                self.assertTrue(favicon_link_errors(links))

    def test_small_ico_and_non_square_icons_are_rejected(self):
        for href, sizes in [("/favicon.ico", "32x32"),
                            ("/favicon-96x96.png", "96x64")]:
            with self.subTest(href=href):
                links = self.links()
                next(link for link in links if link["href"] == href)["sizes"] = sizes
                self.assertTrue(favicon_link_errors(links))

    def test_unstable_or_wrong_mime_icon_urls_are_rejected(self):
        for change in [{"href": "/favicon-96x96.png?v=2"},
                       {"href": "https://cdn.invalid/favicon-96x96.png"},
                       {"type": "image/svg+xml"}]:
            with self.subTest(change=change):
                links = self.links()
                links[0].update(change)
                self.assertTrue(favicon_link_errors(links))

    def test_actual_png_and_ico_dimensions_are_checked(self):
        with tempfile.TemporaryDirectory() as directory:
            png = Path(directory) / "favicon-96x96.png"
            png.write_bytes(b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR"
                            + struct.pack(">II", 96, 96))
            self.assertEqual(favicon_file_errors(png), [])
            ico = Path(directory) / "favicon.ico"
            directory_entries = b"".join(
                bytes((size, size)) + b"\0" * 14 for size in (16, 32, 48))
            ico.write_bytes(struct.pack("<HHH", 0, 1, 3) + directory_entries)
            self.assertEqual(favicon_file_errors(ico), [])
            png.write_bytes(png.read_bytes()[:16] + struct.pack(">II", 32, 32))
            self.assertTrue(favicon_file_errors(png))
            ico.write_bytes(b"not an icon")
            self.assertTrue(favicon_file_errors(ico))

    def test_both_google_crawlers_must_be_allowed(self):
        urls = ["https://www.justsimpleapps.online/",
                "https://www.justsimpleapps.online/favicon-96x96.png"]
        self.assertEqual(favicon_crawl_errors("User-agent: *\nAllow: /\n", urls), [])
        blocked = "User-agent: Googlebot-Image\nDisallow: /favicon-96x96.png\n"
        errors = favicon_crawl_errors(blocked, urls)
        self.assertTrue(any("Googlebot-Image" in error for error in errors))
        self.assertFalse(any(error.startswith("Googlebot:") for error in errors))


if __name__ == "__main__":
    unittest.main()
