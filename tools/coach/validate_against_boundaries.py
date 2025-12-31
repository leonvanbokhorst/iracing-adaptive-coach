#!/usr/bin/env python3
"""
Tool: Validate Lap Against Track Boundaries

Compares a lap to the aggregated track boundaries to show:
1. What % of available track width you're using
2. Where you could use more/less width
3. Specific zones where you're conservative vs aggressive

Usage:
    python tools/coach/validate_against_boundaries.py <your_lap.csv> <boundaries.json> [output.png] [--dark]

Example:
    python tools/coach/validate_against_boundaries.py \
        data/your_lap.csv \
        tracks/track-data/limerock-2019-gp-boundaries.json \
        output.png
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
    
    # Remove wrap-around points
    if 'LapDistPct' in df.columns and len(df) > 1:
        if df['LapDistPct'].iloc[-1] < df['LapDistPct'].iloc[-2]:
            df = df.iloc[:-1]
        df = df.sort_values('LapDistPct').reset_index(drop=True)
    
    df = df.drop_duplicates(subset=['LapDistPct'], keep='first')
    
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


def lat_lon_to_meters(lat, lon, ref_lat, ref_lon):
    """
    Convert lat/lon difference to approximate meters.
    Uses simplified Earth model.
    """
    lat_m = (lat - ref_lat) * 111000
    lon_m = (lon - ref_lon) * 111000 * np.cos(np.radians(ref_lat))
    return lat_m, lon_m


def calculate_track_width_usage(lap_df, boundaries):
    """
    Calculate what % of track width is being used at each point.
    
    Returns:
        Array of percentages (0-100%)
        0% = on inner boundary
        100% = on outer boundary
        >100% = outside outer boundary (aggressive!)
        <0% = inside inner boundary (defensive!)
    """
    lap_lat = lap_df['Lat'].values
    lap_lon = lap_df['Lon'].values
    
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    # Extract coordinates
    inner_lat = np.array([p['lat'] for p in inner_bounds])
    inner_lon = np.array([p['lon'] for p in inner_bounds])
    outer_lat = np.array([p['lat'] for p in outer_bounds])
    outer_lon = np.array([p['lon'] for p in outer_bounds])
    
    usage_pct = []
    
    for i, (y, x) in enumerate(zip(lap_lat, lap_lon)):
        # Get corresponding boundary points
        inner_y, inner_x = inner_lat[i], inner_lon[i]
        outer_y, outer_x = outer_lat[i], outer_lon[i]
        
        # Calculate distances in meters
        dist_to_inner_m, _ = lat_lon_to_meters(y, x, inner_y, inner_x)
        dist_to_inner = np.sqrt((y - inner_y)**2 + (x - inner_x)**2) * 111000
        
        dist_to_outer = np.sqrt((y - outer_y)**2 + (x - outer_x)**2) * 111000
        
        # Track width available
        track_width = np.sqrt((outer_y - inner_y)**2 + (outer_x - inner_x)**2) * 111000
        
        # Lateral distance from inner (positive = toward outer)
        # Simple approximation: use perpendicular component
        inner_to_outer_lat = outer_y - inner_y
        inner_to_outer_lon = outer_x - inner_x
        
        lap_from_inner_lat = y - inner_y
        lap_from_inner_lon = x - inner_x
        
        # Project lap position onto inner->outer vector
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


def create_validation_visualization(lap_df, boundaries, output_path, 
                                    track_id=None, lap_name="Your Lap", 
                                    dark_mode=False):
    """
    Create visualization showing track width usage.
    """
    # Interpolate lap to match boundaries
    lap_interp = interpolate_to_common_distance(lap_df, num_points=3000)
    
    if lap_interp is None:
        print("Error: Could not interpolate lap data")
        return None
    
    # Calculate usage
    usage_pct = calculate_track_width_usage(lap_interp, boundaries)
    
    # Load track data if available
    track_data = None
    if track_id:
        try:
            track_data = load_track_data(track_id)
        except:
            pass
    
    # Color scheme
    if dark_mode:
        bg_color = '#1a1a2e'
        panel_color = '#16213e'
        text_color = 'white'
        inner_color = '#4cc9f0'
        outer_color = '#ff6b6b'
        grid_color = 'white'
    else:
        bg_color = '#fafafa'
        panel_color = '#ffffff'
        text_color = '#1a1a2e'
        inner_color = '#0077b6'
        outer_color = '#e63946'
        grid_color = '#cccccc'
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor(bg_color)
    
    # ==========================================
    # Subplot 1: Track with boundaries and lap
    # ==========================================
    ax1 = fig.add_subplot(2, 2, (1, 2))
    ax1.set_facecolor(panel_color)
    
    # Extract boundary coordinates
    inner_bounds = boundaries['inner_boundary']
    outer_bounds = boundaries['outer_boundary']
    
    inner_lat = [p['lat'] for p in inner_bounds]
    inner_lon = [p['lon'] for p in inner_bounds]
    outer_lat = [p['lat'] for p in outer_bounds]
    outer_lon = [p['lon'] for p in outer_bounds]
    
    # Plot boundaries - subtle grey
    boundary_color = '#999999' if not dark_mode else '#666666'
    ax1.plot(inner_lon, inner_lat, color=boundary_color, linewidth=0.8, 
             alpha=0.4, zorder=2)
    ax1.plot(outer_lon, outer_lat, color=boundary_color, linewidth=0.8,
             alpha=0.4, zorder=2)
    
    # Plot lap colored by usage
    lap_lat = lap_interp['Lat'].values
    lap_lon = lap_interp['Lon'].values
    
    # Color points by usage: 0-50% = blue (inner), 50-100% = green (outer), >100% = red (aggressive)
    colors = []
    for u in usage_pct:
        if u < 0:
            colors.append('#4cc9f0')  # Cyan (defensive)
        elif u < 25:
            colors.append('#0077b6')  # Dark blue (inner half)
        elif u < 50:
            colors.append('#2a9d8f')  # Teal (inner quarter)
        elif u < 75:
            colors.append('#e9c46a')  # Yellow (outer quarter)
        elif u < 100:
            colors.append('#f4a261')  # Orange (outer half)
        else:
            colors.append('#e63946')  # Red (aggressive!)
    
    # Plot lap as scatter for color coding
    scatter = ax1.scatter(lap_lon, lap_lat, c=usage_pct, cmap='RdYlGn_r', 
                         s=2, alpha=0.8, vmin=-10, vmax=110, zorder=3)
    
    # Add colorbar
    cbar = plt.colorbar(scatter, ax=ax1, label='Track Width Usage (%)')
    cbar.ax.yaxis.label.set_color(text_color)
    cbar.ax.tick_params(colors=text_color)
    
    ax1.set_xlabel('Longitude', color=text_color)
    ax1.set_ylabel('Latitude', color=text_color)
    ax1.set_title(f'{lap_name} - Track Width Usage (0%=Inner, 100%=Outer)',
                  fontsize=12, fontweight='bold', color=text_color)
    ax1.tick_params(colors=text_color)
    # Remove legend since boundaries are subtle now
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3, color=grid_color)
    for spine in ax1.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 2: Usage percentage over lap
    # ==========================================
    ax2 = fig.add_subplot(2, 2, 3)
    ax2.set_facecolor(panel_color)
    
    distance_pct = lap_interp['LapDistPct'].values * 100
    
    # Fill zones
    ax2.fill_between(distance_pct, 0, usage_pct, where=(usage_pct >= 0) & (usage_pct <= 100),
                     color='#2a9d8f', alpha=0.5, label='Within boundaries')
    ax2.fill_between(distance_pct, 0, usage_pct, where=(usage_pct > 100),
                     color='#e63946', alpha=0.5, label='Outside boundary (aggressive!)')
    ax2.fill_between(distance_pct, 0, usage_pct, where=(usage_pct < 0),
                     color='#4cc9f0', alpha=0.5, label='Inside boundary (conservative)')
    
    # Plot line
    ax2.plot(distance_pct, usage_pct, color=text_color, linewidth=1.5, alpha=0.8)
    
    # Reference lines
    ax2.axhline(y=0, color=inner_color, linestyle='--', linewidth=1, alpha=0.5, label='Inner')
    ax2.axhline(y=100, color=outer_color, linestyle='--', linewidth=1, alpha=0.5, label='Outer')
    ax2.axhline(y=50, color='gray', linestyle=':', linewidth=1, alpha=0.3, label='Midpoint')
    
    # Add corner markers if track data available
    if track_data:
        for turn in track_data.get('turn', []):
            mid_pct = (turn['start'] + turn['end']) / 2 * 100
            ax2.axvline(x=mid_pct, color='gold', linestyle=':', alpha=0.3)
    
    ax2.set_xlabel('Lap Distance (%)', color=text_color)
    ax2.set_ylabel('Track Width Usage (%)', color=text_color)
    ax2.set_title('Width Usage Over Lap (Green=Good, Yellow=Aggressive, Red=Max)',
                  fontsize=12, fontweight='bold', color=text_color)
    ax2.tick_params(colors=text_color)
    ax2.legend(loc='best', facecolor=panel_color, edgecolor=grid_color,
               labelcolor=text_color, fontsize=8)
    ax2.grid(True, alpha=0.3, color=grid_color)
    ax2.set_xlim(0, 100)
    ax2.set_ylim(-20, 120)
    for spine in ax2.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 3: Statistics
    # ==========================================
    ax3 = fig.add_subplot(2, 2, 4)
    ax3.set_facecolor(panel_color)
    ax3.axis('off')
    
    # Calculate statistics
    avg_usage = np.mean(usage_pct[(usage_pct >= 0) & (usage_pct <= 100)])
    max_usage = np.max(usage_pct)
    min_usage = np.min(usage_pct)
    
    aggressive_zones = (usage_pct > 100).sum()
    defensive_zones = (usage_pct < 0).sum()
    aggressive_pct = (aggressive_zones / len(usage_pct)) * 100
    defensive_pct = (defensive_zones / len(usage_pct)) * 100
    
    # Find biggest aggressive zones
    big_aggressive = usage_pct > 105
    aggressive_peaks = []
    in_zone = False
    zone_start = None
    zone_max = 0
    
    for i, is_agg in enumerate(big_aggressive):
        if is_agg and not in_zone:
            in_zone = True
            zone_start = i
            zone_max = usage_pct[i]
        elif is_agg and in_zone:
            zone_max = max(zone_max, usage_pct[i])
        elif not is_agg and in_zone:
            in_zone = False
            aggressive_peaks.append({
                'start_pct': float(distance_pct[zone_start]),
                'max': float(zone_max),
                'max_pct': float(distance_pct[np.argmax(usage_pct[zone_start:i])])
            })
    
    stats_text = f"""
╔═══════════════════════════════════════════════╗
║         TRACK WIDTH USAGE ANALYSIS           ║
╠═══════════════════════════════════════════════╣

OVERALL STATISTICS:
  Average Usage:     {avg_usage:6.1f}%
  Maximum:           {max_usage:6.1f}%
  Minimum:           {min_usage:6.1f}%

ZONE BREAKDOWN:
  Aggressive (>100%):  {aggressive_pct:5.1f}% of lap
  Conservative (<0%):  {defensive_pct:5.1f}% of lap
  Within bounds:       {100-aggressive_pct-defensive_pct:5.1f}% of lap

TOP AGGRESSIVE ZONES (>105%):
"""
    
    for idx, zone in enumerate(aggressive_peaks[:3], 1):
        stats_text += f"  {idx}. {zone['max_pct']:.0f}% → Max {zone['max']:.1f}%\n"
    
    stats_text += f"""
╚═══════════════════════════════════════════════╝

INTERPRETATION:
  0-50%:   Using inner half of track
  50-100%: Using outer half of track
  >100%:   Going BEYOND outer boundary!
  <0%:     Staying inside inner boundary

GREEN = Good pace usage
YELLOW = Getting aggressive
RED = Maximum track usage (best!)
"""
    
    ax3.text(0.05, 0.95, stats_text, transform=ax3.transAxes,
             fontsize=9, color=text_color, family='monospace',
             verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"Validation visualization saved to: {output_path}")
    
    return {
        "avg_usage_pct": float(avg_usage),
        "max_usage_pct": float(max_usage),
        "min_usage_pct": float(min_usage),
        "aggressive_pct": float(aggressive_pct),
        "defensive_pct": float(defensive_pct),
        "aggressive_zones": len(aggressive_peaks)
    }


def main():
    if len(sys.argv) < 3:
        print(json.dumps({
            "error": "Usage: python validate_against_boundaries.py <your_lap.csv> <boundaries.json> [output.png] [--dark]"
        }))
        sys.exit(1)
    
    dark_mode = '--dark' in sys.argv
    args = [a for a in sys.argv if a != '--dark']
    
    lap_file = Path(args[1])
    boundaries_file = Path(args[2])
    output_path = args[3] if len(args) > 3 else "lap_validation.png"
    
    if not lap_file.exists():
        print(json.dumps({"error": f"Lap file not found: {lap_file}"}))
        sys.exit(1)
    
    if not boundaries_file.exists():
        print(json.dumps({"error": f"Boundaries file not found: {boundaries_file}"}))
        sys.exit(1)
    
    # Load data
    lap_df = load_telemetry(lap_file)
    boundaries = load_boundaries(boundaries_file)
    
    if lap_df is None or boundaries is None:
        print(json.dumps({"error": "Failed to load data"}))
        sys.exit(1)
    
    # Extract lap name
    lap_name = lap_file.stem
    if " - " in lap_name:
        parts = lap_name.split(" - ")
        if len(parts) >= 2:
            lap_name = parts[1]
    
    # Create visualization
    stats = create_validation_visualization(
        lap_df, boundaries, output_path,
        lap_name=lap_name,
        dark_mode=dark_mode
    )
    
    if stats:
        print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()

