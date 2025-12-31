#!/usr/bin/env python3
"""
Tool: Deviation from Reference Line Visualization

Shows the REFERENCE (alien) line colored by how much YOU deviate from it.
Uses a non-linear color scale where small deviations are fine, but large ones are alarming.

Scale:
- 0-10cm: Green (fine)
- 10-50cm: Yellow (getting off)
- 50cm-1m: Orange (too far)
- 1m-2m+: Red (what are you doing?!)

Usage:
    python tools/coach/visualize_deviation_from_reference.py <your_lap.csv> <reference_lap.csv> <boundaries.json> <output_dir> [track_id] [--dark] [--session-id SESSION_ID]

Examples:
    # Without session ID (uses generic names)
    python tools/coach/visualize_deviation_from_reference.py lap.csv ref.csv bounds.json output/ track-id

    # With session ID (prefixes all output files)
    python tools/coach/visualize_deviation_from_reference.py lap.csv ref.csv bounds.json output/ track-id --session-id 2025-12-31-13-58
    # Creates: output/2025-12-31-13-58-deviation-s01.png, etc.
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.collections import LineCollection
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
    """Load telemetry CSV file."""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def load_boundaries(filepath):
    """Load track boundary data."""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading boundaries: {e}")
        return None


def interpolate_to_common_distance(df, num_points=3000):
    """Interpolate telemetry to common distance points."""
    if df is None or len(df) == 0:
        return None
    
    df = df.copy()
    
    if 'LapDistPct' in df.columns and len(df) > 1:
        # Find wrap-around
        wrap_idx = None
        for i in range(len(df) - 1):
            if df['LapDistPct'].iloc[i+1] < df['LapDistPct'].iloc[i]:
                wrap_idx = i + 1
                break
        
        if wrap_idx is not None:
            wrapped_rows = df.iloc[wrap_idx:].copy()
            non_wrapped_rows = df.iloc[:wrap_idx].copy()
            wrapped_rows['LapDistPct'] = wrapped_rows['LapDistPct'] + 1.0
            df = pd.concat([non_wrapped_rows, wrapped_rows], ignore_index=True)
    
    df = df.drop_duplicates(subset=['LapDistPct'], keep='first')
    df = df.sort_values('LapDistPct').reset_index(drop=True)
    
    dist_new = np.linspace(0, 1, num_points)
    
    result = {'LapDistPct': dist_new}
    
    for col in ['Lat', 'Lon', 'Speed']:
        if col in df.columns:
            try:
                f = interp1d(df['LapDistPct'].values, df[col].values, 
                           kind='linear', fill_value='extrapolate')
                result[col] = f(dist_new)
            except:
                pass
    
    return pd.DataFrame(result)


def calculate_track_width_usage(lap_df, boundaries):
    """Calculate normalized track width usage (0=inner, 1=outer)."""
    lap_lat = lap_df['Lat'].values
    lap_lon = lap_df['Lon'].values
    
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    inner_lat = np.array([p['lat'] for p in inner_bounds])
    inner_lon = np.array([p['lon'] for p in inner_bounds])
    outer_lat = np.array([p['lat'] for p in outer_bounds])
    outer_lon = np.array([p['lon'] for p in outer_bounds])
    
    usage = []
    
    for i, (y, x) in enumerate(zip(lap_lat, lap_lon)):
        inner_y, inner_x = inner_lat[i], inner_lon[i]
        outer_y, outer_x = outer_lat[i], outer_lon[i]
        
        vec_inner_outer_lat = outer_y - inner_y
        vec_inner_outer_lon = outer_x - inner_x
        vec_inner_current_lat = y - inner_y
        vec_inner_current_lon = x - inner_x
        
        dot = (vec_inner_current_lat * vec_inner_outer_lat +
               vec_inner_current_lon * vec_inner_outer_lon)
        denom = vec_inner_outer_lat**2 + vec_inner_outer_lon**2
        
        if denom > 0:
            ratio = dot / denom
        else:
            ratio = 0.5
        
        usage.append(ratio)
    
    usage = np.clip(usage, 0, 1)
    return np.array(usage)


def compute_track_width_meters(boundaries):
    """Compute physical track width (meters) at each distance_pct."""
    inner_lat = np.array([p['lat'] for p in boundaries['inner_boundary']])
    inner_lon = np.array([p['lon'] for p in boundaries['inner_boundary']])
    outer_lat = np.array([p['lat'] for p in boundaries['outer_boundary']])
    outer_lon = np.array([p['lon'] for p in boundaries['outer_boundary']])
    
    widths = []
    for ilat, ilon, olat, olon in zip(inner_lat, inner_lon, outer_lat, outer_lon):
        dlat = olat - ilat
        dlon = olon - ilon
        lat_m = dlat * 111000
        lon_m = dlon * 111000 * np.cos(np.radians((ilat + olat) / 2))
        widths.append(np.sqrt(lat_m**2 + lon_m**2))
    
    return np.array(widths)


def create_deviation_colormap():
    """
    Create a non-linear colormap for deviation visualization (relative usage diff).
    
    Scale (as % of track width):
    - 0-5%: Green (fine)
    - 5-15%: Yellow (starting to drift)
    - 15-30%: Orange (needs correction)
    - >30%: Red (off line)
    """
    colors = [
        (0.00, '#00b050'),
        (0.12, '#38c172'),
        (0.24, '#7fba00'),
        (0.36, '#c4d600'),
        (0.48, '#ffe600'),
        (0.64, '#ffb000'),
        (0.78, '#ff7b00'),
        (0.92, '#f44336'),
        (1.00, '#b71c1c'),
    ]
    
    # positions expressed relative to 1m (0-1)
    positions = [min(c[0], 1.0) for c in colors]
    color_list = [c[1] for c in colors]
    
    return mcolors.LinearSegmentedColormap.from_list('deviation',
                                                     list(zip(positions, color_list)))


def get_sector_bounds(track_data, sector_num):
    """Get start/end percentages for a sector."""
    sectors = track_data.get('sector', [])
    if sector_num < 1 or sector_num > len(sectors):
        return 0, 1
    
    this_sector_end = sectors[sector_num - 1]['marker']
    
    if sector_num == 1:
        sector_start = 0.0
    else:
        sector_start = sectors[sector_num - 2]['marker']
    
    return sector_start, this_sector_end


def create_sector_deviation_visualization(your_df, ref_df, boundaries, output_dir,
                                        track_id=None, your_name="Your Lap",
                                        ref_name="Reference", dark_mode=False,
                                        session_id=None):
    """
    Create deviation visualizations for each sector.
    Shows reference line colored by YOUR deviation from it.
    """
    
    # Green color for your line
    user_color = '#7fba00'
    
    # Interpolate
    your_interp = interpolate_to_common_distance(your_df, num_points=3000)
    ref_interp = interpolate_to_common_distance(ref_df, num_points=3000)
    
    if your_interp is None or ref_interp is None:
        print("Error: Could not interpolate data")
        return None
    
    # Calculate relative usage differences and physical deviations
    your_usage = calculate_track_width_usage(your_interp, boundaries)
    ref_usage = calculate_track_width_usage(ref_interp, boundaries)
    relative_dev = np.abs(your_usage - ref_usage)
    
    track_widths_m = compute_track_width_meters(boundaries)
    abs_dev_m = relative_dev * track_widths_m
    raw_max = abs_dev_m.max()
    color_max_m = min(1.0, max(0.2, raw_max * 1.1))
    
    # Load track data
    track_data = None
    if track_id:
        try:
            track_data = load_track_data(track_id)
        except:
            pass
    
    if not track_data:
        print("No track data - cannot determine sectors")
        return None
    
    # Color scheme
    if dark_mode:
        bg_color = '#1a1a2e'
        panel_color = '#16213e'
        text_color = 'white'
        grid_color = 'white'
    else:
        bg_color = '#fafafa'
        panel_color = '#ffffff'
        text_color = '#1a1a2e'
        grid_color = '#aaaaaa'
    
    boundary_color = '#cccccc' if not dark_mode else '#666666'
    
    # Extract boundaries
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    inner_lat = np.array([p['lat'] for p in inner_bounds])
    inner_lon = np.array([p['lon'] for p in inner_bounds])
    outer_lat = np.array([p['lat'] for p in outer_bounds])
    outer_lon = np.array([p['lon'] for p in outer_bounds])
    
    ref_lat = ref_interp['Lat'].values
    ref_lon = ref_interp['Lon'].values
    your_lat_vals = your_interp['Lat'].values
    your_lon_vals = your_interp['Lon'].values
    
    # Custom colormap
    cmap = create_deviation_colormap()
    
    # Create visualizations
    sectors = track_data.get('sector', [])
    
    for sector_num in range(1, len(sectors) + 1):
        sector_start, sector_end = get_sector_bounds(track_data, sector_num)
        
        # Filter to sector
        ref_mask = (ref_interp['LapDistPct'] >= sector_start) & \
                  (ref_interp['LapDistPct'] <= sector_end)
        your_mask = (your_interp['LapDistPct'] >= sector_start) & \
                   (your_interp['LapDistPct'] <= sector_end)
        
        inner_mask = (np.array([p['distance_pct'] for p in inner_bounds]) >= sector_start) & \
                    (np.array([p['distance_pct'] for p in inner_bounds]) <= sector_end)
        outer_mask = (np.array([p['distance_pct'] for p in outer_bounds]) >= sector_start) & \
                    (np.array([p['distance_pct'] for p in outer_bounds]) <= sector_end)
        
        ref_sector_lat = ref_lat[ref_mask]
        ref_sector_lon = ref_lon[ref_mask]
        your_sector_lat = your_lat_vals[your_mask]
        your_sector_lon = your_lon_vals[your_mask]
        sector_rel_dev = relative_dev[ref_mask]
        sector_abs_dev = abs_dev_m[ref_mask]
        sector_abs_clipped = np.clip(sector_abs_dev, 0, color_max_m)
        
        inner_sector_lat = inner_lat[inner_mask]
        inner_sector_lon = inner_lon[inner_mask]
        outer_sector_lat = outer_lat[outer_mask]
        outer_sector_lon = outer_lon[outer_mask]
        
        if len(ref_sector_lat) == 0:
            continue
        
        # Create figure (wider aspect for horizontal colorbar)
        fig, ax = plt.subplots(figsize=(12, 9))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(panel_color)
        
        # Plot boundaries (thin grey)
        ax.plot(inner_sector_lon, inner_sector_lat, color=boundary_color, 
               linewidth=0.8, alpha=0.4, zorder=2)
        ax.plot(outer_sector_lon, outer_sector_lat, color=boundary_color,
               linewidth=0.8, alpha=0.4, zorder=2)
        
        # Plot reference line colored by your deviation from it using variable line width
        points = np.array([ref_sector_lon, ref_sector_lat]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        segment_values = sector_abs_clipped[:-1]
        line_widths = 1.2 + (segment_values / color_max_m) * 1.8
        lc = LineCollection(segments, cmap=cmap, norm=plt.Normalize(0, color_max_m),
                            array=segment_values, linewidths=line_widths, zorder=3)
        ax.add_collection(lc)
        
        # Overlay YOUR actual line in white on top
        ax.plot(your_sector_lon, your_sector_lat, color=user_color, linewidth=0.7, alpha=1, zorder=4)
        
        # Custom horizontal colorbar underneath the plot (full width)
        cbar = plt.colorbar(lc, ax=ax, orientation='horizontal', location='bottom',
                           pad=0.08, aspect=40, shrink=1.0)
        cbar.set_label('Deviation from Reference (cm)', color=text_color, fontsize=10)
        cbar.ax.xaxis.label.set_color(text_color)
        cbar.ax.tick_params(colors=text_color, labelsize=9)
        
        tick_values = np.linspace(0, color_max_m, 6)
        cbar.set_ticks(tick_values)
        cbar.set_ticklabels([f"{v*100:.0f}" for v in tick_values])
        
        # Clean up axes (remove lat/lon labels - not useful for this viz)
        ax.set_xlabel('')
        ax.set_ylabel('')
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        
        sector_name = sectors[sector_num - 1].get('name', f"Sector {sector_num}")
        ax.set_title(f'Sector {sector_num} - Your Deviation from {ref_name}\'s Line',
                    fontsize=12, fontweight='bold', color=text_color, pad=10)
        
        ax.tick_params(colors=text_color, length=0)
        ax.set_aspect('equal')
        ax.grid(False)
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Calculate stats for this sector
        avg_abs_cm = np.mean(sector_abs_dev) * 100
        max_abs_cm = np.max(sector_abs_dev) * 100
        avg_rel_pct = np.mean(sector_rel_dev) * 100
        
        fine_pct = (sector_abs_dev <= 0.15).sum() / len(sector_abs_dev) * 100
        warning_pct = ((sector_abs_dev > 0.15) & (sector_abs_dev <= 0.40)).sum() / len(sector_abs_dev) * 100
        bad_pct = ((sector_abs_dev > 0.40) & (sector_abs_dev <= 0.70)).sum() / len(sector_abs_dev) * 100
        terrible_pct = (sector_abs_dev > 0.70).sum() / len(sector_abs_dev) * 100
        
        stats_text = f"""Deviation Stats:
Avg: {avg_abs_cm:.0f} cm | Max: {max_abs_cm:.0f} cm
Avg Δ (width): {avg_rel_pct:.1f}%
"""
        
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=9, color=text_color, family='monospace',
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor=panel_color, alpha=0.9, edgecolor=grid_color))
        
        plt.tight_layout()
        
        # Save with session ID prefix if provided
        if session_id:
            filename = f"{session_id}-deviation-s{sector_num:02d}.png"
        else:
            filename = f"sector-{sector_num:02d}-deviation.png"
        output_file = Path(output_dir) / filename
        plt.savefig(output_file, dpi=200, facecolor=fig.get_facecolor(),
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"✓ {output_file}")
    
    return True


def main():
    if len(sys.argv) < 5:
        print(json.dumps({
            "error": "Usage: python visualize_deviation_from_reference.py <your_lap.csv> <reference_lap.csv> <boundaries.json> <output_dir> [track_id] [--dark] [--session-id ID]"
        }))
        sys.exit(1)
    
    dark_mode = '--dark' in sys.argv
    
    # Parse --session-id argument
    session_id = None
    args = []
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--session-id' and i + 1 < len(sys.argv):
            session_id = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--dark':
            i += 1
        else:
            args.append(sys.argv[i])
            i += 1
    
    your_file = Path(args[0])
    ref_file = Path(args[1])
    boundaries_file = Path(args[2])
    output_dir = Path(args[3])
    track_id = args[4] if len(args) > 4 else None
    
    for fpath in [your_file, ref_file, boundaries_file]:
        if not fpath.exists():
            print(json.dumps({"error": f"File not found: {fpath}"}))
            sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    your_lap = load_telemetry(your_file)
    ref_lap = load_telemetry(ref_file)
    boundaries = load_boundaries(boundaries_file)
    
    if any(x is None for x in [your_lap, ref_lap, boundaries]):
        print(json.dumps({"error": "Failed to load data"}))
        sys.exit(1)
    
    your_name = your_file.stem.split(" - ")[1] if " - " in your_file.stem else "Your Lap"
    ref_name = ref_file.stem.split(" - ")[1] if " - " in ref_file.stem else "Reference"
    
    success = create_sector_deviation_visualization(
        your_lap, ref_lap, boundaries, output_dir,
        track_id=track_id,
        your_name=your_name,
        ref_name=ref_name,
        dark_mode=dark_mode,
        session_id=session_id
    )
    
    if success:
        print(f"\nDeviation visualizations saved to: {output_dir}")
        result = {"status": "success", "output_dir": str(output_dir)}
    else:
        result = {"status": "error", "message": "Failed to create visualizations"}
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
