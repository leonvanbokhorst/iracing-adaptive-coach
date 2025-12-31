#!/usr/bin/env python3
"""
Tool: Sector-by-Sector Track Width Comparison

Creates one visualization per sector showing:
1. Track boundaries (grey)
2. Your line (colored by width usage)
3. Shuning's line (colored by width usage)
4. Clear visualization of differences

Usage:
    python tools/coach/visualize_sector_comparison.py <your_lap.csv> <reference_lap.csv> <boundaries.json> <output_dir> [track_id] [--dark]

Example:
    python tools/coach/visualize_sector_comparison.py \
        data/your_lap.csv \
        data/reference_lap.csv \
        tracks/track-data/limerock-2019-gp-boundaries.json \
        weeks/week04/assets/
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    
    # Sort by LapDistPct to handle wrap-around correctly
    if 'LapDistPct' in df.columns and len(df) > 1:
        # Find where it wraps (goes from high to low)
        wrap_idx = None
        for i in range(len(df) - 1):
            if df['LapDistPct'].iloc[i+1] < df['LapDistPct'].iloc[i]:
                wrap_idx = i + 1
                break
        
        # If there's a wrap, move the wrapped rows to the end (they're close to 0, append to 1.0)
        if wrap_idx is not None:
            wrapped_rows = df.iloc[wrap_idx:].copy()
            non_wrapped_rows = df.iloc[:wrap_idx].copy()
            # Shift wrapped rows to be after 1.0 (add 1.0 to their LapDistPct)
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
    """Calculate track width usage percentage at each point."""
    lap_lat = lap_df['Lat'].values
    lap_lon = lap_df['Lon'].values
    
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    inner_lat = np.array([p['lat'] for p in inner_bounds])
    inner_lon = np.array([p['lon'] for p in inner_bounds])
    outer_lat = np.array([p['lat'] for p in outer_bounds])
    outer_lon = np.array([p['lon'] for p in outer_bounds])
    
    usage_pct = []
    
    for i, (y, x) in enumerate(zip(lap_lat, lap_lon)):
        inner_y, inner_x = inner_lat[i], inner_lon[i]
        outer_y, outer_x = outer_lat[i], outer_lon[i]
        
        inner_to_outer_lat = outer_y - inner_y
        inner_to_outer_lon = outer_x - inner_x
        
        lap_from_inner_lat = y - inner_y
        lap_from_inner_lon = x - inner_x
        
        dot_product = (lap_from_inner_lat * inner_to_outer_lat + 
                      lap_from_inner_lon * inner_to_outer_lon)
        vector_length_sq = inner_to_outer_lat**2 + inner_to_outer_lon**2
        
        if vector_length_sq > 0:
            projection_ratio = dot_product / vector_length_sq
            usage = projection_ratio * 100
        else:
            usage = 50.0
        
        usage_pct.append(usage)
    
    return np.array(usage_pct)


def get_sector_bounds(track_data, sector_num):
    """Get start/end percentages for a sector.
    
    Note: Sector markers are END positions, not start!
    Sector 1 ends at marker[0], Sector 2 ends at marker[1], etc.
    """
    sectors = track_data.get('sector', [])
    if sector_num < 1 or sector_num > len(sectors):
        return 0, 1
    
    # Get this sector's end marker
    this_sector_end = sectors[sector_num - 1]['marker']
    
    # Get previous sector's end (which is this sector's start)
    if sector_num == 1:
        sector_start = 0.0
    else:
        sector_start = sectors[sector_num - 2]['marker']
    
    return sector_start, this_sector_end


def create_sector_comparison_visualization(your_lap_df, ref_lap_df, boundaries, 
                                          output_dir, track_id=None, 
                                          your_name="Your Lap", ref_name="Reference",
                                          dark_mode=False):
    """
    Create one visualization per sector comparing both lines.
    """
    # Interpolate
    your_interp = interpolate_to_common_distance(your_lap_df, num_points=3000)
    ref_interp = interpolate_to_common_distance(ref_lap_df, num_points=3000)
    
    if your_interp is None or ref_interp is None:
        print("Error: Could not interpolate data")
        return None
    
    # Calculate usage
    your_usage = calculate_track_width_usage(your_interp, boundaries)
    ref_usage = calculate_track_width_usage(ref_interp, boundaries)
    
    # Load track data for sector info
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
        grid_color = '#cccccc'
    
    boundary_color = '#999999' if not dark_mode else '#666666'
    
    # Extract boundaries
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    inner_lat = np.array([p['lat'] for p in inner_bounds])
    inner_lon = np.array([p['lon'] for p in inner_bounds])
    outer_lat = np.array([p['lat'] for p in outer_bounds])
    outer_lon = np.array([p['lon'] for p in outer_bounds])
    
    your_lat = your_interp['Lat'].values
    your_lon = your_interp['Lon'].values
    ref_lat = ref_interp['Lat'].values
    ref_lon = ref_interp['Lon'].values
    
    # Create visualizations for each sector
    sectors = track_data.get('sector', [])
    
    for sector_num in range(1, len(sectors) + 1):
        sector_start, sector_end = get_sector_bounds(track_data, sector_num)
        
        # Filter to sector
        your_mask = (your_interp['LapDistPct'] >= sector_start) & \
                   (your_interp['LapDistPct'] <= sector_end)
        ref_mask = (ref_interp['LapDistPct'] >= sector_start) & \
                  (ref_interp['LapDistPct'] <= sector_end)
        
        inner_mask = (np.array([p['distance_pct'] for p in inner_bounds]) >= sector_start) & \
                    (np.array([p['distance_pct'] for p in inner_bounds]) <= sector_end)
        outer_mask = (np.array([p['distance_pct'] for p in outer_bounds]) >= sector_start) & \
                    (np.array([p['distance_pct'] for p in outer_bounds]) <= sector_end)
        
        your_sector_lat = your_lat[your_mask]
        your_sector_lon = your_lon[your_mask]
        your_sector_usage = your_usage[your_mask]
        
        ref_sector_lat = ref_lat[ref_mask]
        ref_sector_lon = ref_lon[ref_mask]
        ref_sector_usage = ref_usage[ref_mask]
        
        inner_sector_lat = inner_lat[inner_mask]
        inner_sector_lon = inner_lon[inner_mask]
        outer_sector_lat = outer_lat[outer_mask]
        outer_sector_lon = outer_lon[outer_mask]
        
        if len(your_sector_lat) == 0 or len(ref_sector_lat) == 0:
            continue
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 10))
        fig.patch.set_facecolor(bg_color)
        ax.set_facecolor(panel_color)
        
        # Plot boundaries
        ax.plot(inner_sector_lon, inner_sector_lat, color=boundary_color, 
               linewidth=0.8, alpha=0.4, zorder=2)
        ax.plot(outer_sector_lon, outer_sector_lat, color=boundary_color,
               linewidth=0.8, alpha=0.4, zorder=2)
        
        # Plot reference lap (dashed, lighter)
        ax.scatter(ref_sector_lon, ref_sector_lat, c=ref_sector_usage, 
                  cmap='RdYlGn_r', s=8, alpha=0.5, vmin=-10, vmax=110,
                  zorder=3, label=f'{ref_name} (faded)')
        
        # Plot your lap (solid, darker)
        scatter = ax.scatter(your_sector_lon, your_sector_lat, c=your_sector_usage,
                            cmap='RdYlGn_r', s=15, alpha=0.9, vmin=-10, vmax=110,
                            zorder=4, label=your_name)
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax, label='Width Usage (%)')
        cbar.ax.yaxis.label.set_color(text_color)
        cbar.ax.tick_params(colors=text_color)
        
        # Labels
        ax.set_xlabel('Longitude', color=text_color)
        ax.set_ylabel('Latitude', color=text_color)
        
        sector_name = sectors[sector_num - 1]['name'] if 'name' in sectors[sector_num - 1] else f"Sector {sector_num}"
        ax.set_title(f'{sector_name} - Track Width Comparison (0%=Inner, 100%=Outer)',
                    fontsize=12, fontweight='bold', color=text_color)
        
        ax.tick_params(colors=text_color)
        ax.legend(loc='best', facecolor=panel_color, edgecolor=grid_color,
                 labelcolor=text_color, fontsize=10)
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.2, color=grid_color)
        for spine in ax.spines.values():
            spine.set_color(grid_color)
        
        # Calculate delta stats for this sector
        avg_your = np.mean(your_sector_usage)
        avg_ref = np.mean(ref_sector_usage)
        delta = avg_ref - avg_your
        
        # Add stats box
        stats_text = f"Avg Usage:\n{your_name}: {avg_your:.1f}%\n{ref_name}: {avg_ref:.1f}%\nDelta: {delta:+.1f}%"
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
               fontsize=10, color=text_color, family='monospace',
               verticalalignment='top', bbox=dict(boxstyle='round', 
               facecolor=panel_color, alpha=0.8, edgecolor=grid_color))
        
        plt.tight_layout()
        
        # Save
        output_file = Path(output_dir) / f"sector-{sector_num:02d}-comparison.png"
        plt.savefig(output_file, dpi=150, facecolor=fig.get_facecolor(),
                   edgecolor='none', bbox_inches='tight')
        plt.close()
        
        print(f"✓ {output_file}")
    
    return True


def main():
    if len(sys.argv) < 5:
        print(json.dumps({
            "error": "Usage: python visualize_sector_comparison.py <your_lap.csv> <reference_lap.csv> <boundaries.json> <output_dir> [track_id] [--dark]"
        }))
        sys.exit(1)
    
    dark_mode = '--dark' in sys.argv
    args = [a for a in sys.argv if a != '--dark']
    
    your_file = Path(args[1])
    ref_file = Path(args[2])
    boundaries_file = Path(args[3])
    output_dir = Path(args[4])
    track_id = args[5] if len(args) > 5 else None
    
    # Verify files
    for fpath in [your_file, ref_file, boundaries_file]:
        if not fpath.exists():
            print(json.dumps({"error": f"File not found: {fpath}"}))
            sys.exit(1)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    your_lap = load_telemetry(your_file)
    ref_lap = load_telemetry(ref_file)
    boundaries = load_boundaries(boundaries_file)
    
    if any(x is None for x in [your_lap, ref_lap, boundaries]):
        print(json.dumps({"error": "Failed to load data"}))
        sys.exit(1)
    
    # Extract names
    your_name = your_file.stem.split(" - ")[1] if " - " in your_file.stem else "Your Lap"
    ref_name = ref_file.stem.split(" - ")[1] if " - " in ref_file.stem else "Reference"
    
    # Create visualizations
    success = create_sector_comparison_visualization(
        your_lap, ref_lap, boundaries, output_dir,
        track_id=track_id,
        your_name=your_name,
        ref_name=ref_name,
        dark_mode=dark_mode
    )
    
    if success:
        print(f"\nSector comparisons saved to: {output_dir}")
        result = {"status": "success", "output_dir": str(output_dir)}
    else:
        result = {"status": "error", "message": "Failed to create visualizations"}
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

