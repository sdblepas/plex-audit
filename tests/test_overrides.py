"""
Tests for app/overrides.py
Covers: add_unique, remove_value, load_json (default fallback)
"""
import json
import os
import sys
import tempfile
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.overrides import add_unique, remove_value, load_json, save_json, DEFAULT


# ─────────────────────────────────────────────
# add_unique
# ─────────────────────────────────────────────

class TestAddUnique:

    def test_adds_new_value(self):
        lst = [1, 2]
        add_unique(lst, 3)
        assert lst == [1, 2, 3]

    def test_does_not_add_duplicate(self):
        lst = [1, 2, 3]
        add_unique(lst, 2)
        assert lst == [1, 2, 3]

    def test_adds_to_empty_list(self):
        lst = []
        add_unique(lst, 42)
        assert lst == [42]

    def test_string_dedup(self):
        lst = ["Nolan", "Kubrick"]
        add_unique(lst, "Nolan")
        assert lst.count("Nolan") == 1


# ─────────────────────────────────────────────
# remove_value
# ─────────────────────────────────────────────

class TestRemoveValue:

    def test_removes_existing_value(self):
        lst = [1, 2, 3]
        remove_value(lst, 2)
        assert lst == [1, 3]

    def test_no_error_on_missing_value(self):
        lst = [1, 2, 3]
        remove_value(lst, 99)   # should not raise
        assert lst == [1, 2, 3]

    def test_removes_string(self):
        lst = ["Nolan", "Kubrick"]
        remove_value(lst, "Nolan")
        assert lst == ["Kubrick"]

    def test_removes_only_first_occurrence(self):
        lst = [1, 2, 2, 3]
        remove_value(lst, 2)
        assert lst == [1, 2, 3]


# ─────────────────────────────────────────────
# load_json
# ─────────────────────────────────────────────

class TestLoadJson:

    def test_returns_default_when_file_missing(self):
        result = load_json("/nonexistent/path/overrides.json")
        assert result == DEFAULT

    def test_loads_valid_file(self):
        data = {"ignore_movies": [1, 2], "wishlist_movies": [99]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = load_json(path)
            assert result["ignore_movies"] == [1, 2]
            assert result["wishlist_movies"] == [99]
        finally:
            os.unlink(path)

    def test_fills_missing_keys_with_defaults(self):
        data = {"ignore_movies": [1]}   # missing other keys
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(data, f)
            path = f.name
        try:
            result = load_json(path)
            assert "wishlist_movies" in result
            assert result["wishlist_movies"] == []
        finally:
            os.unlink(path)

    def test_returns_default_on_corrupt_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{ this is not json }")
            path = f.name
        try:
            result = load_json(path)
            assert result == DEFAULT
        finally:
            os.unlink(path)