#!/usr/bin/env python3
"""
Coach Tool: Balance Map Visualization (FACTS ONLY)

Visualizes where on track you're understeering, oversteering, or spinning.
Creates a track-position plot showing balance state throughout a lap.

Little Padawan interprets the visual - tool just shows the data.

Usage:
    python tools/coach/visualize_balance_map.py <telemetry.ibt>
    python tools/coach/visualize_balance_map.py <telemetry.ibt> --output balance_map.png
    python tools/coach/visualize_balance_map.py <telemetry.ibt> --track oschersleben-gp
    python tools/coach/visualize_balance_map.py <telemetry.ibt> --lap 4  # Single lap
    python tools/coach/visualize_balance_map.py <telemetry.ibt> --compare 4 6  # Compare two laps
"""

import sys
import json
import argparse
from pathlib import Path
import math

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.collections import LineCollection
    import numpy as np
except ImportError:
    print(json.dumps({"error": "matplotlib/numpy not installed. Run: uv add matplotlib numpy"}))
    sys.exit(1)

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


# =============================================================================
# CONSTANTS (same as analyze_car_balance.py)
# =============================================================================

MIN_ANALYSIS_SPEED_MS = 15  # ~54 km/h
MIN_STEERING_DEG = 5

UNDERSTEER_THRESHOLD = 0.7
NEUTRAL_MIN = 0.85
NEUTRAL_MAX = 1.15
HIGH_ROTATION_THRESHOLD = 1.15
OVERSTEER_THRESHOLD = 1.4
SPIN_THRESHOLD_DEG_S = 65


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def rad_to_deg(rad: float) -> float:
    return rad * (180 / math.pi)


def calculate_expected_yaw_rate(steering_deg: float, speed_ms: float, wheelbase: float = 2.3) -> float:
    """Calculate expected yaw rate using bicycle model."""
    steering_ratio = 14.0
    front_wheel_angle_deg = abs(steering_deg) / steering_ratio
    front_wheel_angle_rad = math.radians(front_wheel_angle_deg)
    
    if front_wheel_angle_rad < 0.001 or speed_ms < 1:
        return 0.0
    
    yaw_rate_rad_s = speed_ms * math.tan(front_wheel_angle_rad) / wheelbase
    return abs(rad_to_deg(yaw_rate_rad_s))


def load_track_data(track_id: str) -> dict:
    """Load track data for corner annotations."""
    track_path = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_path.exists():
        with open(track_path) as f:
            return json.load(f)
    return None


def classify_balance_state(ratio: float, yaw_deg_s: float) -> str:
    """Classify balance state from response ratio and yaw rate."""
    if yaw_deg_s > SPIN_THRESHOLD_DEG_S:
        return "spin"
    elif ratio < UNDERSTEER_THRESHOLD:
        return "understeer"
    elif ratio < NEUTRAL_MIN:
        return "mild_understeer"
    elif ratio <= NEUTRAL_MAX:
        return "neutral"
    elif ratio <= OVERSTEER_THRESHOLD:
        return "high_rotation"
    else:
        return "oversteer"


# =============================================================================
# MAIN VISUALIZATION
# =============================================================================

def load_ibt_data(ibt_path: str, lap: int = None):
    """
    Load telemetry data from IBT file, optionally filtered by lap.
    
    Returns dict with track_positions, response_ratios, balance_states, yaw_rates.
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    required = ["SteeringWheelAngle", "YawRate", "Speed", "LapDistPct"]
    if lap is not None:
        required.append("Lap")
    
    missing = [c for c in required if c not in available]
    if missing:
        ibt.close()
        return {"error": f"Missing required channels: {missing}"}
    
    # Load data
    steering_data = ibt.get_all("SteeringWheelAngle")
    yaw_data = ibt.get_all("YawRate")
    speed_data = ibt.get_all("Speed")
    dist_data = ibt.get_all("LapDistPct")
    lap_data = ibt.get_all("Lap") if lap is not None else None
    
    ibt.close()
    
    # Calculate balance data
    track_positions = []
    response_ratios = []
    balance_states = []
    yaw_rates = []
    
    for i in range(len(steering_data)):
        # Filter by lap if specified
        if lap is not None and int(lap_data[i]) != lap:
            continue
            
        steering_deg = abs(rad_to_deg(steering_data[i]))
        yaw_deg_s = abs(rad_to_deg(yaw_data[i]))
        speed_ms = speed_data[i]
        track_pct = dist_data[i] * 100
        
        # Skip if not in analysis zone
        if speed_ms < MIN_ANALYSIS_SPEED_MS or steering_deg < MIN_STEERING_DEG:
            continue
        
        expected_yaw = calculate_expected_yaw_rate(steering_deg, speed_ms)
        if expected_yaw < 1.0:
            continue
        
        ratio = yaw_deg_s / expected_yaw
        state = classify_balance_state(ratio, yaw_deg_s)
        
        track_positions.append(track_pct)
        response_ratios.append(ratio)
        balance_states.append(state)
        yaw_rates.append(yaw_deg_s)
    
    return {
        "track_positions": track_positions,
        "response_ratios": response_ratios,
        "balance_states": balance_states,
        "yaw_rates": yaw_rates
    }


def create_balance_map(ibt_path: str, output_path: str = None, track_id: str = None, lap: int = None):
    """
    Create a track-position balance map showing where overdriving occurs.
    
    Args:
        ibt_path: Path to IBT file
        output_path: Where to save the image (optional, shows if None)
        track_id: Track ID for corner annotations
        lap: Specific lap to analyze (None = all laps overlaid)
    """
    data = load_ibt_data(ibt_path, lap)
    
    if "error" in data:
        print(json.dumps(data))
        return
    
    track_positions = data["track_positions"]
    response_ratios = data["response_ratios"]
    balance_states = data["balance_states"]
    yaw_rates = data["yaw_rates"]
    
    if not track_positions:
        print(json.dumps({"error": f"No data found for lap {lap}"}))
        return
    
    # Load track data for corner annotations
    track_data = load_track_data(track_id) if track_id else None
    
    # Create the visualization
    fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
    fig.patch.set_facecolor('#1a1a2e')
    
    # Color map for states
    state_colors = {
        "understeer": "#3498db",      # Blue
        "mild_understeer": "#85c1e9", # Light blue
        "neutral": "#2ecc71",         # Green
        "high_rotation": "#f39c12",   # Orange
        "oversteer": "#e74c3c",       # Red
        "spin": "#9b59b6",            # Purple
    }
    
    # === TOP PLOT: Response Ratio vs Track Position ===
    ax1 = axes[0]
    ax1.set_facecolor('#16213e')
    
    # Plot each point colored by state
    for state, color in state_colors.items():
        mask = [s == state for s in balance_states]
        x = [track_positions[i] for i in range(len(mask)) if mask[i]]
        y = [response_ratios[i] for i in range(len(mask)) if mask[i]]
        if x:
            ax1.scatter(x, y, c=color, s=2, alpha=0.5, label=state.replace("_", " ").title())
    
    # Add threshold lines
    ax1.axhline(y=UNDERSTEER_THRESHOLD, color='#3498db', linestyle='--', alpha=0.7, linewidth=1)
    ax1.axhline(y=NEUTRAL_MIN, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=1)
    ax1.axhline(y=NEUTRAL_MAX, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=1)
    ax1.axhline(y=OVERSTEER_THRESHOLD, color='#e74c3c', linestyle='--', alpha=0.7, linewidth=1)
    ax1.axhline(y=1.0, color='white', linestyle='-', alpha=0.3, linewidth=1)
    
    # Zone labels
    ax1.text(101, 0.5, 'UNDERSTEER', color='#3498db', fontsize=8, va='center')
    ax1.text(101, 1.0, 'NEUTRAL', color='#2ecc71', fontsize=8, va='center')
    ax1.text(101, 1.27, 'HIGH ROT', color='#f39c12', fontsize=8, va='center')
    ax1.text(101, 1.6, 'OVERSTEER', color='#e74c3c', fontsize=8, va='center')
    
    ax1.set_ylabel('Response Ratio\n(actual/expected yaw)', color='white', fontsize=10)
    ax1.set_ylim(0, 2.5)
    ax1.tick_params(colors='white')
    ax1.spines['bottom'].set_color('#444')
    ax1.spines['left'].set_color('#444')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.grid(True, alpha=0.2, color='white')
    
    # Legend
    ax1.legend(loc='upper left', fontsize=8, framealpha=0.8, facecolor='#16213e', 
               edgecolor='#444', labelcolor='white')
    
    # === BOTTOM PLOT: Yaw Rate vs Track Position ===
    ax2 = axes[1]
    ax2.set_facecolor('#16213e')
    
    # Plot yaw rate colored by state
    for state, color in state_colors.items():
        mask = [s == state for s in balance_states]
        x = [track_positions[i] for i in range(len(mask)) if mask[i]]
        y = [yaw_rates[i] for i in range(len(mask)) if mask[i]]
        if x:
            ax2.scatter(x, y, c=color, s=2, alpha=0.5)
    
    # Spin threshold
    ax2.axhline(y=SPIN_THRESHOLD_DEG_S, color='#9b59b6', linestyle='--', alpha=0.7, linewidth=1)
    ax2.text(101, SPIN_THRESHOLD_DEG_S, 'SPIN', color='#9b59b6', fontsize=8, va='center')
    
    ax2.set_xlabel('Track Position (%)', color='white', fontsize=10)
    ax2.set_ylabel('Yaw Rate (°/s)', color='white', fontsize=10)
    ax2.set_xlim(0, 100)
    ax2.tick_params(colors='white')
    ax2.spines['bottom'].set_color('#444')
    ax2.spines['left'].set_color('#444')
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.grid(True, alpha=0.2, color='white')
    
    # Add corner annotations if track data available
    if track_data and "turn" in track_data:
        for turn in track_data["turn"]:
            turn_start = turn["start"] * 100
            turn_name = turn["name"]
            # Add vertical line at corner start
            ax1.axvline(x=turn_start, color='white', alpha=0.2, linewidth=0.5)
            ax2.axvline(x=turn_start, color='white', alpha=0.2, linewidth=0.5)
            # Add corner label
            ax2.text(turn_start + 0.5, ax2.get_ylim()[1] * 0.95, turn_name, 
                    color='white', fontsize=6, rotation=90, va='top', alpha=0.6)
    
    # Title
    filename = Path(ibt_path).stem
    lap_str = f" - Lap {lap}" if lap else " - All Laps"
    fig.suptitle(f'Balance Map: {filename}{lap_str}', color='white', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor='#1a1a2e', edgecolor='none', 
                   bbox_inches='tight')
        print(json.dumps({"success": True, "output": output_path}))
    else:
        plt.show()
    
    plt.close()


def create_lap_comparison(ibt_path: str, lap1: int, lap2: int, output_path: str = None, track_id: str = None):
    """
    Create side-by-side comparison of two laps' balance maps.
    
    Args:
        ibt_path: Path to IBT file
        lap1: First lap number (left side)
        lap2: Second lap number (right side)
        output_path: Where to save the image
        track_id: Track ID for corner annotations
    """
    # Load data for both laps
    data1 = load_ibt_data(ibt_path, lap1)
    data2 = load_ibt_data(ibt_path, lap2)
    
    if "error" in data1:
        print(json.dumps(data1))
        return
    if "error" in data2:
        print(json.dumps(data2))
        return
    
    # Load track data for corner annotations
    track_data = load_track_data(track_id) if track_id else None
    
    # Color map for states
    state_colors = {
        "understeer": "#3498db",
        "mild_understeer": "#85c1e9",
        "neutral": "#2ecc71",
        "high_rotation": "#f39c12",
        "oversteer": "#e74c3c",
        "spin": "#9b59b6",
    }
    
    # Create figure with 2x2 subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 10), sharex=True, sharey='row')
    fig.patch.set_facecolor('#1a1a2e')
    
    # Count events for each lap
    def count_events(data):
        counts = {"understeer": 0, "oversteer": 0, "spin": 0, "neutral": 0}
        for state in data["balance_states"]:
            if state in ["understeer", "mild_understeer"]:
                counts["understeer"] += 1
            elif state in ["oversteer", "high_rotation"]:
                counts["oversteer"] += 1
            elif state == "spin":
                counts["spin"] += 1
            else:
                counts["neutral"] += 1
        return counts
    
    counts1 = count_events(data1)
    counts2 = count_events(data2)
    
    for col, (data, lap_num, counts) in enumerate([(data1, lap1, counts1), (data2, lap2, counts2)]):
        track_positions = data["track_positions"]
        response_ratios = data["response_ratios"]
        balance_states = data["balance_states"]
        yaw_rates = data["yaw_rates"]
        
        # TOP ROW: Response Ratio
        ax_top = axes[0, col]
        ax_top.set_facecolor('#16213e')
        
        for state, color in state_colors.items():
            mask = [s == state for s in balance_states]
            x = [track_positions[i] for i in range(len(mask)) if mask[i]]
            y = [response_ratios[i] for i in range(len(mask)) if mask[i]]
            if x:
                ax_top.scatter(x, y, c=color, s=3, alpha=0.6)
        
        # Threshold lines
        ax_top.axhline(y=UNDERSTEER_THRESHOLD, color='#3498db', linestyle='--', alpha=0.5, linewidth=1)
        ax_top.axhline(y=OVERSTEER_THRESHOLD, color='#e74c3c', linestyle='--', alpha=0.5, linewidth=1)
        ax_top.axhline(y=1.0, color='white', linestyle='-', alpha=0.2, linewidth=1)
        
        # Stats box
        stats_text = f"US: {counts['understeer']}  OS: {counts['oversteer']}  SP: {counts['spin']}"
        ax_top.text(50, 2.35, stats_text, color='white', fontsize=9, ha='center',
                   bbox=dict(boxstyle='round', facecolor='#16213e', edgecolor='#444', alpha=0.9))
        
        ax_top.set_title(f'Lap {lap_num}', color='white', fontsize=12, fontweight='bold')
        ax_top.set_ylim(0, 2.5)
        ax_top.tick_params(colors='white')
        ax_top.spines['bottom'].set_color('#444')
        ax_top.spines['left'].set_color('#444')
        ax_top.spines['top'].set_visible(False)
        ax_top.spines['right'].set_visible(False)
        ax_top.grid(True, alpha=0.15, color='white')
        
        if col == 0:
            ax_top.set_ylabel('Response Ratio', color='white', fontsize=10)
        
        # BOTTOM ROW: Yaw Rate
        ax_bot = axes[1, col]
        ax_bot.set_facecolor('#16213e')
        
        for state, color in state_colors.items():
            mask = [s == state for s in balance_states]
            x = [track_positions[i] for i in range(len(mask)) if mask[i]]
            y = [yaw_rates[i] for i in range(len(mask)) if mask[i]]
            if x:
                ax_bot.scatter(x, y, c=color, s=3, alpha=0.6)
        
        ax_bot.axhline(y=SPIN_THRESHOLD_DEG_S, color='#9b59b6', linestyle='--', alpha=0.5, linewidth=1)
        
        ax_bot.set_xlabel('Track Position (%)', color='white', fontsize=10)
        ax_bot.set_xlim(0, 100)
        ax_bot.tick_params(colors='white')
        ax_bot.spines['bottom'].set_color('#444')
        ax_bot.spines['left'].set_color('#444')
        ax_bot.spines['top'].set_visible(False)
        ax_bot.spines['right'].set_visible(False)
        ax_bot.grid(True, alpha=0.15, color='white')
        
        if col == 0:
            ax_bot.set_ylabel('Yaw Rate (°/s)', color='white', fontsize=10)
        
        # Add corner annotations
        if track_data and "turn" in track_data:
            for turn in track_data["turn"]:
                turn_start = turn["start"] * 100
                ax_top.axvline(x=turn_start, color='white', alpha=0.15, linewidth=0.5)
                ax_bot.axvline(x=turn_start, color='white', alpha=0.15, linewidth=0.5)
    
    # Overall title
    filename = Path(ibt_path).stem
    
    # Determine which lap is "better"
    total1 = counts1["oversteer"] + counts1["spin"] * 5  # Weight spins heavily
    total2 = counts2["oversteer"] + counts2["spin"] * 5
    
    if total1 < total2:
        comparison = f"Lap {lap1} cleaner ({total1} vs {total2} weighted events)"
    elif total2 < total1:
        comparison = f"Lap {lap2} cleaner ({total2} vs {total1} weighted events)"
    else:
        comparison = "Both laps similar"
    
    fig.suptitle(f'Lap Comparison: {filename}\n{comparison}', 
                 color='white', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor='#1a1a2e', edgecolor='none',
                   bbox_inches='tight')
        print(json.dumps({"success": True, "output": output_path}))
    else:
        plt.show()
    
    plt.close()


def create_corner_balance_chart(ibt_path: str, track_id: str, output_path: str = None):
    """
    Create a bar chart showing balance issues per corner.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID (required for corner data)
        output_path: Where to save the image
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        print(json.dumps({"error": f"Failed to open IBT file: {str(e)}"}))
        return
    
    available = set(ibt.var_headers_names or [])
    
    # Load data
    steering_data = ibt.get_all("SteeringWheelAngle")
    yaw_data = ibt.get_all("YawRate")
    speed_data = ibt.get_all("Speed")
    dist_data = ibt.get_all("LapDistPct")
    
    ibt.close()
    
    # Load track data
    track_data = load_track_data(track_id)
    if not track_data or "turn" not in track_data:
        print(json.dumps({"error": f"No track data for {track_id}"}))
        return
    
    # Count events per corner
    corner_data = {}
    for turn in track_data["turn"]:
        corner_data[turn["name"]] = {
            "understeer": 0,
            "oversteer": 0,
            "spin": 0,
            "start": turn["start"],
            "end": turn["end"],
        }
    
    # Classify each sample
    for i in range(len(steering_data)):
        steering_deg = abs(rad_to_deg(steering_data[i]))
        yaw_deg_s = abs(rad_to_deg(yaw_data[i]))
        speed_ms = speed_data[i]
        track_pct = dist_data[i]
        
        if speed_ms < MIN_ANALYSIS_SPEED_MS or steering_deg < MIN_STEERING_DEG:
            continue
        
        expected_yaw = calculate_expected_yaw_rate(steering_deg, speed_ms)
        if expected_yaw < 1.0:
            continue
        
        ratio = yaw_deg_s / expected_yaw
        state = classify_balance_state(ratio, yaw_deg_s)
        
        # Find which corner this belongs to
        for name, data in corner_data.items():
            if data["start"] <= track_pct <= data["end"]:
                if state in ["understeer", "mild_understeer"]:
                    data["understeer"] += 1
                elif state in ["oversteer", "high_rotation"]:
                    data["oversteer"] += 1
                elif state == "spin":
                    data["spin"] += 1
                break
    
    # Create visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.patch.set_facecolor('#1a1a2e')
    ax.set_facecolor('#16213e')
    
    corners = list(corner_data.keys())
    x = np.arange(len(corners))
    width = 0.25
    
    understeer_counts = [corner_data[c]["understeer"] for c in corners]
    oversteer_counts = [corner_data[c]["oversteer"] for c in corners]
    spin_counts = [corner_data[c]["spin"] for c in corners]
    
    # Normalize to percentages (samples per corner vary)
    max_per_corner = [max(understeer_counts[i] + oversteer_counts[i] + spin_counts[i], 1) 
                      for i in range(len(corners))]
    
    bars1 = ax.bar(x - width, understeer_counts, width, label='Understeer', color='#3498db', alpha=0.8)
    bars2 = ax.bar(x, oversteer_counts, width, label='Oversteer', color='#e74c3c', alpha=0.8)
    bars3 = ax.bar(x + width, spin_counts, width, label='Spin', color='#9b59b6', alpha=0.8)
    
    ax.set_xlabel('Corner', color='white', fontsize=10)
    ax.set_ylabel('Event Count', color='white', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(corners, rotation=45, ha='right', fontsize=8, color='white')
    ax.tick_params(colors='white')
    ax.legend(facecolor='#16213e', edgecolor='#444', labelcolor='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, axis='y', alpha=0.2, color='white')
    
    filename = Path(ibt_path).stem
    fig.suptitle(f'Corner Balance Breakdown: {filename}', color='white', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, facecolor='#1a1a2e', edgecolor='none',
                   bbox_inches='tight')
        print(json.dumps({"success": True, "output": output_path}))
    else:
        plt.show()
    
    plt.close()


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Visualize car balance (understeer/oversteer) on track map"
    )
    parser.add_argument("ibt_file", help="Path to IBT telemetry file")
    parser.add_argument("--output", "-o", help="Output image path (shows if not specified)")
    parser.add_argument("--track", help="Track ID for corner annotations (e.g., oschersleben-gp)")
    parser.add_argument("--chart", choices=["map", "corners"], default="map",
                       help="Chart type: 'map' (track position) or 'corners' (bar chart)")
    parser.add_argument("--lap", type=int, help="Specific lap to analyze")
    parser.add_argument("--compare", nargs=2, type=int, metavar=("LAP1", "LAP2"),
                       help="Compare two laps side-by-side (e.g., --compare 4 6)")
    
    args = parser.parse_args()
    
    # Compare mode takes priority
    if args.compare:
        create_lap_comparison(args.ibt_file, args.compare[0], args.compare[1], 
                             args.output, args.track)
    elif args.chart == "map":
        create_balance_map(args.ibt_file, args.output, args.track, args.lap)
    elif args.chart == "corners":
        if not args.track:
            print(json.dumps({"error": "Corner chart requires --track argument"}))
            return
        create_corner_balance_chart(args.ibt_file, args.track, args.output)


if __name__ == "__main__":
    main()

