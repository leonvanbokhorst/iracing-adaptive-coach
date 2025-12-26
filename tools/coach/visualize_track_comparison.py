#!/usr/bin/env python3
"""
Coach Tool: Visualize Track Speed Delta Comparison - GENERIC FOR ANY TRACK

Creates a visual map of the track showing speed differences between
current lap and reference lap using GPS coordinates.

This tool is track-agnostic and works for any circuit with GPS data.

Features:
- Automatically extracts track name from Garage 61 filename
- Automatically extracts lap times from Garage 61 filename format
- Generates color-coded track map (green = faster, red = slower)
- Marks key locations (gains/losses) on the map
- Prints detailed stats to terminal for Little Padawan to interpret
- Clean, reusable visualization for any track/comparison

Usage:
    python tools/coach/visualize_track_comparison.py <current_lap.csv> <reference_lap.csv> <output_image.png>

Example:
    python tools/coach/visualize_track_comparison.py \\
        "data/Garage 61 - Driver - Car - Track - 01.29.691 - ID.csv" \\
        "data/compare/Garage 61 - Driver - Car - Track - 01.28.969 - ID.csv" \\
        "weeks/week02/comparison/track-speed-delta-map.png"
    
Output:
    - PNG image with clean track map (20x20 figure, high resolution)
    - Terminal output with detailed stats for coaching
    - JSON file with track data points for reference

Philosophy:
    Tools provide FACTS (printed to terminal as structured data)
    Little Padawan provides MEANING (coaching narrative based on facts)
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path


def load_telemetry(filepath):
    """Load telemetry CSV file"""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def gps_to_meters(lat, lon):
    """
    Convert GPS coordinates to meters using equirectangular projection.
    This is the PROPER way that actually works!
    """
    lat_center = np.mean(lat)
    lon_center = np.mean(lon)
    
    # Convert to approximate meters
    lat_scale = 111320  # meters per degree latitude
    lon_scale = 111320 * np.cos(np.radians(lat_center))  # meters per degree longitude
    
    x = (lon - lon_center) * lon_scale
    y = (lat - lat_center) * lat_scale
    
    return x, y


def calculate_speed_delta(current_df, reference_df):
    """
    Calculate speed delta between current and reference laps.
    Uses actual GPS coordinates (no interpolation to preserve track shape!)
    """
    # Use ACTUAL GPS coordinates from current lap (DON'T interpolate - that creates straight lines!)
    current_lat = current_df['Lat'].values
    current_lon = current_df['Lon'].values
    current_speed = current_df['Speed'].values
    current_dist = current_df['LapDistPct'].values
    
    # For each point in current lap, find closest point in reference lap by distance
    reference_speed_matched = np.zeros_like(current_speed)
    
    for i, dist in enumerate(current_dist):
        # Find closest distance point in reference lap
        idx = np.argmin(np.abs(reference_df['LapDistPct'].values - dist))
        reference_speed_matched[i] = reference_df['Speed'].values[idx]
    
    # Calculate delta (m/s)
    speed_delta = current_speed - reference_speed_matched
    
    # Convert GPS to meters (proper equirectangular projection)
    x, y = gps_to_meters(current_lat, current_lon)
    
    return {
        'lap_dist': current_dist,
        'x': x,  # meters
        'y': y,  # meters
        'lat': current_lat,
        'lon': current_lon,
        'current_speed': current_speed,
        'reference_speed': reference_speed_matched,
        'speed_delta': speed_delta
    }


def create_track_visualization(data, output_path, current_time, reference_time, track_name="Track"):
    """
    Create a beautiful track map with speed delta visualization.
    Stats are printed to terminal for Little Padawan to interpret.
    """
    # Create figure - CLEAN track map only
    fig, ax_map = plt.subplots(1, 1, figsize=(20, 20))
    
    # Convert speed delta from m/s to km/h
    speed_delta_kmh = data['speed_delta'] * 3.6
    
    # Create color map (red = slower, white = same, green = faster)
    # Normalize around 0 with symmetric scale
    max_delta = max(abs(speed_delta_kmh.min()), abs(speed_delta_kmh.max()))
    norm = plt.Normalize(vmin=-max_delta, vmax=max_delta)
    cmap = plt.cm.RdYlGn  # Red-Yellow-Green
    
    # Plot track as colored line segments (using meters, not GPS degrees!)
    x = data['x']
    y = data['y']
    
    # Plot each segment with color based on speed delta
    for i in range(len(x) - 1):
        color = cmap(norm(speed_delta_kmh[i]))
        ax_map.plot([x[i], x[i+1]], [y[i], y[i+1]], 
                   color=color, linewidth=15, solid_capstyle='round')
    
    # Mark specific problem zones
    # 40% lap distance (biggest loss)
    # Store indices for terminal output only (markers disabled for cleaner view)
    idx_40 = int(0.40 * len(x))
    idx_0 = 0
    idx_10 = int(0.10 * len(x))
    idx_50 = int(0.50 * len(x))
    
    # Start/Finish line
    ax_map.plot(x[0], y[0], 'w^', markersize=15, zorder=5, 
               markeredgecolor='black', markeredgewidth=2)
    ax_map.text(x[0], y[0], '  START/FINISH', fontsize=12, 
               fontweight='bold', va='bottom', ha='left',
               bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Styling - equal aspect for meters
    ax_map.set_aspect('equal')
    ax_map.set_xlabel('X Position (meters)', fontsize=14, fontweight='bold')
    ax_map.set_ylabel('Y Position (meters)', fontsize=14, fontweight='bold')
    
    # Adjust margins to show full track
    x_margin = (x.max() - x.min()) * 0.1
    y_margin = (y.max() - y.min()) * 0.1
    ax_map.set_xlim(x.min() - x_margin, x.max() + x_margin)
    ax_map.set_ylim(y.min() - y_margin, y.max() + y_margin)
    ax_map.set_title(f'{track_name} - Speed Delta Map\n' + 
                    f'Current: {current_time} vs Reference: {reference_time}',
                    fontsize=18, fontweight='bold', pad=20)
    ax_map.grid(True, alpha=0.2, linestyle='--')
    # Legend disabled for cleaner view
    # ax_map.legend(loc='upper left', fontsize=12, framealpha=0.95)
    
    # Color bar - larger and clearer
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax_map, orientation='horizontal', 
                       pad=0.05, aspect=40, shrink=0.8)
    cbar.set_label('Speed Delta (km/h) — Green: Faster, Red: Slower', 
                  fontsize=14, fontweight='bold')
    cbar.ax.tick_params(labelsize=12)
    
    plt.tight_layout()
    
    # Save the figure
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✅ Track visualization saved to: {output_path}")
    
    # ============================================================================
    # PRINT STATS TO TERMINAL FOR LITTLE PADAWAN TO INTERPRET
    # ============================================================================
    
    # Calculate time deltas
    gap_s = float(current_time.split(':')[0])*60 + float(current_time.split(':')[1]) - (float(reference_time.split(':')[0])*60 + float(reference_time.split(':')[1]))
    
    # Find max gain/loss locations
    max_gain_idx = speed_delta_kmh.argmax()
    max_loss_idx = speed_delta_kmh.argmin()
    
    # Print structured stats for Little Padawan to interpret
    print("\n" + "="*80)
    print("📊 TELEMETRY COMPARISON DATA")
    print("="*80)
    print(f"\nTrack: {track_name}")
    print(f"Current Lap:   {current_time}")
    print(f"Reference Lap: {reference_time}")
    print(f"Gap:           {gap_s:.3f}s")
    
    print(f"\n{'='*80}")
    print("📈 SPEED DELTA STATISTICS")
    print("="*80)
    print(f"Max Gain:  +{speed_delta_kmh.max():.2f} km/h  @ {data['lap_dist'][max_gain_idx]*100:.1f}% lap")
    print(f"Max Loss:  {speed_delta_kmh.min():.2f} km/h  @ {data['lap_dist'][max_loss_idx]*100:.1f}% lap")
    print(f"Avg Delta: {speed_delta_kmh.mean():.2f} km/h")
    
    print(f"\n{'='*80}")
    print("📍 KEY LOCATIONS")
    print("="*80)
    
    # Specific markers on map
    print(f"\n🔴 Red X @ 40% lap:")
    print(f"   Delta: {speed_delta_kmh[idx_40]:.2f} km/h")
    print(f"   Status: {'SLOWER' if speed_delta_kmh[idx_40] < 0 else 'FASTER'}")
    
    print(f"\n🟠 Orange X @ Start/Finish:")
    print(f"   Delta: {speed_delta_kmh[idx_0]:.2f} km/h")
    print(f"   Status: {'SLOWER' if speed_delta_kmh[idx_0] < 0 else 'FASTER'}")
    
    print(f"\n⭐ Green Star @ 10% lap:")
    print(f"   Delta: {speed_delta_kmh[idx_10]:.2f} km/h")
    print(f"   Status: {'SLOWER' if speed_delta_kmh[idx_10] < 0 else 'FASTER'}")
    
    print(f"\n⭐ Green Star @ 50% lap:")
    print(f"   Delta: {speed_delta_kmh[idx_50]:.2f} km/h")
    print(f"   Status: {'SLOWER' if speed_delta_kmh[idx_50] < 0 else 'FASTER'}")
    
    print(f"\n{'='*80}")
    print("🎨 VISUAL SUMMARY")
    print("="*80)
    faster_pct = (speed_delta_kmh > 0).sum() / len(speed_delta_kmh) * 100
    slower_pct = (speed_delta_kmh < 0).sum() / len(speed_delta_kmh) * 100
    print(f"Faster sections: {faster_pct:.1f}% of lap (green on map)")
    print(f"Slower sections: {slower_pct:.1f}% of lap (red on map)")
    
    print(f"\n{'='*80}")
    print("✅ Little Padawan: Use this data to create your coaching narrative!")
    print("="*80 + "\n")
    
    # Also save data for reference
    data_output = str(output_path).replace('.png', '-data.json')
    with open(data_output, 'w') as f:
        json.dump({
            'max_gain_kmh': float(speed_delta_kmh.max()),
            'max_loss_kmh': float(speed_delta_kmh.min()),
            'avg_delta_kmh': float(speed_delta_kmh.mean()),
            'problem_zone_40pct': {
                'lap_pct': 0.40,
                'delta_kmh': float(speed_delta_kmh[idx_40]),
                'x_m': float(x[idx_40]),
                'y_m': float(y[idx_40])
            },
            'problem_zone_0pct': {
                'lap_pct': 0.0,
                'delta_kmh': float(speed_delta_kmh[idx_0]),
                'x_m': float(x[idx_0]),
                'y_m': float(y[idx_0])
            },
            'gain_zone_10pct': {
                'lap_pct': 0.10,
                'delta_kmh': float(speed_delta_kmh[idx_10]),
                'x_m': float(x[idx_10]),
                'y_m': float(y[idx_10])
            },
            'gain_zone_50pct': {
                'lap_pct': 0.50,
                'delta_kmh': float(speed_delta_kmh[idx_50]),
                'x_m': float(x[idx_50]),
                'y_m': float(y[idx_50])
            }
        }, f, indent=2)
    print(f"✅ Track data saved to: {data_output}")
    
    return output_path


def main():
    if len(sys.argv) != 4:
        print("Usage: python visualize_track_comparison.py <current_lap.csv> <reference_lap.csv> <output_image.png>")
        sys.exit(1)
    
    current_file = Path(sys.argv[1])
    reference_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    
    if not current_file.exists():
        print(f"❌ Current lap file not found: {current_file}")
        sys.exit(1)
    
    if not reference_file.exists():
        print(f"❌ Reference lap file not found: {reference_file}")
        sys.exit(1)
    
    print(f"📊 Loading telemetry files...")
    current_df = load_telemetry(current_file)
    reference_df = load_telemetry(reference_file)
    
    if current_df is None or reference_df is None:
        print("❌ Failed to load telemetry files")
        sys.exit(1)
    
    print(f"🔍 Calculating speed deltas...")
    data = calculate_speed_delta(current_df, reference_df)
    
    # Auto-detect track name from filename
    track_name = "Track"
    filename_parts = current_file.stem.split(" - ")
    if len(filename_parts) >= 4:
        track_name = filename_parts[3]  # Track name from Garage 61 format
    
    # Extract lap times from filenames (Garage 61 format: "...TrackName - MM.SS.mmm - ...")
    current_time = "Unknown"
    reference_time = "Unknown"
    
    for part in filename_parts:
        if "." in part and len(part.split(".")) == 3:
            time_parts = part.split(".")
            if len(time_parts[0]) == 2:  # MM.SS.mmm format
                mins = int(time_parts[0])
                secs = int(time_parts[1])
                current_time = f"{mins}:{secs:02d}.{time_parts[2]}"
                break
    
    ref_filename_parts = reference_file.stem.split(" - ")
    for part in ref_filename_parts:
        if "." in part and len(part.split(".")) == 3:
            time_parts = part.split(".")
            if len(time_parts[0]) == 2:
                mins = int(time_parts[0])
                secs = int(time_parts[1])
                reference_time = f"{mins}:{secs:02d}.{time_parts[2]}"
                break
    
    print(f"🎨 Creating track visualization...")
    print(f"   Track: {track_name}")
    print(f"   Current: {current_time}")
    print(f"   Reference: {reference_time}")
    
    create_track_visualization(data, output_file, 
                               current_time=current_time,
                               reference_time=reference_time,
                               track_name=track_name)
    
    print(f"\n✅ DONE! Check terminal output above for stats! 🏎️📊")


if __name__ == "__main__":
    main()

