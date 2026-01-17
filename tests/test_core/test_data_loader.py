"""
Unit tests for data_loader.py

Tests CSV loading, session analysis, and sector analysis functions.
"""

import pytest
import pandas as pd
from io import StringIO
from pathlib import Path
from tools.core.data_loader import (
    load_session_data,
    analyze_session_basic,
    analyze_sectors,
)


@pytest.fixture
def sample_csv_content():
    """Sample CSV content matching Garage 61 export format."""
    return """Lap,Lap time,Clean,Inc,Sector 1,Sector 2,Sector 3
1,90.500,1,0,30.100,35.200,25.200
2,89.800,1,0,29.900,34.900,25.000
3,91.200,0,1,30.500,35.500,25.200
4,89.500,1,0,29.800,34.700,25.000
5,90.100,1,0,30.000,35.100,25.000
6,180.000,0,0,60.000,70.000,50.000
7,89.900,1,0,29.850,35.000,25.050
"""


@pytest.fixture
def sample_df(sample_csv_content):
    """Load sample CSV into DataFrame."""
    df = pd.read_csv(StringIO(sample_csv_content))
    return df


class TestLoadSessionData:
    """Test load_session_data function."""

    def test_column_normalization(self, tmp_path, sample_csv_content):
        """Test that column names are normalized."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        
        # Should normalize 'Lap time' to 'LapTime'
        assert 'LapTime' in df.columns

    def test_removes_zero_laptimes(self, tmp_path):
        """Test that zero lap times are removed."""
        csv_content = """Lap,Lap time,Clean
1,90.500,1
2,0,1
3,89.800,1
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        df = load_session_data(str(csv_file))
        
        assert len(df) == 2  # Zero lap time row removed
        assert 0 not in df['LapTime'].values

    def test_marks_outliers(self, tmp_path):
        """Test that extreme outliers are marked."""
        # Create data with a clear outlier (4x median time for pit stop)
        csv_content = """Lap,Lap time,Clean,Inc
1,90.500,1,0
2,89.800,1,0
3,89.500,1,0
4,360.000,1,0
5,90.100,1,0
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        df = load_session_data(str(csv_file))
        
        # Lap 4 (360s) should be marked as outlier (>2x median of ~90s)
        outlier_rows = df[df['is_outlier']]
        assert len(outlier_rows) >= 1

    def test_marks_clean_laps(self, tmp_path, sample_csv_content):
        """Test that clean laps are identified correctly."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        
        # Laps with Inc=1 or outliers should not be clean
        clean_count = df['clean'].sum()
        assert clean_count < len(df)


class TestAnalyzeSessionBasic:
    """Test analyze_session_basic function."""

    def test_basic_analysis(self, tmp_path, sample_csv_content):
        """Test basic session statistics."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        analysis = analyze_session_basic(df)
        
        assert analysis is not None
        assert 'best_lap' in analysis
        assert 'avg_lap' in analysis
        assert 'sigma' in analysis
        assert 'total_laps' in analysis
        assert 'clean_laps' in analysis

    def test_best_lap_is_minimum(self, tmp_path, sample_csv_content):
        """Test that best lap is the minimum clean lap time."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        analysis = analyze_session_basic(df)
        
        # Best lap should be around 89.5 (the fastest clean lap)
        assert analysis['best_lap'] < 91.0
        assert analysis['best_lap'] >= 89.0

    def test_returns_none_for_no_clean_laps(self, tmp_path):
        """Test returns None when no clean laps exist."""
        csv_content = """Lap,Lap time,Clean
1,90.500,0
2,89.800,0
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        df = load_session_data(str(csv_file))
        analysis = analyze_session_basic(df)
        
        assert analysis is None


class TestAnalyzeSectors:
    """Test analyze_sectors function."""

    def test_sector_analysis(self, tmp_path, sample_csv_content):
        """Test sector analysis returns correct structure."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        sectors = analyze_sectors(df)
        
        assert 'Sector 1' in sectors
        assert 'Sector 2' in sectors
        assert 'Sector 3' in sectors

    def test_sector_contains_required_fields(self, tmp_path, sample_csv_content):
        """Test each sector has required analysis fields."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        sectors = analyze_sectors(df)
        
        for sector_name, sector_data in sectors.items():
            assert 'best' in sector_data
            assert 'avg' in sector_data
            assert 'worst' in sector_data
            assert 'sigma' in sector_data
            assert 'loss_per_lap' in sector_data
            assert 'total_loss' in sector_data

    def test_loss_per_lap_calculation(self, tmp_path, sample_csv_content):
        """Test that loss_per_lap is average - best."""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(sample_csv_content)
        
        df = load_session_data(str(csv_file))
        sectors = analyze_sectors(df)
        
        for sector_name, sector_data in sectors.items():
            expected_loss = sector_data['avg'] - sector_data['best']
            assert sector_data['loss_per_lap'] == pytest.approx(expected_loss)

    def test_empty_df_returns_empty_dict(self, tmp_path):
        """Test that empty dataframe returns empty dict."""
        csv_content = """Lap,Lap time,Clean,Sector 1,Sector 2
1,90.500,0,30.0,35.0
"""
        csv_file = tmp_path / "test.csv"
        csv_file.write_text(csv_content)
        
        df = load_session_data(str(csv_file))
        sectors = analyze_sectors(df)
        
        # No clean laps, so should return empty
        assert sectors == {}
