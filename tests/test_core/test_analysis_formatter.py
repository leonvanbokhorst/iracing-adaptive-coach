"""
Unit tests for analysis_formatter.py

Tests the formatted output functions for coaching.
"""

import pytest
from tools.core.analysis_formatter import (
    format_comparison,
)


class TestFormatComparison:
    """Test format_comparison function."""

    def test_improved(self):
        """Test formatting when current is faster than previous."""
        result = format_comparison(89.5, 90.0)
        assert "improved" in result
        assert "0.50s" in result
        assert "✓" in result

    def test_slower(self):
        """Test formatting when current is slower than previous."""
        result = format_comparison(90.5, 90.0)
        assert "slower" in result
        assert "0.50s" in result

    def test_no_change(self):
        """Test formatting when times are essentially equal."""
        result = format_comparison(90.005, 90.0)
        assert result == "no change"

    def test_exact_same(self):
        """Test formatting when times are exactly equal."""
        result = format_comparison(90.0, 90.0)
        assert result == "no change"

    def test_significant_improvement(self):
        """Test large improvement formatting."""
        result = format_comparison(88.0, 90.0)
        assert "improved" in result
        assert "2.00s" in result

    def test_significant_regression(self):
        """Test large regression formatting."""
        result = format_comparison(92.0, 90.0)
        assert "slower" in result
        assert "2.00s" in result


class TestPrintSessionAnalysis:
    """Test print_session_analysis function output."""

    def test_prints_without_error(self, capsys):
        """Test that print_session_analysis runs without errors."""
        from tools.core.analysis_formatter import print_session_analysis
        
        analysis = {
            'best_lap': 89.5,
            'avg_lap': 90.2,
            'sigma': 0.65,
            'clean_laps': 8,
            'total_laps': 10,
        }
        
        print_session_analysis(analysis)
        
        captured = capsys.readouterr()
        assert "Session Analysis" in captured.out
        assert "1:29.500" in captured.out  # Formatted best lap
        assert "0.650" in captured.out  # Sigma

    def test_prints_with_sectors(self, capsys):
        """Test print_session_analysis with sector data."""
        from tools.core.analysis_formatter import print_session_analysis
        
        analysis = {
            'best_lap': 89.5,
            'avg_lap': 90.2,
            'sigma': 0.65,
            'clean_laps': 8,
            'total_laps': 10,
        }
        
        sectors = {
            'Sector 1': {
                'best': 29.5,
                'avg': 29.8,
                'worst': 30.5,
                'sigma': 0.3,
                'loss_per_lap': 0.3,
                'total_loss': 2.4,
            },
            'Sector 2': {
                'best': 34.5,
                'avg': 35.2,
                'worst': 36.0,
                'sigma': 0.5,
                'loss_per_lap': 0.7,  # Higher loss
                'total_loss': 5.6,
            },
        }
        
        print_session_analysis(analysis, sectors)
        
        captured = capsys.readouterr()
        assert "Sector Breakdown" in captured.out
        assert "Sector 1" in captured.out
        assert "Sector 2" in captured.out
        assert "Focus here" in captured.out  # Should mark problem sector


class TestPrintCoachingSummary:
    """Test print_coaching_summary function output."""

    def test_prints_without_error(self, capsys):
        """Test that print_coaching_summary runs without errors."""
        from tools.core.analysis_formatter import print_coaching_summary
        
        analysis = {
            'best_lap': 89.5,
            'avg_lap': 90.2,
            'sigma': 0.45,  # Excellent
            'clean_laps': 8,
            'total_laps': 10,
        }
        
        print_coaching_summary(analysis)
        
        captured = capsys.readouterr()
        assert "Little Padawan" in captured.out
        assert "Master Lonn" in captured.out
        assert "1:29.500" in captured.out
        assert "excellent" in captured.out  # Low sigma

    def test_consistency_assessment_good(self, capsys):
        """Test good consistency assessment."""
        from tools.core.analysis_formatter import print_coaching_summary
        
        analysis = {
            'best_lap': 89.5,
            'avg_lap': 90.2,
            'sigma': 0.75,  # Good
            'clean_laps': 8,
            'total_laps': 10,
        }
        
        print_coaching_summary(analysis)
        
        captured = capsys.readouterr()
        assert "good" in captured.out

    def test_consistency_assessment_needs_work(self, capsys):
        """Test poor consistency assessment."""
        from tools.core.analysis_formatter import print_coaching_summary
        
        analysis = {
            'best_lap': 89.5,
            'avg_lap': 92.0,
            'sigma': 1.8,  # Needs work
            'clean_laps': 8,
            'total_laps': 10,
        }
        
        print_coaching_summary(analysis)
        
        captured = capsys.readouterr()
        assert "needs work" in captured.out
