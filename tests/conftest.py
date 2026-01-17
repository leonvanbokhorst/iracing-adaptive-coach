"""
Shared pytest fixtures for tool tests.

Provides:
- Sample data paths
- Temp directory fixtures
- Skip markers for tests requiring real telemetry
"""

import pytest
from pathlib import Path


@pytest.fixture
def project_root():
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def data_dir(project_root):
    """Return the data directory."""
    return project_root / "data"


@pytest.fixture
def tools_dir(project_root):
    """Return the tools directory."""
    return project_root / "tools"


@pytest.fixture
def sample_ibt(data_dir):
    """Return path to sample IBT file, or skip if not available."""
    ibt_files = list(data_dir.glob("*.ibt"))
    if not ibt_files:
        pytest.skip("No IBT files available for testing")
    return ibt_files[0]


@pytest.fixture
def sample_standings_csv(data_dir):
    """Return path to a sample standings CSV."""
    standings_dir = data_dir / "standings"
    csv_files = list(standings_dir.glob("*.csv"))
    if not csv_files:
        pytest.skip("No standings CSV files available")
    return csv_files[0]


@pytest.fixture
def sample_telemetry_csv(data_dir):
    """Return path to a sample telemetry CSV."""
    compare_dir = data_dir / "compare"
    csv_files = list(compare_dir.glob("*.csv"))
    if not csv_files:
        pytest.skip("No telemetry CSV files available")
    return csv_files[0]


@pytest.fixture
def tracks_dir(project_root):
    """Return the tracks directory."""
    return project_root / "tracks"


@pytest.fixture
def track_data_dir(tracks_dir):
    """Return the track-data directory with JSON track configs."""
    return tracks_dir / "track-data"


# Tool discovery helpers
def get_all_tools(tools_dir: Path) -> list[Path]:
    """Get all Python tool files."""
    tools = []
    for subdir in ["core", "coach", "viz"]:
        subpath = tools_dir / subdir
        if subpath.exists():
            tools.extend(subpath.glob("*.py"))
    return sorted(tools)


@pytest.fixture
def all_tool_paths(tools_dir):
    """Return paths to all tool Python files."""
    return get_all_tools(tools_dir)


@pytest.fixture
def core_tools(tools_dir):
    """Return paths to core tools only."""
    return sorted((tools_dir / "core").glob("*.py"))


@pytest.fixture
def coach_tools(tools_dir):
    """Return paths to coach tools only."""
    return sorted((tools_dir / "coach").glob("*.py"))


@pytest.fixture
def viz_tools(tools_dir):
    """Return paths to viz tools only."""
    return sorted((tools_dir / "viz").glob("*.py"))
