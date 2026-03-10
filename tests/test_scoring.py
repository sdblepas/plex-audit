"""
Tests for scoring logic and release date filter extracted from scanner.py
These functions are tested in isolation — no Plex/TMDB calls needed.
"""
import pytest
from datetime import date, timedelta


# ─────────────────────────────────────────────
# Scoring formulas (mirrored from scanner.py)
# Keeping them here so tests don't import the
# full scanner (which has side effects at module level)
# ─────────────────────────────────────────────

def franchise_score(have: int, total: int) -> float:
    return (have / total * 100) if total else 0


def classics_score(missing: int, max_results: int) -> float:
    return max(0.0, 100.0 - (missing / max(1, max_results) * 100))


def directors_score(missing_total: int, directors_count: int) -> float:
    return max(0.0, 100.0 - (missing_total / max(1, directors_count) * 5))


def global_score(fs: float, ds: float, cs: float) -> float:
    return round((fs * 0.5) + (ds * 0.25) + (cs * 0.25), 1)


def is_released(release_date: str) -> bool:
    """Mirror of the filter logic added in scanner.py."""
    release = (release_date or "")[:10]
    if not release:
        return False
    return release <= date.today().isoformat()


# ─────────────────────────────────────────────
# Franchise score
# ─────────────────────────────────────────────

class TestFranchiseScore:

    def test_perfect_collection(self):
        assert franchise_score(10, 10) == 100.0

    def test_half_complete(self):
        assert franchise_score(5, 10) == 50.0

    def test_empty_collection(self):
        assert franchise_score(0, 0) == 0.0

    def test_nothing_owned(self):
        assert franchise_score(0, 10) == 0.0


# ─────────────────────────────────────────────
# Classics score
# ─────────────────────────────────────────────

class TestClassicsScore:

    def test_no_classics_missing(self):
        assert classics_score(0, 120) == 100.0

    def test_all_classics_missing(self):
        assert classics_score(120, 120) == 0.0

    def test_half_missing(self):
        assert classics_score(60, 120) == 50.0

    def test_never_goes_negative(self):
        assert classics_score(9999, 120) == 0.0

    def test_zero_max_results_safe(self):
        # max(1, 0) prevents division by zero
        assert classics_score(0, 0) == 100.0


# ─────────────────────────────────────────────
# Directors score
# ─────────────────────────────────────────────

class TestDirectorsScore:

    def test_no_missing_films(self):
        assert directors_score(0, 10) == 100.0

    def test_many_missing_clamps_to_zero(self):
        assert directors_score(9999, 10) == 0.0

    def test_never_goes_negative(self):
        assert directors_score(500, 1) == 0.0

    def test_moderate_missing(self):
        # 10 missing / 10 directors * 5 = 5 → 100 - 5 = 95
        assert directors_score(10, 10) == 95.0


# ─────────────────────────────────────────────
# Global score
# ─────────────────────────────────────────────

class TestGlobalScore:

    def test_perfect_score(self):
        assert global_score(100.0, 100.0, 100.0) == 100.0

    def test_zero_score(self):
        assert global_score(0.0, 0.0, 0.0) == 0.0

    def test_weighted_correctly(self):
        # franchise=100, directors=0, classics=0
        # 100*0.5 + 0*0.25 + 0*0.25 = 50
        assert global_score(100.0, 0.0, 0.0) == 50.0

    def test_rounded_to_one_decimal(self):
        result = global_score(33.3, 33.3, 33.3)
        assert result == round((33.3 * 0.5) + (33.3 * 0.25) + (33.3 * 0.25), 1)


# ─────────────────────────────────────────────
# Release date filter
# ─────────────────────────────────────────────

class TestIsReleased:

    def test_past_date_is_released(self):
        past = (date.today() - timedelta(days=30)).isoformat()
        assert is_released(past) is True

    def test_today_is_released(self):
        assert is_released(date.today().isoformat()) is True

    def test_future_date_not_released(self):
        future = (date.today() + timedelta(days=30)).isoformat()
        assert is_released(future) is False

    def test_empty_string_not_released(self):
        assert is_released("") is False

    def test_none_not_released(self):
        assert is_released(None) is False

    def test_partial_date_string(self):
        # TMDB sometimes returns "2024-00-00" style — still parseable as string compare
        past = "2020-01-01"
        assert is_released(past) is True

    def test_future_year_not_released(self):
        assert is_released("2099-01-01") is False