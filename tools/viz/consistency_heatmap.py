#!/usr/bin/env python3
"""
Visualization Tool: Consistency Heatmap

Generates a heatmap showing corner times across all laps.
Green = close to best, Red = far from best.

Instantly reveals which corners are "dialed" vs "lottery".

Usage:
    python tools/viz/consistency_heatmap.py <telemetry.ibt> --track oschersleben-gp
    python tools/viz/consistency_heatmap.py <telemetry.ibt> --track oschersleben-gp -o heatmap.png

Output: PNG image
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

try:
    import matplotlib.pyplot as plt
    import matplotlib.colors as mcolors
    import numpy as np
except ImportError:
    print(json.dumps({"error": "matplotlib not installed. Run: uv add matplotlib"}))
    sys.exit(1)

# Import our session extractor
sys.path.insert(0, str(Path(__file__).parent.parent))
from core.extract_session_from_ibt import extract_session


def generate_consistency_heatmap(
    ibt_path: str,
    track_id: str,
    output_path: Optional[str] = None,
    show: bool = False
) -> dict:
    """
    Generate a heatmap of corner times across laps.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID for corner data
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
    valid_laps = [l for l in laps if l.get("valid", False) and "corners" in l]
    
    if not valid_laps:
        return {"error": "No valid laps with corner data found"}
    
    # Get corner names
    corner_names = list(valid_laps[0]["corners"].keys())
    
    # Build data matrix
    # Rows = laps, Columns = corners
    # Values = time difference from best time in that corner
    
    # Find best time per corner
    best_times = {}
    for corner in corner_names:
        times = [l["corners"].get(corner) for l in valid_laps if l["corners"].get(corner)]
        if times:
            best_times[corner] = min(times)
    
    # Build matrix of deltas (time - best)
    data = []
    lap_labels = []
    for lap in valid_laps:
        row = []
        for corner in corner_names:
            time = lap["corners"].get(corner)
            best = best_times.get(corner)
            if time and best:
                delta = time - best
                row.append(delta)
            else:
                row.append(0)
        data.append(row)
        lap_labels.append(f"L{lap['lap_number']}")
    
    data = np.array(data)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, max(4, len(valid_laps) * 0.8)))
    
    # Custom colormap: green (0) -> yellow -> red (max)
    max_delta = np.max(data)
    if max_delta < 0.5:
        max_delta = 0.5  # Minimum scale
    
    # Create heatmap
    im = ax.imshow(data, aspect='auto', cmap='RdYlGn_r', vmin=0, vmax=max_delta)
    
    # Labels
    ax.set_xticks(range(len(corner_names)))
    ax.set_xticklabels([c.replace(" ", "\n") for c in corner_names], fontsize=8, rotation=45, ha='right')
    
    ax.set_yticks(range(len(lap_labels)))
    ax.set_yticklabels(lap_labels, fontsize=10)
    
    # Add value annotations
    for i in range(len(lap_labels)):
        for j in range(len(corner_names)):
            value = data[i, j]
            text_color = 'white' if value > max_delta * 0.6 else 'black'
            if value > 0.05:
                ax.text(j, i, f"+{value:.2f}", ha='center', va='center', 
                       fontsize=7, color=text_color, fontweight='bold')
            else:
                ax.text(j, i, "✓", ha='center', va='center',
                       fontsize=10, color='darkgreen', fontweight='bold')
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Time Loss vs Best (seconds)', fontsize=10)
    
    # Title
    track_name = session_data["metadata"].get("track", "Unknown Track")
    best_lap = session_data["summary"]["best_lap_time_formatted"]
    ax.set_title(f"Corner Consistency Heatmap\n{track_name} | Best Lap: {best_lap}", 
                fontsize=12, fontweight='bold')
    
    ax.set_xlabel("Corner", fontsize=10)
    ax.set_ylabel("Lap", fontsize=10)
    
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
        # Default output path
        default_path = Path(ibt_path).stem + "_consistency_heatmap.png"
        plt.savefig(default_path, dpi=150, bbox_inches='tight',
                   facecolor='white', edgecolor='none')
        plt.close()
        return {"success": True, "file": default_path}


def main():
    parser = argparse.ArgumentParser(description="Generate corner consistency heatmap")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, required=True, help="Track ID")
    parser.add_argument("--output", "-o", type=str, help="Output PNG path")
    parser.add_argument("--show", action="store_true", help="Show plot interactively")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = generate_consistency_heatmap(
        ibt_path, 
        args.track, 
        args.output,
        args.show
    )
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

