"""
Tests for app/config.py
Covers: _deep_merge, is_configured
"""
import copy
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.config import _deep_merge, is_configured, DEFAULT_CONFIG


# ─────────────────────────────────────────────
# _deep_merge
# ─────────────────────────────────────────────

class TestDeepMerge:

    def test_override_leaf_value(self):
        base     = {"A": {"x": 1, "y": 2}}
        override = {"A": {"x": 99}}
        result   = _deep_merge(base, override)
        assert result["A"]["x"] == 99
        assert result["A"]["y"] == 2          # untouched

    def test_adds_missing_key(self):
        base     = {"A": {"x": 1}}
        override = {"A": {"z": 3}}
        result   = _deep_merge(base, override)
        assert result["A"]["z"] == 3
        assert result["A"]["x"] == 1

    def test_does_not_mutate_base(self):
        base     = {"A": {"x": 1}}
        original = copy.deepcopy(base)
        _deep_merge(base, {"A": {"x": 99}})
        assert base == original

    def test_none_override_returns_base(self):
        base   = {"A": 1}
        result = _deep_merge(base, None)
        assert result == base

    def test_nested_three_levels(self):
        base     = {"A": {"B": {"C": 1}}}
        override = {"A": {"B": {"C": 42}}}
        result   = _deep_merge(base, override)
        assert result["A"]["B"]["C"] == 42

    def test_scalar_override_replaces_dict(self):
        """If override provides a scalar where base had a dict, scalar wins."""
        base     = {"A": {"x": 1}}
        override = {"A": "flat"}
        result   = _deep_merge(base, override)
        assert result["A"] == "flat"

    def test_default_config_not_mutated_by_partial_override(self):
        partial = {"PLEX": {"PLEX_URL": "http://plex:32400"}}
        result  = _deep_merge(DEFAULT_CONFIG, partial)
        assert result["PLEX"]["PLEX_URL"] == "http://plex:32400"
        assert DEFAULT_CONFIG["PLEX"]["PLEX_URL"] == ""   # original untouched


# ─────────────────────────────────────────────
# is_configured
# ─────────────────────────────────────────────

class TestIsConfigured:

    def _cfg(self, url="", token="", library="", api_key=""):
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg["PLEX"]["PLEX_URL"]      = url
        cfg["PLEX"]["PLEX_TOKEN"]    = token
        cfg["PLEX"]["LIBRARY_NAME"]  = library
        cfg["TMDB"]["TMDB_API_KEY"]  = api_key
        return cfg

    def test_all_fields_set_returns_true(self):
        cfg = self._cfg("http://plex", "token123", "Movies", "tmdb_key")
        assert is_configured(cfg) is True

    def test_missing_plex_url_returns_false(self):
        cfg = self._cfg("", "token123", "Movies", "tmdb_key")
        assert is_configured(cfg) is False

    def test_missing_token_returns_false(self):
        cfg = self._cfg("http://plex", "", "Movies", "tmdb_key")
        assert is_configured(cfg) is False

    def test_missing_library_returns_false(self):
        cfg = self._cfg("http://plex", "token123", "", "tmdb_key")
        assert is_configured(cfg) is False

    def test_missing_tmdb_key_returns_false(self):
        cfg = self._cfg("http://plex", "token123", "Movies", "")
        assert is_configured(cfg) is False

    def test_whitespace_only_value_returns_false(self):
        cfg = self._cfg("   ", "token123", "Movies", "tmdb_key")
        assert is_configured(cfg) is False

    def test_default_config_not_configured(self):
        assert is_configured(copy.deepcopy(DEFAULT_CONFIG)) is False