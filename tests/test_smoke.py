"""
Smoke tests for all tools.

Tests that:
1. All tools can be imported without crashing
2. All CLI tools can run --help without crashing
"""

import subprocess
import sys
from pathlib import Path

import pytest

# Get project root
PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / "tools"


def get_tool_modules():
    """Get all tool Python files as module paths."""
    tools = []
    for subdir in ["core", "coach", "viz"]:
        subpath = TOOLS_DIR / subdir
        if subpath.exists():
            for py_file in sorted(subpath.glob("*.py")):
                if py_file.name.startswith("__"):
                    continue
                module_path = f"tools.{subdir}.{py_file.stem}"
                tools.append((module_path, py_file))
    return tools


# Parametrize with all tool modules
ALL_TOOLS = get_tool_modules()
TOOL_IDS = [t[0] for t in ALL_TOOLS]


class TestToolImports:
    """Test that all tools can be imported."""

    @pytest.mark.parametrize("module_path,file_path", ALL_TOOLS, ids=TOOL_IDS)
    def test_import(self, module_path, file_path):
        """Test that each tool module can be imported without errors."""
        result = subprocess.run(
            [sys.executable, "-c", f"import {module_path}"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=30,
        )
        assert result.returncode == 0, (
            f"Failed to import {module_path}:\n"
            f"stdout: {result.stdout}\n"
            f"stderr: {result.stderr}"
        )


class TestToolHelp:
    """Test that CLI tools can show help."""

    @pytest.mark.parametrize("module_path,file_path", ALL_TOOLS, ids=TOOL_IDS)
    def test_help_flag(self, module_path, file_path):
        """Test that each tool with argparse responds to --help."""
        result = subprocess.run(
            [sys.executable, str(file_path), "--help"],
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=30,
        )
        # Allow exit code 0 (success) or 2 (argparse with required args missing)
        # Some tools may not have --help if they don't use argparse
        if result.returncode not in (0, 2):
            # Check if it's just a tool without argparse (no main/argparse)
            content = file_path.read_text()
            if "argparse" not in content and "ArgumentParser" not in content:
                pytest.skip(f"{module_path} does not use argparse")
            else:
                pytest.fail(
                    f"--help failed for {module_path} (exit {result.returncode}):\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )


class TestToolInventory:
    """Verify tool counts match expectations."""

    def test_core_tool_count(self):
        """Verify we have the expected number of core tools."""
        core_tools = list((TOOLS_DIR / "core").glob("*.py"))
        core_tools = [t for t in core_tools if not t.name.startswith("__")]
        assert len(core_tools) >= 10, f"Expected at least 10 core tools, found {len(core_tools)}"

    def test_coach_tool_count(self):
        """Verify we have the expected number of coach tools."""
        coach_tools = list((TOOLS_DIR / "coach").glob("*.py"))
        coach_tools = [t for t in coach_tools if not t.name.startswith("__")]
        assert len(coach_tools) >= 20, f"Expected at least 20 coach tools, found {len(coach_tools)}"

    def test_viz_tool_count(self):
        """Verify we have the expected number of viz tools."""
        viz_tools = list((TOOLS_DIR / "viz").glob("*.py"))
        viz_tools = [t for t in viz_tools if not t.name.startswith("__")]
        assert len(viz_tools) >= 4, f"Expected at least 4 viz tools, found {len(viz_tools)}"

    def test_total_tool_count(self):
        """Verify total tool count."""
        all_tools = get_tool_modules()
        assert len(all_tools) >= 40, f"Expected at least 40 tools total, found {len(all_tools)}"
