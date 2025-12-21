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
    
    IMPORTANT: Garage 61 exports use m/s² for acceleration data:
    - LatAccel is in m/s² (need to divide by 9.81 to get G)
    - LongAccel is in m/s² (need to divide by 9.81 to get G)
    This function normalizes both to G for consistency.
    """
    if df is None or len(df) == 0:
        return None
    
    # Make a copy to avoid modifying the original
    df = df.copy()
    
    # FIX: Remove wrap-around points (where LapDistPct goes backwards)
    # Garage 61 sometimes includes the first point again at the end
    if 'LapDistPct' in df.columns and len(df) > 1:
        # Check if last point wraps back to start
        if df['LapDistPct'].iloc[-1] < df['LapDistPct'].iloc[-2]:
            df = df.iloc[:-1]  # Remove last row
        # Also ensure it's sorted (just in case)
        df = df.sort_values('LapDistPct').reset_index(drop=True)
    
    # FIX: Convert LatAccel from m/s² to G if it exists
    if 'LatAccel' in df.columns:
        # Check if values are suspiciously high (likely in m/s² not G)
        if df['LatAccel'].abs().max() > 5.0:  # FF1600 can't exceed ~2.5g lateral
            df['LatAccel'] = df['LatAccel'] / 9.81  # Convert m/s² to G
    
    # FIX: Convert LongAccel from m/s² to G if it exists
    if 'LongAccel' in df.columns:
        # Check if values are suspiciously high (likely in m/s² not G)
        if df['LongAccel'].abs().max() > 5.0:  # FF1600 can't exceed ~2g braking or 1g accel
            df['LongAccel'] = df['LongAccel'] / 9.81  # Convert m/s² to G
    
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
    
    # --- Cornering (G-forces) - ENHANCED ---
    if 'LongAccel' in current_interp.columns and 'LongAccel' in reference_interp.columns:
        comparison["cornering"]["current_max_braking_g"] = float(current_interp['LongAccel'].min())
        comparison["cornering"]["reference_max_braking_g"] = float(reference_interp['LongAccel'].min())
        comparison["cornering"]["braking_g_diff"] = float(current_interp['LongAccel'].min() - reference_interp['LongAccel'].min())
        
        comparison["cornering"]["current_max_accel_g"] = float(current_interp['LongAccel'].max())
        comparison["cornering"]["reference_max_accel_g"] = float(reference_interp['LongAccel'].max())
        comparison["cornering"]["accel_g_diff"] = float(current_interp['LongAccel'].max() - reference_interp['LongAccel'].max())
        
        # Longitudinal G smoothness (lower = smoother)
        comparison["cornering"]["current_long_g_smoothness"] = float(current_interp['LongAccel'].std())
        comparison["cornering"]["reference_long_g_smoothness"] = float(reference_interp['LongAccel'].std())
    
    if 'LatAccel' in current_interp.columns and 'LatAccel' in reference_interp.columns:
        current_lat_abs = current_interp['LatAccel'].abs()
        reference_lat_abs = reference_interp['LatAccel'].abs()
        
        comparison["cornering"]["current_max_lat_g"] = float(current_lat_abs.max())
        comparison["cornering"]["reference_max_lat_g"] = float(reference_lat_abs.max())
        comparison["cornering"]["lat_g_diff"] = float(current_lat_abs.max() - reference_lat_abs.max())
        
        # Average lateral G (shows overall cornering load)
        comparison["cornering"]["current_avg_lat_g"] = float(current_lat_abs.mean())
        comparison["cornering"]["reference_avg_lat_g"] = float(reference_lat_abs.mean())
        comparison["cornering"]["avg_lat_g_diff"] = float(current_lat_abs.mean() - reference_lat_abs.mean())
        
        # Lateral G smoothness (lower = smoother, higher = spiky/overdriving)
        comparison["cornering"]["current_lat_g_smoothness"] = float(current_lat_abs.std())
        comparison["cornering"]["reference_lat_g_smoothness"] = float(reference_lat_abs.std())
        comparison["cornering"]["lat_g_smoothness_diff"] = float(current_lat_abs.std() - reference_lat_abs.std())
        
        # Find where max lateral G occurs
        lat_g_diff = current_lat_abs.values - reference_lat_abs.values
        comparison["cornering"]["max_lat_g_gain"] = float(lat_g_diff.max())
        comparison["cornering"]["max_lat_g_loss"] = float(lat_g_diff.min())
        comparison["cornering"]["max_lat_g_gain_distance_pct"] = float(current_interp.loc[lat_g_diff.argmax(), 'distance_pct'])
        comparison["cornering"]["max_lat_g_loss_distance_pct"] = float(current_interp.loc[lat_g_diff.argmin(), 'distance_pct'])
    
    # Combined G-force (total load on car)
    if 'LongAccel' in current_interp.columns and 'LatAccel' in current_interp.columns:
        current_total_g = np.sqrt(current_interp['LongAccel']**2 + current_interp['LatAccel']**2)
        reference_total_g = np.sqrt(reference_interp['LongAccel']**2 + reference_interp['LatAccel']**2)
        
        comparison["cornering"]["current_max_total_g"] = float(current_total_g.max())
        comparison["cornering"]["reference_max_total_g"] = float(reference_total_g.max())
        comparison["cornering"]["max_total_g_diff"] = float(current_total_g.max() - reference_total_g.max())
        comparison["cornering"]["current_avg_total_g"] = float(current_total_g.mean())
        comparison["cornering"]["reference_avg_total_g"] = float(reference_total_g.mean())
    
    # --- Overdriving Detection (Steering vs Lateral G) ---
    if 'SteeringWheelAngle' in current_interp.columns and 'LatAccel' in current_interp.columns and 'Speed' in current_interp.columns:
        comparison["overdriving_indicators"] = analyze_overdriving(current_interp, reference_interp)
    
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
            
            # Add G-force data at each point
            if 'LatAccel' in current_interp.columns:
                point["current_lat_g"] = float(abs(current_interp.iloc[idx]['LatAccel']))
                point["reference_lat_g"] = float(abs(reference_interp.iloc[idx]['LatAccel']))
                point["lat_g_diff"] = float(abs(current_interp.iloc[idx]['LatAccel']) - abs(reference_interp.iloc[idx]['LatAccel']))
            
            if 'LongAccel' in current_interp.columns:
                point["current_long_g"] = float(current_interp.iloc[idx]['LongAccel'])
                point["reference_long_g"] = float(reference_interp.iloc[idx]['LongAccel'])
                point["long_g_diff"] = float(current_interp.iloc[idx]['LongAccel'] - reference_interp.iloc[idx]['LongAccel'])
            
            if 'SteeringWheelAngle' in current_interp.columns:
                point["current_steering"] = float(abs(current_interp.iloc[idx]['SteeringWheelAngle']))
                point["reference_steering"] = float(abs(reference_interp.iloc[idx]['SteeringWheelAngle']))
            
            comparison["distance_comparison"].append(point)
    
    return comparison


def analyze_overdriving(current_df, reference_df):
    """
    Detect overdriving indicators by comparing steering angle vs lateral G.
    
    High steering angle but low lateral G = sliding/overdriving
    High steering angle AND high lateral G = good load transfer
    """
    indicators = {}
    
    if 'SteeringWheelAngle' not in current_df.columns or 'LatAccel' not in current_df.columns:
        return indicators
    
    # Calculate absolute values for comparison
    current_steering_abs = current_df['SteeringWheelAngle'].abs()
    reference_steering_abs = reference_df['SteeringWheelAngle'].abs()
    current_lat_g_abs = current_df['LatAccel'].abs()
    reference_lat_g_abs = reference_df['LatAccel'].abs()
    
    # Average steering input
    indicators["current_avg_steering_angle"] = float(current_steering_abs.mean())
    indicators["reference_avg_steering_angle"] = float(reference_steering_abs.mean())
    indicators["avg_steering_diff"] = float(current_steering_abs.mean() - reference_steering_abs.mean())
    
    # Max steering input
    indicators["current_max_steering_angle"] = float(current_steering_abs.max())
    indicators["reference_max_steering_angle"] = float(reference_steering_abs.max())
    
    # Steering smoothness (std dev - lower is smoother)
    indicators["current_steering_smoothness"] = float(current_steering_abs.std())
    indicators["reference_steering_smoothness"] = float(reference_steering_abs.std())
    indicators["steering_smoothness_diff"] = float(current_steering_abs.std() - reference_steering_abs.std())
    
    # Calculate "efficiency" ratio: Lateral G per degree of steering
    # Higher = more efficient (getting more grip per steering input)
    current_efficiency = current_lat_g_abs / (current_steering_abs + 0.001)  # avoid divide by zero
    reference_efficiency = reference_lat_g_abs / (reference_steering_abs + 0.001)
    
    indicators["current_avg_steering_efficiency"] = float(current_efficiency.mean())
    indicators["reference_avg_steering_efficiency"] = float(reference_efficiency.mean())
    indicators["steering_efficiency_diff"] = float(current_efficiency.mean() - reference_efficiency.mean())
    
    # Find zones where you're using MORE steering but getting LESS lateral G (overdriving)
    overdriving_score = (current_steering_abs > reference_steering_abs) & (current_lat_g_abs < reference_lat_g_abs)
    indicators["overdriving_pct_of_lap"] = float((overdriving_score.sum() / len(current_df)) * 100)
    
    # Find zones where you're using LESS steering but getting MORE lateral G (better technique)
    better_technique = (current_steering_abs < reference_steering_abs) & (current_lat_g_abs > reference_lat_g_abs)
    indicators["better_technique_pct_of_lap"] = float((better_technique.sum() / len(current_df)) * 100)
    
    return indicators


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

