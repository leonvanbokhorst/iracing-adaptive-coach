#!/usr/bin/env python3
"""
Visualization Tool: Lap Evolution Chart

Shows lap times over the session to visualize:
- Learning curve (improving?)
- Fatigue (degrading at end?)
- Outliers (incidents/offs)

Usage:
    python tools/viz/lap_evolution_chart.py <telemetry.ibt> --track oschersleben-gp
    python tools/viz/lap_evolution_chart.py <telemetry.ibt> --track oschersleben-gp -o evolution.png

Output: PNG image
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print(json.dumps({"error": "matplotlib not installed. Run: uv add matplotlib"}))
    sys.exit(1)

# Import our session extractor
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.extract_session_from_ibt import extract_session


def generate_lap_evolution_chart(
    ibt_path: str,
    track_id: Optional[str] = None,
    output_path: Optional[str] = None,
    show: bool = False
) -> dict:
    """
    Generate a lap time evolution chart.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID (optional, for track name)
        output_path: Output PNG path (optional)
        show: Show plot interactively
    
    Returns:
        dict with status and file path
    """
    # Extract session data
    session_data = extract_session(ibt_path, track_id)
    
    if "error" in session_data:
        return session_data
    
    laps = session_data.get("laps", [])
    
    if not laps:
        return {"error": "No laps found"}
    
    # Extract lap times
    lap_numbers = [l["lap_number"] for l in laps]
    lap_times = [l["lap_time"] for l in laps]
    valid_flags = [l.get("valid", True) for l in laps]
    
    # Find best lap
    valid_times = [(n, t) for n, t, v in zip(lap_numbers, lap_times, valid_flags) if v and 60 < t < 180]
    if valid_times:
        best_lap_num, best_time = min(valid_times, key=lambda x: x[1])
    else:
        best_lap_num, best_time = None, None
    
    # Calculate statistics for valid laps only
    valid_lap_times = [t for t, v in zip(lap_times, valid_flags) if v and 60 < t < 180]
    if valid_lap_times:
        avg_time = np.mean(valid_lap_times)
        theoretical = session_data["summary"].get("theoretical_optimal")
    else:
        avg_time = None
        theoretical = None
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Format times as MM:SS.mmm for y-axis
    def format_time(t):
        return f"{int(t // 60)}:{t % 60:06.3f}"
    
    # Plot lap times
    colors = []
    for i, (n, t, v) in enumerate(zip(lap_numbers, lap_times, valid_flags)):
        if not v or t < 60 or t > 180:
            colors.append('lightgray')  # Invalid/outlap
        elif best_time and t == best_time:
            colors.append('green')  # Best lap
        elif best_time and t < best_time * 1.02:
            colors.append('limegreen')  # Within 2% of best
        elif best_time and t < best_time * 1.05:
            colors.append('gold')  # Within 5% of best
        else:
            colors.append('tomato')  # Slow lap
    
    bars = ax.bar(lap_numbers, lap_times, color=colors, edgecolor='black', linewidth=0.5)
    
    # Add lap time labels on bars
    for bar, t, v in zip(bars, lap_times, valid_flags):
        if v and 60 < t < 180:
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
                   format_time(t), ha='center', va='bottom', fontsize=8, rotation=45)
    
    # Reference lines
    if best_time:
        ax.axhline(y=best_time, color='green', linestyle='--', linewidth=1.5, 
                  label=f'Best: {format_time(best_time)}')
    
    if avg_time:
        ax.axhline(y=avg_time, color='blue', linestyle=':', linewidth=1.5,
                  label=f'Average: {format_time(avg_time)}')
    
    if theoretical:
        ax.axhline(y=theoretical, color='purple', linestyle='-.', linewidth=1.5,
                  label=f'Optimal: {format_time(theoretical)}')
    
    # Styling
    ax.set_xlabel('Lap Number', fontsize=11)
    ax.set_ylabel('Lap Time (seconds)', fontsize=11)
    ax.set_xticks(lap_numbers)
    
    # Set y-axis limits with padding
    valid_min = min(t for t in lap_times if 60 < t < 180) if any(60 < t < 180 for t in lap_times) else 90
    valid_max = max(t for t in lap_times if 60 < t < 180) if any(60 < t < 180 for t in lap_times) else 120
    y_padding = (valid_max - valid_min) * 0.15
    ax.set_ylim(valid_min - y_padding, valid_max + y_padding * 2)
    
    # Title
    track_name = session_data["metadata"].get("track", "Unknown Track")
    total_laps = len(laps)
    ax.set_title(f"Lap Time Evolution\n{track_name} | {total_laps} Laps",
                fontsize=12, fontweight='bold')
    
    # Legend
    ax.legend(loc='upper right', fontsize=9)
    
    # Grid
    ax.grid(axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Add trend line for valid laps
    if len(valid_lap_times) >= 3:
        valid_indices = [i+1 for i, (t, v) in enumerate(zip(lap_times, valid_flags)) if v and 60 < t < 180]
        z = np.polyfit(valid_indices, valid_lap_times, 1)
        p = np.poly1d(z)
        trend_x = np.linspace(min(valid_indices), max(valid_indices), 100)
        ax.plot(trend_x, p(trend_x), 'r-', alpha=0.5, linewidth=2, label='Trend')
        
        # Determine trend direction
        slope = z[0]
        if slope < -0.1:
            trend_text = "IMPROVING ▲"
            trend_color = 'green'
        elif slope > 0.1:
            trend_text = "DEGRADING ▼"
            trend_color = 'red'
        else:
            trend_text = "STABLE ─"
            trend_color = 'blue'
        
        ax.text(0.02, 0.98, trend_text, transform=ax.transAxes, fontsize=10,
               verticalalignment='top', fontweight='bold', color=trend_color,
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    plt.tight_layout()
    
    # Save or show
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        return {"success": True, "file": output_path}
    elif show:
        plt.show()
        return {"success": True, "displayed": True}
    else:
        default_path = Path(ibt_path).stem + "_lap_evolution.png"
        plt.savefig(default_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        return {"success": True, "file": default_path}


def main():
    parser = argparse.ArgumentParser(description="Generate lap time evolution chart")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, help="Track ID (optional)")
    parser.add_argument("--output", "-o", type=str, help="Output PNG path")
    parser.add_argument("--show", action="store_true", help="Show plot interactively")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = generate_lap_evolution_chart(
        ibt_path,
        args.track,
        args.output,
        args.show
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

