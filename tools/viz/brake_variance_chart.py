#!/usr/bin/env python3
"""
Visualization Tool: Brake Point Variance Chart

Shows brake point consistency per corner as a horizontal bar chart.
Quickly identifies which corners have drifting brake points (need work)
vs locked-in brake points (consistent technique).

Usage:
    uv run python tools/viz/brake_variance_chart.py <brake.json> -o output.png
    uv run python tools/viz/brake_variance_chart.py <telemetry.ibt> --track oschersleben-gp -o output.png

Output: PNG bar chart showing σ (variance in meters) per corner
"""

import sys
import json
import argparse
from pathlib import Path

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def load_brake_data(source_path: str, track_id: str = None) -> dict:
    """
    Load brake data from JSON file or generate from IBT.
    """
    path = Path(source_path)
    
    if path.suffix == '.json':
        # Load pre-generated brake JSON
        with open(path) as f:
            return json.load(f)
    elif path.suffix == '.ibt':
        # Generate brake data from IBT
        if not track_id:
            return {"error": "Track ID required for IBT files (--track)"}
        
        # Import and run brake detection
        sys.path.insert(0, str(Path(__file__).parent.parent / "coach"))
        from detect_brake_point_drift import detect_brake_point_drift
        return detect_brake_point_drift(source_path, track_id)
    else:
        return {"error": f"Unsupported file type: {path.suffix}"}


def create_brake_variance_chart(brake_data: dict, output_path: str, title: str = None):
    """
    Create horizontal bar chart showing brake point variance per corner.
    """
    if not HAS_MATPLOTLIB:
        print(json.dumps({"error": "matplotlib not installed. Run: uv add matplotlib"}))
        return False
    
    if "error" in brake_data:
        print(json.dumps(brake_data))
        return False
    
    # Extract corner data
    corners = []
    for name, data in brake_data.get("corners", {}).items():
        consistency = data.get("consistency", {})
        sigma = consistency.get("sigma_meters")
        laps = consistency.get("laps_analyzed", 0)
        
        if sigma is not None and laps >= 2:
            corners.append({
                "name": name,
                "sigma": sigma,
                "laps": laps
            })
    
    if not corners:
        print(json.dumps({"error": "No brake point data found"}))
        return False
    
    # Sort by variance (highest first)
    corners.sort(key=lambda x: x["sigma"], reverse=True)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, max(6, len(corners) * 0.5)))
    
    # Data for plotting
    names = [c["name"] for c in corners]
    sigmas = [c["sigma"] for c in corners]
    
    # Color based on variance
    colors = []
    for s in sigmas:
        if s < 5:
            colors.append('#2ecc71')  # Green - locked
        elif s < 15:
            colors.append('#f39c12')  # Orange - solid
        else:
            colors.append('#e74c3c')  # Red - drifting
    
    # Create horizontal bars
    y_pos = range(len(names))
    bars = ax.barh(y_pos, sigmas, color=colors, edgecolor='white', linewidth=0.5)
    
    # Add value labels on bars
    for i, (bar, sigma) in enumerate(zip(bars, sigmas)):
        width = bar.get_width()
        label = f"{sigma:.1f}m"
        
        # Position label inside or outside bar depending on size
        if width > max(sigmas) * 0.3:
            ax.text(width - max(sigmas) * 0.02, bar.get_y() + bar.get_height()/2,
                   label, ha='right', va='center', color='white', fontweight='bold', fontsize=10)
        else:
            ax.text(width + max(sigmas) * 0.02, bar.get_y() + bar.get_height()/2,
                   label, ha='left', va='center', color='black', fontsize=10)
    
    # Customize axes
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names)
    ax.invert_yaxis()  # Highest variance at top
    ax.set_xlabel('Brake Point Variance (σ in meters)')
    
    # Add threshold lines
    ax.axvline(x=5, color='#2ecc71', linestyle='--', alpha=0.5, linewidth=2)
    ax.axvline(x=15, color='#f39c12', linestyle='--', alpha=0.5, linewidth=2)
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='#2ecc71', label='Locked (< 5m)'),
        mpatches.Patch(facecolor='#f39c12', label='Solid (5-15m)'),
        mpatches.Patch(facecolor='#e74c3c', label='Drifting (> 15m)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    
    # Title
    if title:
        ax.set_title(title, fontsize=14, fontweight='bold')
    else:
        track_name = brake_data.get("metadata", {}).get("track", "Unknown Track")
        ax.set_title(f"Brake Point Consistency\n{track_name}", fontsize=14, fontweight='bold')
    
    # Grid
    ax.grid(axis='x', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Create brake point variance chart")
    parser.add_argument("source", help="Path to brake.json or .ibt file")
    parser.add_argument("--track", type=str, help="Track ID (required for IBT files)")
    parser.add_argument("--output", "-o", type=str, required=True, help="Output PNG file")
    parser.add_argument("--title", type=str, help="Custom chart title")
    
    args = parser.parse_args()
    
    if not Path(args.source).exists():
        print(json.dumps({"error": f"File not found: {args.source}"}))
        sys.exit(1)
    
    # Load data
    brake_data = load_brake_data(args.source, args.track)
    
    # Create chart
    success = create_brake_variance_chart(brake_data, args.output, args.title)
    
    if success:
        print(json.dumps({"success": True, "file": args.output}))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
