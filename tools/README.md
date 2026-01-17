# Tools Architecture: Facts vs Meaning

## Philosophy

**Tools provide FACTS. Little Padawan provides MEANING.**

Tools output pure JSON data with zero interpretation. Little Padawan reads the facts, interprets them in context, and coaches Master Lonn.

---

## Quick Reference

```bash
# Run all tests
uv run pytest

# Run smoke tests only (fast, checks all 42 tools)
uv run pytest tests/test_smoke.py

# Run unit tests only
uv run pytest tests/test_core/

# Run with coverage
uv run pytest --cov=tools
```

---

## Directory Structure

```
tools/
├── core/           # Foundation tools (data loading, formatting)
├── coach/          # Coaching analysis tools (technique, standings)
├── viz/            # Visualization tools (charts, heatmaps)
└── README.md       # This file

tests/
├── conftest.py          # Shared fixtures
├── test_smoke.py        # Import & CLI tests for all tools
└── test_core/           # Unit tests for core libraries
    ├── test_time_formatter.py
    ├── test_data_loader.py
    └── test_analysis_formatter.py
```

---

## Tool Inventory (42 tools)

### Tier 1 - CORE WORKFLOW (13 tools)
Actively used in `.cursor/commands/` and coaching workflows.

| Tool | Purpose | Input |
|------|---------|-------|
| `core/extract_session_from_ibt.py` | Extract session data from IBT files | IBT file |
| `core/analyze_session.py` | Session statistics and analysis | CSV file |
| `core/generate_weekly_standings_report.py` | Weekly standings report | CSV file |
| `coach/analyze_ibt_technique.py` | Technique analysis from telemetry | IBT file |
| `coach/detect_apex_points.py` | Apex point detection | IBT file |
| `coach/detect_brake_point_drift.py` | Brake point consistency | IBT file |
| `coach/analyze_input_smoothness.py` | Input smoothness analysis | IBT file |
| `coach/visualize_standings_progression.py` | Season progression charts | CSV files |
| `coach/visualize_irating_distribution.py` | iRating distribution chart | CSV file |
| `viz/corner_entry_traces.py` | Corner entry visualization | IBT file |
| `viz/consistency_heatmap.py` | Consistency heatmap | IBT file |
| `viz/lap_evolution_chart.py` | Lap evolution chart | JSON file |
| `viz/brake_variance_chart.py` | Brake variance chart | JSON/IBT file |

### Tier 2 - LIBRARY (6 tools)
Internal modules used by other tools.

| Tool | Purpose |
|------|---------|
| `core/time_formatter.py` | Lap time formatting utilities |
| `core/data_loader.py` | CSV loading and session analysis |
| `core/analysis_formatter.py` | Formatted output for coaching |
| `core/track_data_loader.py` | Track JSON data loading |
| `core/corner_identifier.py` | Corner identification from track data |
| `core/parse_ibt.py` | IBT file parsing (foundation for IBT tools) |

### Tier 3 - DOCUMENTED (10 tools)
Documented in workflows but not in primary commands.

| Tool | Purpose | Docs |
|------|---------|------|
| `coach/analyze_car_balance.py` | Understeer/oversteer detection | tools/README.md |
| `coach/analyze_braking_technique.py` | Brake zone analysis | tools/README.md |
| `coach/analyze_telemetry.py` | General telemetry analysis | coaching-handbook |
| `coach/compare_laps.py` | Lap-to-lap comparison | tools/README.md |
| `coach/compare_telemetry.py` | Two-lap telemetry comparison | tools/README.md |
| `coach/compare_weekly_standings.py` | Week-over-week standings | standings-workflow |
| `coach/track_rivals.py` | Rival tracking | standings-workflow |
| `coach/analyze_standings.py` | Standings analysis | standings-workflow |
| `core/extract_lap_telemetry.py` | Single lap extraction | ibt-coaching-system-plan |
| `core/generate_track_map.py` | Track map generation | create-track-profile |

### Tier 4 - UTILITY & ASSET GENERATION (13 tools)
Visualization and utility tools used for guidebook assets.

| Tool | Purpose |
|------|---------|
| `coach/visualize_6dof_pairs.py` | 6DOF pair visualization (generated assets/) |
| `coach/visualize_traction_circle.py` | Traction circle charts |
| `coach/visualize_driver_traction_circle.py` | Driver-specific traction circles |
| `coach/visualize_racing_lines.py` | Racing line visualization |
| `coach/visualize_sector_comparison.py` | Sector comparison charts |
| `coach/visualize_track_comparison.py` | Track comparison visualization |
| `coach/visualize_corner_detail.py` | Corner detail analysis |
| `coach/visualize_deviation_from_reference.py` | Deviation visualization |
| `coach/aggregate_track_boundaries.py` | Track boundary aggregation |
| `coach/validate_against_boundaries.py` | Boundary validation |
| `coach/demo_corner_analysis.py` | Demo/example code |
| `core/data_summary.py` | Data cleaning summary utilities |
| `coach/generate_corrected_progression_charts.py` | **DEPRECATED** - hardcoded S1 2026 data |

---

## Core Tool Characteristics

- Output pure JSON
- No interpretation
- No coaching language
- Just numbers and data
- No "you should" or "focus on"
- No rule-based logic

### Example: `analyze_session.py`

**Bad (rule-based interpretation)**:

```json
{
  "sector_2": {
    "status": "needs_work",
    "recommendation": "Focus on Sector 2 consistency"
  }
}
```

**Good (pure facts)**:

```json
{
  "sectors": {
    "Sector 2": {
      "best": 30.845,
      "average": 31.807,
      "sigma": 0.748,
      "loss_per_lap": 0.961
    }
  }
}
```

Little Padawan reads this and decides:

- "Sector 2 has 3x more loss than others → focus area"
- "σ = 0.748s → consistency issue"
- "Does Master Lonn need a visualization?"

---

## Car Balance Analysis (`analyze_car_balance.py`)

**FACTS ONLY** - Outputs raw telemetry data for Little Padawan to interpret.

**What It Measures (raw numbers, no interpretation):**

- **Steering Response Ratio** - Expected vs actual yaw rate
- **Balance Distribution** - Percentages in each state (understeer/neutral/high_rotation/oversteer)
- **Event Counts** - Raw counts of understeer, oversteer, spins
- **Transitions** - Where state changes occur (track position, ratio, yaw rate)
- **Input Smoothness** - Steering rate statistics (avg, max, std, distribution by rate bands)
- **Tire Temperatures** - Peak, session avg, cornering temps (L/M/R for each tire)
- **Delta Correlation** - Delta change during balance events
- **Corner Breakdown** - Per-corner counts (when track data provided)

**Usage:**

```bash
uv run python tools/coach/analyze_car_balance.py telemetry.ibt
uv run python tools/coach/analyze_car_balance.py telemetry.ibt --track oschersleben-gp
uv run python tools/coach/analyze_car_balance.py telemetry.ibt --pretty
```

**Example Output (FACTS, no interpretation):**

```json
{
  "balance_distribution_pct": {
    "understeer": 16.7,
    "neutral": 50.6,
    "oversteer": 15.5
  },
  "event_counts": { "understeer": 8991, "oversteer": 8345, "spins": 26 },
  "input_smoothness": {
    "avg_steering_rate_deg_s": 29.0,
    "max_steering_rate_deg_s": 619.2
  },
  "tire_analysis": {
    "left_front": { "peak_avg_c": 98.2, "cornering_max_R_c": 96.0 }
  },
  "corners": { "T1": { "understeer_count": 403, "oversteer_count": 670 } }
}
```

**Little Padawan interprets these facts:**

- "RF peak 134°C? Above 110° = overheating tire"
- "16.7% understeer vs 15.5% oversteer? Balanced."
- "98.7% inputs under 150 deg/s? Butter smooth!"

---

## Testing

### Running Tests

```bash
# All tests
uv run pytest

# Verbose with short traceback
uv run pytest -v --tb=short

# Specific test file
uv run pytest tests/test_smoke.py

# Specific test class
uv run pytest tests/test_core/test_time_formatter.py::TestFormatLaptime

# With coverage report
uv run pytest --cov=tools --cov-report=term-missing
```

### Test Structure

| Test File | What It Tests |
|-----------|---------------|
| `test_smoke.py` | All 42 tools import correctly, CLI --help works |
| `test_time_formatter.py` | Lap time formatting functions |
| `test_data_loader.py` | CSV loading, session analysis |
| `test_analysis_formatter.py` | Output formatting functions |

### Adding New Tests

1. Create test file in appropriate directory (`tests/test_core/`, etc.)
2. Use fixtures from `conftest.py` for sample data
3. Follow naming convention: `test_*.py`, functions `test_*`

---

## How Little Padawan Uses Tools

### 1. Run Tool

```bash
uv run python tools/core/analyze_session.py data/session.csv
```

### 2. Read JSON Facts

```python
import subprocess
import json

result = subprocess.run(
    ['uv', 'run', 'python', 'tools/core/analyze_session.py', 'data/session.csv'],
    capture_output=True,
    text=True
)

facts = json.loads(result.stdout)
```

### 3. Interpret Facts

```python
# Little Padawan's interpretation logic
sector_losses = {name: data['loss_per_lap']
                 for name, data in facts['sectors'].items()}

max_loss_sector = max(sector_losses, key=sector_losses.get)
max_loss = sector_losses[max_loss_sector]
avg_loss = sum(sector_losses.values()) / len(sector_losses)

if max_loss > 2 * avg_loss:
    focus_area = max_loss_sector
    # This is where Master Lonn should focus
```

### 4. Coach Master Lonn

```
"Master Lonn, I analyzed your session.

Sector 2 is your focus area:
- Loss per lap: 0.96s
- That's 3x more than other sectors
- Best: 30.85s, Average: 31.81s

Let's work on Sector 2 consistency.
Goal: Average under 31.0s

Want me to show you a chart of your S2 times?"
```

---

## Creating New Tools

### Template

```python
#!/usr/bin/env python3
"""
Core Tool: [Tool Name] (FACTS ONLY)

This tool outputs PURE FACTS as JSON. No interpretation, no coaching.
Little Padawan reads this output and gives it meaning.

Usage:
    uv run python tools/core/tool_name.py <args>

Output: JSON with factual data
"""

import json
import argparse
import pandas as pd
from pathlib import Path


def load_data(file_path):
    """Load input data from file"""
    path = Path(file_path)
    if path.suffix == '.csv':
        return pd.read_csv(path)
    elif path.suffix == '.json':
        with open(path) as f:
            return json.load(f)
    else:
        raise ValueError(f"Unsupported file type: {path.suffix}")


def analyze_facts(df):
    """Return pure facts as dictionary"""
    facts = {
        "row_count": len(df),
        "columns": list(df.columns),
        # Only numbers and data, no interpretation
    }
    return facts


def main():
    parser = argparse.ArgumentParser(description="Tool description")
    parser.add_argument("input_file", help="Input file path")
    parser.add_argument("-o", "--output", help="Output file path")
    args = parser.parse_args()
    
    # Load data
    data = load_data(args.input_file)
    
    # Analyze and output facts
    facts = analyze_facts(data)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(facts, f, indent=2)
    else:
        print(json.dumps(facts, indent=2))


if __name__ == "__main__":
    main()
```

### Rules

1. Output must be valid JSON
2. No interpretation in output
3. No coaching language
4. Pure numbers and data structures
5. Handle errors gracefully (return error in JSON)
6. Include `--help` support via argparse

---

## Bottom Line

**Tools = Facts (JSON)**
**Little Padawan = Meaning (Coaching)**

This separation allows Little Padawan to be truly adaptive, not rule-based.
