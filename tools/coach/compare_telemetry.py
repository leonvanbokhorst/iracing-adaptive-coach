#!/usr/bin/env python3
"""
Coach Tool: Compare Telemetry (FACTS ONLY)

Compares two telemetry files (current lap vs reference lap) and outputs
pure factual differences in speed, braking, throttle, and G-forces.

Little Padawan reads this output and gives it coaching meaning.

Usage:
    python tools/coach/compare_telemetry.py <current_lap.csv> <reference_lap.csv>
    
Output: JSON with factual comparison data
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path


def load_telemetry(filepath):
    """Load telemetry CSV file"""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        return None


def interpolate_telemetry(df, target_length=1000):
    """
    Interpolate telemetry data to a common length for comparison.
    Uses distance-based interpolation if available, otherwise time-based.
    """
    if df is None or len(df) == 0:
        return None
    
    # Check what columns we have
    has_distance = 'LapDistPct' in df.columns
    
    if has_distance:
        # Use distance percentage (0-1) for interpolation
        x_old = df['LapDistPct'].values
    else:
        # Use normalized time (0-1)
        x_old = np.linspace(0, 1, len(df))
    
    # Create new evenly spaced points
    x_new = np.linspace(0, 1, target_length)
    
    # Interpolate each column
    interpolated = {'distance_pct': x_new}
    
    for col in df.columns:
        if col != 'LapDistPct' and df[col].dtype in [np.float64, np.int64]:
            try:
                interpolated[col] = np.interp(x_new, x_old, df[col].values)
            except:
                pass
    
    return pd.DataFrame(interpolated)


def compare_metrics(current_df, reference_df):
    """
    Compare key metrics between current and reference laps.
    Returns factual differences only.
    """
    if current_df is None or reference_df is None:
        return {"error": "Could not load one or both telemetry files"}
    
    # Interpolate both to same length for comparison
    current_interp = interpolate_telemetry(current_df)
    reference_interp = interpolate_telemetry(reference_df)
    
    if current_interp is None or reference_interp is None:
        return {"error": "Could not interpolate telemetry data"}
    
    comparison = {
        "lap_summary": {},
        "speed": {},
        "braking": {},
        "throttle": {},
        "cornering": {},
        "distance_comparison": []
    }
    
    # --- Lap Summary ---
    comparison["lap_summary"] = {
        "current_samples": len(current_df),
        "reference_samples": len(reference_df),
        "interpolated_points": len(current_interp)
    }
    
    # --- Speed Comparison ---
    if 'Speed' in current_interp.columns and 'Speed' in reference_interp.columns:
        speed_diff = current_interp['Speed'].values - reference_interp['Speed'].values
        
        comparison["speed"] = {
            "current_top": float(current_interp['Speed'].max()),
            "reference_top": float(reference_interp['Speed'].max()),
            "top_diff": float(current_interp['Speed'].max() - reference_interp['Speed'].max()),
            "current_avg": float(current_interp['Speed'].mean()),
            "reference_avg": float(reference_interp['Speed'].mean()),
            "avg_diff": float(current_interp['Speed'].mean() - reference_interp['Speed'].mean()),
            "max_gain": float(speed_diff.max()),
            "max_loss": float(speed_diff.min()),
            "gain_distance_pct": float(current_interp.loc[speed_diff.argmax(), 'distance_pct']),
            "loss_distance_pct": float(current_interp.loc[speed_diff.argmin(), 'distance_pct'])
        }
    
    # --- Braking Comparison ---
    if 'Brake' in current_interp.columns and 'Brake' in reference_interp.columns:
        current_braking = current_interp['Brake'] > 0
        reference_braking = reference_interp['Brake'] > 0
        
        comparison["braking"] = {
            "current_max_pressure": float(current_interp['Brake'].max()),
            "reference_max_pressure": float(reference_interp['Brake'].max()),
            "current_braking_pct": float((current_braking.sum() / len(current_interp)) * 100),
            "reference_braking_pct": float((reference_braking.sum() / len(reference_interp)) * 100),
            "braking_time_diff_pct": float(((current_braking.sum() - reference_braking.sum()) / len(current_interp)) * 100)
        }
        
        # Find braking zones (where brake > 0.1)
        current_brake_zones = find_zones(current_interp, 'Brake', threshold=0.1)
        reference_brake_zones = find_zones(reference_interp, 'Brake', threshold=0.1)
        
        comparison["braking"]["current_brake_zones"] = len(current_brake_zones)
        comparison["braking"]["reference_brake_zones"] = len(reference_brake_zones)
    
    # --- Throttle Comparison ---
    if 'Throttle' in current_interp.columns and 'Throttle' in reference_interp.columns:
        current_full_throttle = current_interp['Throttle'] > 0.95
        reference_full_throttle = reference_interp['Throttle'] > 0.95
        
        comparison["throttle"] = {
            "current_full_throttle_pct": float((current_full_throttle.sum() / len(current_interp)) * 100),
            "reference_full_throttle_pct": float((reference_full_throttle.sum() / len(reference_interp)) * 100),
            "full_throttle_diff_pct": float(((current_full_throttle.sum() - reference_full_throttle.sum()) / len(current_interp)) * 100),
            "current_avg_throttle": float(current_interp['Throttle'].mean()),
            "reference_avg_throttle": float(reference_interp['Throttle'].mean()),
            "avg_throttle_diff": float(current_interp['Throttle'].mean() - reference_interp['Throttle'].mean())
        }
    
    # --- Cornering (G-forces) ---
    if 'LongAccel' in current_interp.columns and 'LongAccel' in reference_interp.columns:
        comparison["cornering"]["current_max_braking_g"] = float(current_interp['LongAccel'].min())
        comparison["cornering"]["reference_max_braking_g"] = float(reference_interp['LongAccel'].min())
        comparison["cornering"]["braking_g_diff"] = float(current_interp['LongAccel'].min() - reference_interp['LongAccel'].min())
    
    if 'LatAccel' in current_interp.columns and 'LatAccel' in reference_interp.columns:
        comparison["cornering"]["current_max_lat_g"] = float(current_interp['LatAccel'].abs().max())
        comparison["cornering"]["reference_max_lat_g"] = float(reference_interp['LatAccel'].abs().max())
        comparison["cornering"]["lat_g_diff"] = float(current_interp['LatAccel'].abs().max() - reference_interp['LatAccel'].abs().max())
    
    # --- Distance-based Comparison (sample every 10% of lap) ---
    if 'Speed' in current_interp.columns and 'Speed' in reference_interp.columns:
        for pct in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
            idx = int(pct * (len(current_interp) - 1))
            
            point = {
                "distance_pct": float(pct),
                "current_speed": float(current_interp.iloc[idx]['Speed']),
                "reference_speed": float(reference_interp.iloc[idx]['Speed']),
                "speed_diff": float(current_interp.iloc[idx]['Speed'] - reference_interp.iloc[idx]['Speed'])
            }
            
            if 'Brake' in current_interp.columns:
                point["current_brake"] = float(current_interp.iloc[idx]['Brake'])
                point["reference_brake"] = float(reference_interp.iloc[idx]['Brake'])
            
            if 'Throttle' in current_interp.columns:
                point["current_throttle"] = float(current_interp.iloc[idx]['Throttle'])
                point["reference_throttle"] = float(reference_interp.iloc[idx]['Throttle'])
            
            comparison["distance_comparison"].append(point)
    
    return comparison


def find_zones(df, column, threshold=0.1):
    """Find zones where a column value exceeds threshold"""
    zones = []
    in_zone = False
    zone_start = None
    
    for idx, val in enumerate(df[column]):
        if val > threshold and not in_zone:
            in_zone = True
            zone_start = df.iloc[idx]['distance_pct']
        elif val <= threshold and in_zone:
            in_zone = False
            zone_end = df.iloc[idx-1]['distance_pct']
            zones.append({"start": float(zone_start), "end": float(zone_end)})
    
    return zones


def main():
    if len(sys.argv) != 3:
        print(json.dumps({
            "error": "Usage: python compare_telemetry.py <current_lap.csv> <reference_lap.csv>"
        }))
        sys.exit(1)
    
    current_file = Path(sys.argv[1])
    reference_file = Path(sys.argv[2])
    
    if not current_file.exists():
        print(json.dumps({"error": f"Current lap file not found: {current_file}"}))
        sys.exit(1)
    
    if not reference_file.exists():
        print(json.dumps({"error": f"Reference lap file not found: {reference_file}"}))
        sys.exit(1)
    
    # Load telemetry
    current_df = load_telemetry(current_file)
    reference_df = load_telemetry(reference_file)
    
    # Compare
    comparison = compare_metrics(current_df, reference_df)
    
    # Output JSON
    print(json.dumps(comparison, indent=2))


if __name__ == "__main__":
    main()

