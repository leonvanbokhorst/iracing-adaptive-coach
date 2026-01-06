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
    python tools/coach/visualize_track_comparison.py <current_lap.csv> <reference_lap.csv> <output_image.png> [options]

Options:
    --current_time "1:25.710"   Override current lap time
    --ref_time "1:26.090"       Override reference lap time
    --track_name "Winton"       Override track name

Example:
    python tools/coach/visualize_track_comparison.py \
        "data/processed/lap.csv" \
        "data/compare/ref.csv" \
        "output.png" \
        --current_time "1:25.710" --ref_time "1:26.090"

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
import argparse
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


def create_track_visualization(data, output_path, current_time, reference_time, track_name="Track", corner_positions=None):
    """
    Create a beautiful track map with speed delta visualization.
    Stats are printed to terminal for Little Padawan to interpret.
    
    Args:
        corner_positions: Optional list of corner positions as fractions (e.g., [0.155, 0.285, ...] for T1, T2, ...)
    """
    # Create figure - CLEAN track map only
    fig, ax_map = plt.subplots(1, 1, figsize=(20, 20))
    
    # Convert speed delta from m/s to km/h
    speed_delta_kmh = data['speed_delta'] * 3.6
    
    # Create color map (red = slower, white = same, green = faster)
    # Normalize around 0 with symmetric scale
    max_delta = max(abs(speed_delta_kmh.min()), abs(speed_delta_kmh.max()))
    if max_delta == 0: max_delta = 1.0 # Prevent div by zero
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
    
    # Mark corners if provided
    if corner_positions:
        lap_dist = data['lap_dist']
        for i, corner_pct in enumerate(corner_positions, start=1):
            # Find closest point on track to this corner position
            idx = np.argmin(np.abs(lap_dist - corner_pct))
            
            # Plot corner marker (dark circle with white edge)
            ax_map.scatter([x[idx]], [y[idx]], color='#2C3E50', 
                          s=300, zorder=12, marker='o', edgecolors='white', linewidths=2.5)
            
            # Add corner label (white text centered on marker)
            ax_map.annotate(f'{i}', (x[idx], y[idx]), 
                           textcoords="offset points", 
                           xytext=(0, 0),  # Centered on marker
                           fontsize=11, 
                           color='white', 
                           fontweight='bold',
                           ha='center', 
                           va='center',
                           zorder=13)
    
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
    
    # Calculate time deltas if valid times provided
    gap_s = 0.0
    try:
        curr_parts = current_time.split(':')
        ref_parts = reference_time.split(':')
        if len(curr_parts) == 2 and len(ref_parts) == 2:
            curr_seconds = float(curr_parts[0])*60 + float(curr_parts[1])
            ref_seconds = float(ref_parts[0])*60 + float(ref_parts[1])
            gap_s = curr_seconds - ref_seconds
    except:
        gap_s = 0.0
    
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


def parse_lap_time(filename):
    """Attempt to parse lap time from Garage 61 filename"""
    parts = Path(filename).stem.split(" - ")
    for part in parts:
        if "." in part and len(part.split(".")) == 3:
            time_parts = part.split(".")
            if len(time_parts[0]) == 2 and time_parts[0].isdigit():
                return f"{int(time_parts[0])}:{int(time_parts[1]):02d}.{time_parts[2]}"
    return "Unknown"


def main():
    parser = argparse.ArgumentParser(description="Visualize Track Speed Delta Comparison")
    parser.add_argument("current_file", help="Path to current lap telemetry CSV")
    parser.add_argument("reference_file", help="Path to reference lap telemetry CSV")
    parser.add_argument("output_file", help="Path to save output PNG")
    parser.add_argument("--current_time", help="Override current lap time (e.g., 1:25.710)")
    parser.add_argument("--ref_time", help="Override reference lap time (e.g., 1:26.090)")
    parser.add_argument("--track_name", help="Override track name")
    parser.add_argument("--corners", nargs='*', type=float, default=None,
                       metavar='POSITION',
                       help="Corner positions as fractions (e.g., '0.155 0.285 0.417' for T1, T2, T3, ...)")
    
    args = parser.parse_args()
    
    current_file = Path(args.current_file)
    reference_file = Path(args.reference_file)
    output_file = Path(args.output_file)
    
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
    
    # Determine times
    current_time = args.current_time if args.current_time else parse_lap_time(current_file)
    reference_time = args.ref_time if args.ref_time else parse_lap_time(reference_file)
    
    # Determine track name
    track_name = args.track_name
    if not track_name:
        parts = current_file.stem.split(" - ")
        if len(parts) >= 4:
            track_name = parts[3]
        else:
            track_name = "Track"
    
    print(f"🎨 Creating track visualization...")
    print(f"   Track: {track_name}")
    print(f"   Current: {current_time}")
    print(f"   Reference: {reference_time}")
    
    create_track_visualization(data, output_file, 
                               current_time=current_time,
                               reference_time=reference_time,
                               track_name=track_name,
                               corner_positions=args.corners)
    
    print(f"\n✅ DONE! Check terminal output above for stats! 🏎️📊")


if __name__ == "__main__":
    main()
