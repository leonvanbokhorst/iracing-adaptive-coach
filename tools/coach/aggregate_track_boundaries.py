#!/usr/bin/env python3
"""
Tool: Aggregate Track Boundary Data

Takes multiple "inner" and "outer" trace laps and averages them into
clean boundary definitions for track analysis.

This creates a reusable, open-source track boundary map that can be
used for any future lap analysis on this track.

Usage:
    python tools/coach/aggregate_track_boundaries.py <track_id> <inner_file_1> <inner_file_2> <inner_file_3> <outer_file_1> <outer_file_2> <outer_file_3> [output_dir]

Example:
    python tools/coach/aggregate_track_boundaries.py limerock-2019-gp \
        data/tracktrace/inside-1.csv \
        data/tracktrace/inside-2.csv \
        data/tracktrace/inside-3.csv \
        data/tracktrace/outside-1.csv \
        data/tracktrace/outside-2.csv \
        data/tracktrace/outside-3.csv
"""

import sys
import json
import pandas as pd
import numpy as np
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


def interpolate_to_common_distance(df, num_points=2000):
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
    
    for col in ['Lat', 'Lon']:
        if col in df.columns:
            try:
                f = interp1d(df['LapDistPct'].values, df[col].values, 
                           kind='linear', fill_value='extrapolate')
                result[col] = f(dist_new)
            except Exception as e:
                print(f"Warning: Could not interpolate {col}: {e}")
    
    return pd.DataFrame(result)


def aggregate_boundaries(inner_files, outer_files, num_points=3000):
    """
    Aggregate multiple boundary traces into averaged boundaries.
    
    Args:
        inner_files: List of paths to inner boundary laps
        outer_files: List of paths to outer boundary laps
        num_points: Number of points to interpolate to (for averaging)
    
    Returns:
        dict with averaged inner and outer boundaries
    """
    print(f"Loading {len(inner_files)} inner traces...")
    inner_traces = []
    for fpath in inner_files:
        df = load_telemetry(fpath)
        if df is None:
            print(f"  ✗ Failed: {fpath}")
            continue
        
        interp_df = interpolate_to_common_distance(df, num_points=num_points)
        if interp_df is not None:
            inner_traces.append(interp_df)
            print(f"  ✓ Loaded: {Path(fpath).name} ({len(interp_df)} points)")
    
    print(f"\nLoading {len(outer_files)} outer traces...")
    outer_traces = []
    for fpath in outer_files:
        df = load_telemetry(fpath)
        if df is None:
            print(f"  ✗ Failed: {fpath}")
            continue
        
        interp_df = interpolate_to_common_distance(df, num_points=num_points)
        if interp_df is not None:
            outer_traces.append(interp_df)
            print(f"  ✓ Loaded: {Path(fpath).name} ({len(interp_df)} points)")
    
    if not inner_traces or not outer_traces:
        print("Error: Not enough valid traces loaded")
        return None
    
    print(f"\nAggregating {len(inner_traces)} inner + {len(outer_traces)} outer traces...")
    
    # Stack all inner traces and average
    inner_stack = np.array([df[['Lat', 'Lon']].values for df in inner_traces])
    inner_avg_lat = np.mean(inner_stack[:, :, 0], axis=0)
    inner_avg_lon = np.mean(inner_stack[:, :, 1], axis=0)
    inner_std_lat = np.std(inner_stack[:, :, 0], axis=0)
    inner_std_lon = np.std(inner_stack[:, :, 1], axis=0)
    
    # Stack all outer traces and average
    outer_stack = np.array([df[['Lat', 'Lon']].values for df in outer_traces])
    outer_avg_lat = np.mean(outer_stack[:, :, 0], axis=0)
    outer_avg_lon = np.mean(outer_stack[:, :, 1], axis=0)
    outer_std_lat = np.std(outer_stack[:, :, 0], axis=0)
    outer_std_lon = np.std(outer_stack[:, :, 1], axis=0)
    
    # Calculate average confidence (lower std = higher confidence)
    inner_confidence = 1.0 - (np.mean(inner_std_lat) + np.mean(inner_std_lon)) / 0.0001
    outer_confidence = 1.0 - (np.mean(outer_std_lat) + np.mean(outer_std_lon)) / 0.0001
    inner_confidence = max(0, min(1, inner_confidence))  # Clamp 0-1
    outer_confidence = max(0, min(1, outer_confidence))
    
    result = {
        "inner_boundary": [
            {"distance_pct": float(inner_traces[0]['LapDistPct'].iloc[i]),
             "lat": float(inner_avg_lat[i]),
             "lon": float(inner_avg_lon[i]),
             "std_lat": float(inner_std_lat[i]),
             "std_lon": float(inner_std_lon[i])}
            for i in range(len(inner_avg_lat))
        ],
        "outer_boundary": [
            {"distance_pct": float(outer_traces[0]['LapDistPct'].iloc[i]),
             "lat": float(outer_avg_lat[i]),
             "lon": float(outer_avg_lon[i]),
             "std_lat": float(outer_std_lat[i]),
             "std_lon": float(outer_std_lon[i])}
            for i in range(len(outer_avg_lat))
        ],
        "metadata": {
            "inner_samples": len(inner_traces),
            "outer_samples": len(outer_traces),
            "inner_confidence": float(inner_confidence),
            "outer_confidence": float(outer_confidence),
            "points_per_boundary": len(inner_avg_lat),
            "inner_avg_std_lat": float(np.mean(inner_std_lat)),
            "inner_avg_std_lon": float(np.mean(inner_std_lon)),
            "outer_avg_std_lat": float(np.mean(outer_std_lat)),
            "outer_avg_std_lon": float(np.mean(outer_std_lon))
        }
    }
    
    return result


def save_boundaries(track_id, boundaries, output_dir="tracks/track-data"):
    """Save aggregated boundaries to JSON file."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / f"{track_id}-boundaries.json"
    
    with open(output_file, 'w') as f:
        json.dump(boundaries, f, indent=2)
    
    print(f"\n✓ Boundaries saved to: {output_file}")
    
    return output_file


def print_summary(boundaries):
    """Print summary of aggregated boundaries."""
    meta = boundaries['metadata']
    
    print("\n" + "="*60)
    print("TRACK BOUNDARY AGGREGATION SUMMARY")
    print("="*60)
    print(f"\nInner Boundary (From {meta['inner_samples']} laps):")
    print(f"  Confidence: {meta['inner_confidence']:.1%}")
    print(f"  Avg GPS noise (Lat):  {meta['inner_avg_std_lat']:.7f}°")
    print(f"  Avg GPS noise (Lon):  {meta['inner_avg_std_lon']:.7f}°")
    
    print(f"\nOuter Boundary (From {meta['outer_samples']} laps):")
    print(f"  Confidence: {meta['outer_confidence']:.1%}")
    print(f"  Avg GPS noise (Lat):  {meta['outer_avg_std_lat']:.7f}°")
    print(f"  Avg GPS noise (Lon):  {meta['outer_avg_std_lon']:.7f}°")
    
    print(f"\nTotal points per boundary: {meta['points_per_boundary']:,}")
    print("\n" + "="*60)


def main():
    if len(sys.argv) < 8:
        print(json.dumps({
            "error": "Usage: python aggregate_track_boundaries.py <track_id> <inner_1> <inner_2> <inner_3> <outer_1> <outer_2> <outer_3> [output_dir]"
        }))
        sys.exit(1)
    
    track_id = sys.argv[1]
    inner_files = [sys.argv[2], sys.argv[3], sys.argv[4]]
    outer_files = [sys.argv[5], sys.argv[6], sys.argv[7]]
    output_dir = sys.argv[8] if len(sys.argv) > 8 else "tracks/track-data"
    
    # Verify files exist
    all_files = inner_files + outer_files
    for fpath in all_files:
        if not Path(fpath).exists():
            print(json.dumps({"error": f"File not found: {fpath}"}))
            sys.exit(1)
    
    # Aggregate boundaries
    boundaries = aggregate_boundaries(inner_files, outer_files)
    
    if boundaries is None:
        print(json.dumps({"error": "Failed to aggregate boundaries"}))
        sys.exit(1)
    
    # Print summary
    print_summary(boundaries)
    
    # Save to file
    output_file = save_boundaries(track_id, boundaries, output_dir)
    
    # Output JSON with file location
    result = {
        "status": "success",
        "track_id": track_id,
        "output_file": str(output_file),
        "metadata": boundaries['metadata']
    }
    
    print(f"\nJSON output:\n{json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()

