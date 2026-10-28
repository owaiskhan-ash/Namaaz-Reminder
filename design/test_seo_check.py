#!/usr/bin/env python3
"""Regression tests for indexability directives and sitemap freshness."""

import unittest

from seo_check import (
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


if __name__ == "__main__":
    unittest.main()
