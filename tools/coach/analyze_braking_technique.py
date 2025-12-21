#!/usr/bin/env python3
"""
Braking Technique Analyzer (FACTS ONLY)

Analyzes braking technique from telemetry data:
- Detects brake zones
- Measures initial pressure, release smoothness, trail braking
- Compares brake zones between laps
- Identifies technique patterns

Little Padawan reads this output and creates coaching narrative.

Usage:
    python tools/coach/analyze_braking_technique.py <current_lap.csv> [reference_lap.csv]
    
Output: JSON with factual brake zone analysis
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path


def load_telemetry(file_path):
    """Load and clean telemetry data"""
    df = pd.read_csv(file_path)
    
    # Auto-detect and convert G-forces if needed (Garage 61 exports in m/s²)
    if 'LatAccel' in df.columns and df['LatAccel'].abs().max() > 5.0:
        df['LatAccel'] = df['LatAccel'] / 9.81
    if 'LongAccel' in df.columns and df['LongAccel'].abs().max() > 5.0:
        df['LongAccel'] = df['LongAccel'] / 9.81
    
    # Remove wrap-around points (where distance goes backwards)
    if 'LapDistPct' in df.columns:
        df = df[df['LapDistPct'].diff().fillna(1) >= 0].reset_index(drop=True)
    
    return df


def detect_brake_zones(df, min_pressure=0.1, min_duration=0.3):
    """
    Detect brake zones in telemetry data
    
    Args:
        df: Telemetry dataframe
        min_pressure: Minimum brake pressure to consider as braking
        min_duration: Minimum duration (seconds) to consider as brake zone
        
    Returns:
        List of brake zones with start/end indices
    """
    brake_zones = []
    in_brake_zone = False
    zone_start = None
    
    # Estimate sample rate (samples per second)
    total_samples = len(df)
    if total_samples > 1:
        sample_rate = total_samples / (total_samples * 0.0167)  # Rough estimate
    else:
        sample_rate = 60  # Default to 60 Hz
    
    min_samples = int(min_duration * sample_rate)
    
    for idx, row in df.iterrows():
        brake = row.get('Brake', 0)
        
        if brake >= min_pressure and not in_brake_zone:
            # Start of brake zone
            zone_start = idx
            in_brake_zone = True
        elif brake < min_pressure and in_brake_zone:
            # End of brake zone
            zone_end = idx - 1
            zone_length = zone_end - zone_start + 1
            
            if zone_length >= min_samples:
                brake_zones.append({
                    'start_idx': zone_start,
                    'end_idx': zone_end,
                    'samples': zone_length
                })
            
            in_brake_zone = False
            zone_start = None
    
    # Handle case where brake zone extends to end of lap
    if in_brake_zone and zone_start is not None:
        zone_end = len(df) - 1
        zone_length = zone_end - zone_start + 1
        if zone_length >= min_samples:
            brake_zones.append({
                'start_idx': zone_start,
                'end_idx': zone_end,
                'samples': zone_length
            })
    
    return brake_zones


def analyze_brake_zone(df, zone):
    """
    Analyze a single brake zone
    
    Returns:
        Dictionary with brake zone metrics
    """
    start = zone['start_idx']
    end = zone['end_idx']
    zone_df = df.iloc[start:end+1]
    
    # Basic metrics
    brake_pressures = zone_df['Brake'].values
    max_pressure = brake_pressures.max()
    avg_pressure = brake_pressures.mean()
    initial_pressure = brake_pressures[0] if len(brake_pressures) > 0 else 0
    
    # Duration (rough estimate)
    duration = len(zone_df) / 60.0  # Assume 60 Hz
    
    # Lap distance
    start_dist = df.iloc[start]['LapDistPct'] if 'LapDistPct' in df.columns else 0
    end_dist = df.iloc[end]['LapDistPct'] if 'LapDistPct' in df.columns else 0
    
    # Release smoothness (lower = smoother)
    # Calculate standard deviation of pressure changes
    pressure_changes = np.diff(brake_pressures)
    release_smoothness = np.std(pressure_changes) if len(pressure_changes) > 0 else 0
    
    # Trail braking detection: overlap with steering
    steering_angles = zone_df['SteeringWheelAngle'].abs().values if 'SteeringWheelAngle' in zone_df else np.zeros(len(zone_df))
    max_steering = steering_angles.max()
    avg_steering = steering_angles.mean()
    
    # Detect if steering increases while braking (trail braking indicator)
    trail_braking_detected = False
    if len(steering_angles) > 5:
        # Check if steering increases in second half of brake zone
        mid_point = len(steering_angles) // 2
        first_half_steering = steering_angles[:mid_point].mean()
        second_half_steering = steering_angles[mid_point:].mean()
        trail_braking_detected = second_half_steering > first_half_steering * 1.2
    
    # Pressure profile type
    # Smooth ramp: pressure decreases linearly
    # Stab: pressure stays high then drops suddenly
    # Early release: pressure drops quickly
    
    if len(brake_pressures) > 10:
        first_third = brake_pressures[:len(brake_pressures)//3].mean()
        last_third = brake_pressures[-len(brake_pressures)//3:].mean()
        pressure_drop_rate = (first_third - last_third) / duration if duration > 0 else 0
        
        # Classify profile
        if release_smoothness < 0.05 and pressure_drop_rate > 0:
            profile_type = "smooth_ramp"
        elif release_smoothness > 0.1:
            profile_type = "jagged"
        elif last_third < 0.1 and first_third > 0.7:
            profile_type = "early_release"
        else:
            profile_type = "normal"
    else:
        profile_type = "too_short"
        pressure_drop_rate = 0
    
    # Brake + steering overload detection
    # Find moments where both brake and steering are high
    high_brake_threshold = 0.7
    high_steering_threshold = 0.3  # radians
    overload_samples = 0
    
    for i in range(len(zone_df)):
        brake = brake_pressures[i]
        steering = steering_angles[i]
        if brake > high_brake_threshold and steering > high_steering_threshold:
            overload_samples += 1
    
    overload_pct = (overload_samples / len(zone_df) * 100) if len(zone_df) > 0 else 0
    
    return {
        'lap_distance_start_pct': round(float(start_dist) * 100, 1),
        'lap_distance_end_pct': round(float(end_dist) * 100, 1),
        'duration_seconds': round(float(duration), 2),
        'max_pressure': round(float(max_pressure), 3),
        'avg_pressure': round(float(avg_pressure), 3),
        'initial_pressure': round(float(initial_pressure), 3),
        'release_smoothness': round(float(release_smoothness), 4),
        'profile_type': profile_type,
        'pressure_drop_rate': round(float(pressure_drop_rate), 3),
        'max_steering_angle_rad': round(float(max_steering), 3),
        'avg_steering_angle_rad': round(float(avg_steering), 3),
        'trail_braking_detected': bool(trail_braking_detected),
        'brake_steering_overload_pct': round(float(overload_pct), 1)
    }


def compare_brake_zones(current_zones, reference_zones):
    """
    Match and compare brake zones between current and reference laps
    
    Returns:
        List of comparisons
    """
    comparisons = []
    
    # Match zones by lap distance (within 5%)
    for curr_zone in current_zones:
        curr_start = curr_zone['analysis']['lap_distance_start_pct']
        
        # Find matching reference zone
        best_match = None
        min_distance = float('inf')
        
        for ref_zone in reference_zones:
            ref_start = ref_zone['analysis']['lap_distance_start_pct']
            distance = abs(curr_start - ref_start)
            
            if distance < min_distance and distance < 5.0:  # Within 5% lap distance
                best_match = ref_zone
                min_distance = distance
        
        if best_match:
            curr_analysis = curr_zone['analysis']
            ref_analysis = best_match['analysis']
            
            comparisons.append({
                'zone_number': len(comparisons) + 1,
                'lap_distance_pct': curr_start,
                'current': curr_analysis,
                'reference': ref_analysis,
                'differences': {
                    'max_pressure_diff': round(curr_analysis['max_pressure'] - ref_analysis['max_pressure'], 3),
                    'duration_diff': round(curr_analysis['duration_seconds'] - ref_analysis['duration_seconds'], 2),
                    'smoothness_diff': round(curr_analysis['release_smoothness'] - ref_analysis['release_smoothness'], 4),
                    'max_steering_diff_rad': round(curr_analysis['max_steering_angle_rad'] - ref_analysis['max_steering_angle_rad'], 3),
                    'overload_diff_pct': round(curr_analysis['brake_steering_overload_pct'] - ref_analysis['brake_steering_overload_pct'], 1)
                }
            })
    
    return comparisons


def analyze_braking_technique(current_lap_path, reference_lap_path=None):
    """
    Main analysis function
    
    Returns:
        Dictionary with complete braking analysis
    """
    # Load current lap
    current_df = load_telemetry(current_lap_path)
    current_brake_zones = detect_brake_zones(current_df)
    
    # Analyze current lap brake zones
    current_analyzed = []
    for zone in current_brake_zones:
        analysis = analyze_brake_zone(current_df, zone)
        current_analyzed.append({
            'zone_number': len(current_analyzed) + 1,
            'analysis': analysis
        })
    
    result = {
        'current_lap': {
            'file': str(current_lap_path),
            'total_brake_zones': len(current_analyzed),
            'brake_zones': current_analyzed
        }
    }
    
    # Compare with reference if provided
    if reference_lap_path:
        reference_df = load_telemetry(reference_lap_path)
        reference_brake_zones = detect_brake_zones(reference_df)
        
        reference_analyzed = []
        for zone in reference_brake_zones:
            analysis = analyze_brake_zone(reference_df, zone)
            reference_analyzed.append({
                'zone_number': len(reference_analyzed) + 1,
                'analysis': analysis
            })
        
        result['reference_lap'] = {
            'file': str(reference_lap_path),
            'total_brake_zones': len(reference_analyzed),
            'brake_zones': reference_analyzed
        }
        
        result['comparison'] = compare_brake_zones(current_analyzed, reference_analyzed)
    
    return result


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_braking_technique.py <current_lap.csv> [reference_lap.csv]")
        sys.exit(1)
    
    current_lap = sys.argv[1]
    reference_lap = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Run analysis
    result = analyze_braking_technique(current_lap, reference_lap)
    
    # Output JSON
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

