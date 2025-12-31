#!/usr/bin/env python3
"""
Coach Tool: Racing Line Comparison Visualization

Compares GPS coordinates between two telemetry files to show:
1. Where the lines differ (track usage)
2. The lateral offset at each track position
3. Highlights corners where line differences are biggest

Usage:
    python tools/coach/visualize_racing_lines.py <your_lap.csv> <reference_lap.csv> [output.png]

Little Padawan reads the visual output and explains what it means.
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from scipy.interpolate import interp1d

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.core.track_data_loader import load_track_data
except ImportError:
    def load_track_data(track_id):
        return None


def load_telemetry(filepath):
    """Load telemetry CSV file with GPS coordinates."""
    try:
        df = pd.read_csv(filepath)
        # Check required columns
        required = ['Lat', 'Lon', 'LapDistPct']
        missing = [col for col in required if col not in df.columns]
        if missing:
            print(f"Warning: Missing columns {missing} in {filepath}")
            return None
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def interpolate_to_common_distance(df, num_points=2000):
    """
    Interpolate telemetry to common distance points.
    Returns dataframe with evenly spaced LapDistPct values.
    """
    if df is None or len(df) == 0:
        return None
    
    df = df.copy()
    
    # Remove wrap-around points
    if len(df) > 1 and df['LapDistPct'].iloc[-1] < df['LapDistPct'].iloc[-2]:
        df = df.iloc[:-1]
    
    # Sort by distance
    df = df.sort_values('LapDistPct').reset_index(drop=True)
    
    # Remove duplicate distance values (take first occurrence)
    df = df.drop_duplicates(subset=['LapDistPct'], keep='first')
    
    # Create target distance points
    dist_new = np.linspace(df['LapDistPct'].min(), df['LapDistPct'].max(), num_points)
    
    # Interpolate Lat, Lon, and Speed
    result = {'LapDistPct': dist_new}
    
    for col in ['Lat', 'Lon', 'Speed']:
        if col in df.columns:
            try:
                f = interp1d(df['LapDistPct'].values, df[col].values, 
                           kind='linear', fill_value='extrapolate')
                result[col] = f(dist_new)
            except Exception as e:
                print(f"Warning: Could not interpolate {col}: {e}")
    
    return pd.DataFrame(result)


def calculate_lateral_offset(current_df, reference_df):
    """
    Calculate lateral offset between two racing lines.
    
    Uses perpendicular distance from each point on current line
    to the nearest point on reference line.
    
    Returns: Array of offsets (positive = left of reference, negative = right)
    """
    offsets = []
    
    current_lat = current_df['Lat'].values
    current_lon = current_df['Lon'].values
    ref_lat = reference_df['Lat'].values
    ref_lon = reference_df['Lon'].values
    
    # For each point, find the closest reference point and calculate perpendicular distance
    for i in range(len(current_lat)):
        # Simple: just find the distance to the corresponding point (same LapDistPct)
        # This works because we've interpolated both to the same distance points
        dlat = current_lat[i] - ref_lat[i]
        dlon = current_lon[i] - ref_lon[i]
        
        # Convert to approximate meters (rough estimate, good enough for comparison)
        # 1 degree latitude ≈ 111km, 1 degree longitude varies by latitude
        lat_m = dlat * 111000
        lon_m = dlon * 111000 * np.cos(np.radians(current_lat[i]))
        
        # Total offset in meters
        offset = np.sqrt(lat_m**2 + lon_m**2)
        
        # Determine sign (left or right of reference line)
        # Using cross product to determine direction
        if i > 0 and i < len(current_lat) - 1:
            # Direction of reference line at this point
            ref_dx = ref_lon[i+1] - ref_lon[i-1]
            ref_dy = ref_lat[i+1] - ref_lat[i-1]
            
            # Vector from reference to current
            to_current_x = dlon
            to_current_y = dlat
            
            # Cross product to determine side
            cross = ref_dx * to_current_y - ref_dy * to_current_x
            if cross < 0:
                offset = -offset  # Right of reference line
        
        offsets.append(offset)
    
    return np.array(offsets)


def create_racing_line_visualization(current_df, reference_df, output_path, 
                                     track_id=None, current_name="Your Lap", 
                                     reference_name="Reference",
                                     dark_mode=False):
    """
    Create a visualization comparing two racing lines.
    
    Creates a figure with:
    1. Top-down view of both lines overlaid
    2. Lateral offset chart around the lap
    3. Speed comparison where lines differ most
    """
    # Interpolate both to common distance points
    current_interp = interpolate_to_common_distance(current_df)
    reference_interp = interpolate_to_common_distance(reference_df)
    
    if current_interp is None or reference_interp is None:
        print("Error: Could not interpolate data")
        return None
    
    # Calculate lateral offset
    offsets = calculate_lateral_offset(current_interp, reference_interp)
    
    # Load track data if available
    track_data = None
    if track_id:
        try:
            track_data = load_track_data(track_id)
        except:
            pass
    
    # Create figure with 3 subplots
    fig = plt.figure(figsize=(16, 12))
    
    # Color scheme based on mode
    if dark_mode:
        bg_color = '#1a1a2e'
        panel_color = '#16213e'
        text_color = 'white'
        ref_line_color = '#4cc9f0'
        grid_color = 'white'
    else:
        bg_color = '#fafafa'
        panel_color = '#ffffff'
        text_color = '#1a1a2e'
        ref_line_color = '#0077b6'
        grid_color = '#cccccc'
    
    fig.patch.set_facecolor(bg_color)
    
    # ==========================================
    # Subplot 1: Top-down racing line comparison
    # ==========================================
    ax1 = fig.add_subplot(2, 2, (1, 2))
    ax1.set_facecolor(panel_color)
    
    # Plot reference line (thicker, more transparent)
    ax1.plot(reference_interp['Lon'], reference_interp['Lat'], 
             color=ref_line_color, linewidth=4, alpha=0.5, label=reference_name,
             zorder=1)
    
    # Plot current line colored by offset
    # Create line segments for coloring
    points = np.array([current_interp['Lon'].values, 
                       current_interp['Lat'].values]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Color by offset magnitude
    offset_abs = np.abs(offsets[:-1])  # One less for segments
    
    # Create custom colormap (green = close, yellow = medium, red = far)
    colors = ['#00ff88', '#ffff00', '#ff6b6b']
    n_bins = 100
    cmap = LinearSegmentedColormap.from_list('offset', colors, N=n_bins)
    
    # Normalize offsets for coloring (max ~5 meters is very significant)
    norm = plt.Normalize(0, max(3.0, np.percentile(offset_abs, 95)))
    
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=2.5, zorder=2)
    lc.set_array(offset_abs)
    ax1.add_collection(lc)
    
    # Add colorbar
    cbar = plt.colorbar(lc, ax=ax1, label='Line Deviation (meters)', 
                        orientation='vertical', pad=0.02)
    cbar.ax.yaxis.label.set_color(text_color)
    cbar.ax.tick_params(colors=text_color)
    
    # Mark start/finish
    ax1.scatter(current_interp['Lon'].iloc[0], current_interp['Lat'].iloc[0],
                color='#00aa55' if not dark_mode else '#00ff88', 
                s=100, marker='s', zorder=5, label='Start/Finish')
    
    # Add corner labels if track data available
    if track_data:
        for turn in track_data.get('turn', []):
            mid_pct = (turn['start'] + turn['end']) / 2
            idx = int(mid_pct * len(current_interp))
            if 0 <= idx < len(current_interp):
                ax1.annotate(turn['name'], 
                            xy=(current_interp['Lon'].iloc[idx], 
                                current_interp['Lat'].iloc[idx]),
                            fontsize=8, color=text_color, alpha=0.8,
                            ha='center', va='bottom',
                            bbox=dict(boxstyle='round,pad=0.2', 
                                     facecolor=panel_color, alpha=0.8,
                                     edgecolor=grid_color))
    
    ax1.set_xlabel('Longitude', color=text_color)
    ax1.set_ylabel('Latitude', color=text_color)
    ax1.set_title('Racing Line Comparison (Top-Down View)', 
                  fontsize=14, fontweight='bold', color=text_color)
    ax1.tick_params(colors=text_color)
    ax1.legend(loc='upper right', facecolor=panel_color, edgecolor=grid_color, 
               labelcolor=text_color)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3, color=grid_color)
    for spine in ax1.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 2: Lateral offset around the lap
    # ==========================================
    ax2 = fig.add_subplot(2, 2, 3)
    ax2.set_facecolor(panel_color)
    
    distance_pct = current_interp['LapDistPct'].values * 100
    
    # Fill areas - adjust colors for light/dark mode
    left_color = '#0077b6' if not dark_mode else '#4cc9f0'
    right_color = '#e63946' if not dark_mode else '#ff6b6b'
    line_color = '#333333' if not dark_mode else 'white'
    zero_color = '#00aa55' if not dark_mode else '#00ff88'
    corner_color = '#ff9f1c' if not dark_mode else 'yellow'
    
    ax2.fill_between(distance_pct, 0, offsets, where=(offsets >= 0),
                     color=left_color, alpha=0.4, label='Left of reference')
    ax2.fill_between(distance_pct, 0, offsets, where=(offsets < 0),
                     color=right_color, alpha=0.4, label='Right of reference')
    
    # Plot line
    ax2.plot(distance_pct, offsets, color=line_color, linewidth=1.5, alpha=0.8)
    
    # Zero line
    ax2.axhline(y=0, color=zero_color, linestyle='--', linewidth=1, alpha=0.5)
    
    # Add corner markers if track data available
    if track_data:
        for turn in track_data.get('turn', []):
            mid_pct = (turn['start'] + turn['end']) / 2 * 100
            ax2.axvline(x=mid_pct, color=corner_color, linestyle=':', alpha=0.4)
            ax2.text(mid_pct, ax2.get_ylim()[1] * 0.9, turn['name'], 
                    rotation=90, fontsize=7, color=corner_color, alpha=0.8,
                    ha='right', va='top')
    
    ax2.set_xlabel('Lap Distance (%)', color=text_color)
    ax2.set_ylabel('Offset (meters)', color=text_color)
    ax2.set_title('Lateral Deviation from Reference Line', 
                  fontsize=12, fontweight='bold', color=text_color)
    ax2.tick_params(colors=text_color)
    ax2.legend(loc='upper right', facecolor=panel_color, edgecolor=grid_color,
               labelcolor=text_color, fontsize=8)
    ax2.grid(True, alpha=0.3, color=grid_color)
    ax2.set_xlim(0, 100)
    for spine in ax2.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 3: Statistics and insights
    # ==========================================
    ax3 = fig.add_subplot(2, 2, 4)
    ax3.set_facecolor(panel_color)
    ax3.axis('off')
    
    # Calculate statistics
    avg_offset = np.mean(np.abs(offsets))
    max_offset = np.max(np.abs(offsets))
    max_offset_pct = distance_pct[np.argmax(np.abs(offsets))]
    
    # Find biggest deviation zones
    threshold = np.percentile(np.abs(offsets), 75)
    big_deviation_zones = []
    in_zone = False
    zone_start = None
    
    for i, (pct, off) in enumerate(zip(distance_pct, np.abs(offsets))):
        if off > threshold and not in_zone:
            in_zone = True
            zone_start = pct
        elif off <= threshold and in_zone:
            in_zone = False
            big_deviation_zones.append((zone_start, pct))
    
    # Speed comparison at deviation zones
    speed_stats = ""
    if 'Speed' in current_interp.columns and 'Speed' in reference_interp.columns:
        speed_diff = current_interp['Speed'].values - reference_interp['Speed'].values
        avg_speed_diff = np.mean(speed_diff)
        speed_stats = f"""
Speed Comparison:
  Avg speed diff: {avg_speed_diff:+.1f} km/h
  Max faster: +{np.max(speed_diff):.1f} km/h
  Max slower: {np.min(speed_diff):.1f} km/h
"""
    
    # Corner name at max deviation
    max_corner = "Unknown"
    if track_data:
        max_off_dist = max_offset_pct / 100
        for turn in track_data.get('turn', []):
            if turn['start'] <= max_off_dist <= turn['end']:
                max_corner = turn['name']
                break
        for straight in track_data.get('straight', []):
            if straight['start'] <= max_off_dist <= straight['end']:
                max_corner = straight['name']
                break
    
    stats_text = f"""
╔══════════════════════════════════════╗
║        LINE DEVIATION ANALYSIS       ║
╠══════════════════════════════════════╣
║                                      ║
║  Average Offset: {avg_offset:.2f} m              
║  Maximum Offset: {max_offset:.2f} m              
║  Max at: {max_offset_pct:.1f}% ({max_corner})      
║                                      ║
║  Zones with big deviation (>75th %): 
║  {len(big_deviation_zones)} zones identified            
║                                      ║
{speed_stats}║                                      ║
╚══════════════════════════════════════╝

Legend:
[CYAN]  = {reference_name}
[GREEN] = Close to reference (good)
[YELLOW]= Medium deviation
[RED]   = Large deviation (investigate!)

Key Insight: 
Large deviations aren't always bad—
sometimes you NEED to use more track!
Compare with SPEED to see if deviation
helps or hurts.
"""
    
    ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes,
             fontsize=10, color=text_color, family='monospace',
             verticalalignment='top')
    
    plt.tight_layout()
    
    # Save figure
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"Visualization saved to: {output_path}")
    
    # Return analysis summary as JSON
    summary = {
        "avg_offset_m": round(avg_offset, 2),
        "max_offset_m": round(max_offset, 2),
        "max_offset_location_pct": round(max_offset_pct, 1),
        "max_offset_corner": max_corner,
        "big_deviation_zones": len(big_deviation_zones),
        "zones": [{"start_pct": z[0], "end_pct": z[1]} for z in big_deviation_zones[:5]]
    }
    
    return summary


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python visualize_racing_lines.py <your_lap.csv> <reference_lap.csv> [output.png] [track_id] [--dark]"
        }))
        sys.exit(1)
    
    # Check for --dark flag anywhere in args
    dark_mode = '--dark' in sys.argv
    args = [a for a in sys.argv if a != '--dark']
    
    current_file = Path(args[1])
    reference_file = Path(args[2])
    output_path = args[3] if len(args) > 3 else "racing_line_comparison.png"
    track_id = args[4] if len(args) > 4 else None
    
    if not current_file.exists():
        print(json.dumps({"error": f"Current lap file not found: {current_file}"}))
        sys.exit(1)
    
    if not reference_file.exists():
        print(json.dumps({"error": f"Reference lap file not found: {reference_file}"}))
        sys.exit(1)
    
    # Extract names from filenames
    current_name = "Your Lap"
    reference_name = "Reference"
    
    # Try to extract driver name from Garage 61 filename format
    ref_filename = reference_file.stem
    if " - " in ref_filename:
        parts = ref_filename.split(" - ")
        if len(parts) >= 2:
            reference_name = parts[1]  # Driver name is usually second
    
    # Load telemetry
    current_df = load_telemetry(current_file)
    reference_df = load_telemetry(reference_file)
    
    if current_df is None or reference_df is None:
        print(json.dumps({"error": "Could not load telemetry files"}))
        sys.exit(1)
    
    # Create visualization
    summary = create_racing_line_visualization(
        current_df, reference_df, output_path,
        track_id=track_id,
        current_name=current_name,
        reference_name=reference_name,
        dark_mode=dark_mode
    )
    
    if summary:
        print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

