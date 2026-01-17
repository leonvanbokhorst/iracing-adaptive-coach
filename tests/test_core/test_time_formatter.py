"""
Unit tests for time_formatter.py

Tests the pure utility functions for lap time formatting.
"""

import pytest
from tools.core.time_formatter import (
    format_laptime,
    format_laptime_short,
    format_delta,
    format_delta_short,
    parse_laptime,
)


class TestFormatLaptime:
    """Test format_laptime function."""

    def test_basic_minute_plus(self):
        """Test lap time over 1 minute."""
        assert format_laptime(80.356) == "1:20.356"

    def test_ninety_seconds(self):
        """Test 90 second lap."""
        assert format_laptime(90.290) == "1:30.290"

    def test_two_minutes_plus(self):
        """Test lap time over 2 minutes."""
        assert format_laptime(125.450) == "2:05.450"

    def test_under_one_minute(self):
        """Test lap time under 1 minute (no minute prefix)."""
        assert format_laptime(45.123) == "45.123"

    def test_exactly_one_minute(self):
        """Test exactly 60 seconds."""
        assert format_laptime(60.0) == "1:00.000"

    def test_negative_returns_invalid(self):
        """Test negative time returns Invalid."""
        assert format_laptime(-5.0) == "Invalid"

    def test_zero(self):
        """Test zero seconds."""
        assert format_laptime(0.0) == "0.000"

    def test_precision(self):
        """Test millisecond precision is preserved."""
        assert format_laptime(90.001) == "1:30.001"
        assert format_laptime(90.999) == "1:30.999"


class TestFormatLaptimeShort:
    """Test format_laptime_short function (2 decimal places)."""

    def test_basic(self):
        """Test basic lap time formatting with 2 decimals."""
        assert format_laptime_short(80.356) == "1:20.36"

    def test_ninety_seconds(self):
        """Test 90 second lap."""
        assert format_laptime_short(90.290) == "1:30.29"

    def test_under_one_minute(self):
        """Test lap time under 1 minute."""
        assert format_laptime_short(45.123) == "45.12"

    def test_negative_returns_invalid(self):
        """Test negative time returns Invalid."""
        assert format_laptime_short(-1.0) == "Invalid"


class TestFormatDelta:
    """Test format_delta function."""

    def test_positive_delta(self):
        """Test positive delta with + sign."""
        assert format_delta(0.356) == "+0.356"
        assert format_delta(1.234) == "+1.234"

    def test_negative_delta(self):
        """Test negative delta with - sign."""
        assert format_delta(-0.125) == "-0.125"
        assert format_delta(-1.500) == "-1.500"

    def test_zero_delta(self):
        """Test zero delta gets + sign."""
        assert format_delta(0.0) == "+0.000"


class TestFormatDeltaShort:
    """Test format_delta_short function (2 decimal places)."""

    def test_positive_delta(self):
        """Test positive delta with + sign and 2 decimals."""
        assert format_delta_short(0.356) == "+0.36"

    def test_negative_delta(self):
        """Test negative delta with - sign and 2 decimals."""
        # Python uses banker's rounding, so -0.125 -> -0.12
        assert format_delta_short(-0.126) == "-0.13"

    def test_zero_delta(self):
        """Test zero delta."""
        assert format_delta_short(0.0) == "+0.00"


class TestParseLaptime:
    """Test parse_laptime function (reverse of format_laptime)."""

    def test_parse_with_minutes(self):
        """Test parsing time with minutes."""
        assert parse_laptime("1:20.356") == pytest.approx(80.356)

    def test_parse_without_minutes(self):
        """Test parsing time without minutes."""
        assert parse_laptime("45.123") == pytest.approx(45.123)

    def test_roundtrip_with_minutes(self):
        """Test format -> parse roundtrip with minutes."""
        original = 90.290
        formatted = format_laptime(original)
        parsed = parse_laptime(formatted)
        assert parsed == pytest.approx(original, abs=0.001)

    def test_roundtrip_without_minutes(self):
        """Test format -> parse roundtrip without minutes."""
        original = 45.123
        formatted = format_laptime(original)
        parsed = parse_laptime(formatted)
        assert parsed == pytest.approx(original, abs=0.001)

    def test_parse_two_minutes(self):
        """Test parsing time over 2 minutes."""
        assert parse_laptime("2:05.450") == pytest.approx(125.450)
