#!/usr/bin/env python3
"""
Coach Tool: Input Smoothness Analyzer (FACTS with CONTEXT)

Measures how smooth or jerky the driver's inputs are.
Smooth inputs = faster, more consistent, better tire life.
Jerky inputs = slow, inconsistent, wears tires.

Analysis includes:
1. Steering jerk - How abruptly steering changes (rad/s²)
2. Throttle smoothness - Ramp-up consistency (%/s)
3. Brake smoothness - Application and release patterns (%/s)

Key insight: "Gong uses 92.3% brake vs your 75.8%" - but is it confidence
or smoothness that differs? This tool answers that question.

Usage:
    python tools/coach/analyze_input_smoothness.py <telemetry.ibt>
    python tools/coach/analyze_input_smoothness.py <telemetry.ibt> --track oschersleben-gp

Output: JSON with input smoothness metrics
"""

import sys
import json
import argparse
import statistics
from pathlib import Path
from typing import Optional
import math

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for corner-specific analysis."""
    track_file = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_file.exists():
        with open(track_file) as f:
            return json.load(f)
    return None


def find_lap_boundaries(dist_data: list) -> list:
    """Find lap boundaries by detecting LapDistPct crossing."""
    boundaries = [0]
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def calculate_derivative(data: list, tick_rate: int = 60) -> list:
    """
    Calculate rate of change (derivative) for a data series.
    
    Returns list of rates in units per second.
    """
    if len(data) < 2:
        return []
    
    dt = 1.0 / tick_rate  # Time between samples
    derivatives = []
    
    for i in range(1, len(data)):
        rate = (data[i] - data[i-1]) / dt
        derivatives.append(rate)
    
    return derivatives


def calculate_jerk(data: list, tick_rate: int = 60) -> list:
    """
    Calculate jerk (rate of change of rate of change).
    
    For steering: rad/s² (how abruptly steering velocity changes)
    """
    velocity = calculate_derivative(data, tick_rate)
    jerk = calculate_derivative(velocity, tick_rate)
    return jerk


def analyze_steering_smoothness(
    steering_data: list,
    dist_data: list,
    tick_rate: int,
    track_data: Optional[dict] = None
) -> dict:
    """Analyze steering input smoothness."""
    
    # Calculate steering velocity (rad/s) and jerk (rad/s²)
    steering_velocity = calculate_derivative(steering_data, tick_rate)
    steering_jerk = calculate_jerk(steering_data, tick_rate)
    
    if not steering_jerk:
        return {"available": False}
    
    # Use absolute values - we care about magnitude of changes
    abs_velocity = [abs(v) for v in steering_velocity]
    abs_jerk = [abs(j) for j in steering_jerk]
    
    # Overall stats
    avg_jerk = statistics.mean(abs_jerk)
    max_jerk = max(abs_jerk)
    jerk_sigma = statistics.stdev(abs_jerk) if len(abs_jerk) > 1 else 0
    
    result = {
        "available": True,
        "avg_jerk_rad_s2": round(avg_jerk, 2),
        "max_jerk_rad_s2": round(max_jerk, 2),
        "jerk_sigma": round(jerk_sigma, 2),
        "avg_velocity_rad_s": round(statistics.mean(abs_velocity), 2),
        "max_velocity_rad_s": round(max(abs_velocity), 2),
        "max_steering_angle_rad": round(max(abs(s) for s in steering_data), 3),
    }
    
    # Per-corner jerk data
    if track_data and "turn" in track_data and dist_data:
        corner_jerk = {}
        for turn in track_data["turn"]:
            name = turn["name"]
            start = turn["start"]
            end = turn["end"]
            
            # Get jerk values in this corner zone
            zone_jerks = []
            for i, j in enumerate(abs_jerk):
                if i < len(dist_data) and start <= dist_data[i] <= end:
                    zone_jerks.append(j)
            
            if zone_jerks:
                corner_jerk[name] = {
                    "avg_jerk": round(statistics.mean(zone_jerks), 2),
                    "max_jerk": round(max(zone_jerks), 2),
                }
        
        result["per_corner"] = corner_jerk
    
    return result


def analyze_throttle_smoothness(
    throttle_data: list,
    dist_data: list,
    tick_rate: int,
    track_data: Optional[dict] = None
) -> dict:
    """Analyze throttle input smoothness."""
    
    # Convert to percentage (0-100)
    throttle_pct = [t * 100 for t in throttle_data]
    
    # Calculate throttle velocity (%/s) and jerk (%/s²)
    throttle_velocity = calculate_derivative(throttle_pct, tick_rate)
    throttle_jerk = calculate_jerk(throttle_pct, tick_rate)
    
    if not throttle_jerk:
        return {"available": False}
    
    abs_velocity = [abs(v) for v in throttle_velocity]
    abs_jerk = [abs(j) for j in throttle_jerk]
    
    # Separate positive (application) and negative (lift) velocities
    application_rates = [v for v in throttle_velocity if v > 0]
    lift_rates = [abs(v) for v in throttle_velocity if v < 0]
    
    avg_jerk = statistics.mean(abs_jerk)
    
    result = {
        "available": True,
        "avg_jerk_pct_s2": round(avg_jerk, 1),
        "max_jerk_pct_s2": round(max(abs_jerk), 1),
        "avg_application_rate_pct_s": round(statistics.mean(application_rates), 1) if application_rates else 0,
        "avg_lift_rate_pct_s": round(statistics.mean(lift_rates), 1) if lift_rates else 0,
        "max_application_rate_pct_s": round(max(application_rates), 1) if application_rates else 0,
        "max_throttle_pct": round(max(throttle_pct), 1),
        "avg_throttle_pct": round(statistics.mean(throttle_pct), 1),
        "full_throttle_usage_pct": round(sum(1 for t in throttle_pct if t > 95) / len(throttle_pct) * 100, 1),
    }
    
    # Per-corner analysis
    if track_data and "turn" in track_data and dist_data:
        corner_throttle = {}
        for turn in track_data["turn"]:
            name = turn["name"]
            start = turn["start"]
            end = turn["end"]
            
            # Get application rates in corner exit zone (last 50% of corner)
            exit_start = start + (end - start) * 0.5
            zone_apps = []
            for i, v in enumerate(throttle_velocity):
                if i < len(dist_data) and exit_start <= dist_data[i] <= end:
                    if v > 10:  # Only count significant throttle applications
                        zone_apps.append(v)
            
            if zone_apps:
                corner_throttle[name] = {
                    "avg_application_rate": round(statistics.mean(zone_apps), 1),
                    "max_application_rate": round(max(zone_apps), 1),
                }
        
        result["per_corner_exit"] = corner_throttle
    
    return result


def analyze_brake_smoothness(
    brake_data: list,
    dist_data: list,
    tick_rate: int,
    track_data: Optional[dict] = None
) -> dict:
    """Analyze brake input smoothness."""
    
    # Convert to percentage (0-100)
    brake_pct = [b * 100 for b in brake_data]
    
    # Calculate brake velocity (%/s) and jerk (%/s²)
    brake_velocity = calculate_derivative(brake_pct, tick_rate)
    brake_jerk = calculate_jerk(brake_pct, tick_rate)
    
    if not brake_jerk:
        return {"available": False}
    
    abs_velocity = [abs(v) for v in brake_velocity]
    abs_jerk = [abs(j) for j in brake_jerk]
    
    # Separate application (positive) and release (negative)
    application_rates = [v for v in brake_velocity if v > 0]
    release_rates = [abs(v) for v in brake_velocity if v < 0]
    
    avg_jerk = statistics.mean(abs_jerk)
    
    result = {
        "available": True,
        "avg_jerk_pct_s2": round(avg_jerk, 1),
        "max_jerk_pct_s2": round(max(abs_jerk), 1),
        "avg_application_rate_pct_s": round(statistics.mean(application_rates), 1) if application_rates else 0,
        "avg_release_rate_pct_s": round(statistics.mean(release_rates), 1) if release_rates else 0,
        "max_application_rate_pct_s": round(max(application_rates), 1) if application_rates else 0,
        "max_brake_pct": round(max(brake_pct), 1),
        "avg_brake_pct_when_braking": round(
            statistics.mean(b for b in brake_pct if b > 5), 1
        ) if any(b > 5 for b in brake_pct) else 0,
    }
    
    # Per-corner analysis
    if track_data and "turn" in track_data and dist_data:
        corner_brake = {}
        for turn in track_data["turn"]:
            name = turn["name"]
            start = turn["start"]
            
            # Look at braking zone before corner (15% of track before)
            brake_zone_start = start - 0.15
            if brake_zone_start < 0:
                brake_zone_start += 1.0
            
            # Get brake data in this zone
            zone_brakes = []
            zone_releases = []
            for i, v in enumerate(brake_velocity):
                if i >= len(dist_data):
                    continue
                pct = dist_data[i]
                # Handle wraparound
                if brake_zone_start > start:
                    in_zone = pct >= brake_zone_start or pct <= start
                else:
                    in_zone = brake_zone_start <= pct <= start
                
                if in_zone:
                    if v > 10:
                        zone_brakes.append(v)
                    elif v < -10:
                        zone_releases.append(abs(v))
            
            if zone_brakes or zone_releases:
                corner_brake[name] = {
                    "avg_application_rate": round(statistics.mean(zone_brakes), 1) if zone_brakes else None,
                    "avg_release_rate": round(statistics.mean(zone_releases), 1) if zone_releases else None,
                }
        
        result["per_corner_entry"] = corner_brake
    
    return result


def analyze_input_smoothness(ibt_path: str, track_id: Optional[str] = None) -> dict:
    """
    Full input smoothness analysis from IBT file.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Optional track ID for corner-specific analysis
        
    Returns:
        JSON-serializable dict with smoothness analysis
    """
    # Load track data if provided
    track_data = load_track_data(track_id) if track_id else None
    
    # Open IBT file
    ibt = IBT()
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    
    # Extract data
    dist_data = ibt.get_all("LapDistPct") if "LapDistPct" in available else None
    steering_data = ibt.get_all("SteeringWheelAngle") if "SteeringWheelAngle" in available else None
    throttle_data = ibt.get_all("Throttle") if "Throttle" in available else None
    brake_data = ibt.get_all("Brake") if "Brake" in available else None
    
    sample_count = len(dist_data) if dist_data else 0
    
    # Find lap count
    lap_count = 0
    if dist_data:
        boundaries = find_lap_boundaries(dist_data)
        lap_count = len(boundaries) - 1
    
    result = {
        "metadata": {
            "file": Path(ibt_path).name,
            "track": track_data["name"] if track_data else None,
            "track_id": track_id,
            "sample_rate_hz": tick_rate,
            "total_samples": sample_count,
            "duration_seconds": round(sample_count / tick_rate, 1),
            "laps_found": lap_count,
        },
        "steering": {},
        "throttle": {},
        "brake": {},
    }
    
    # Analyze each input
    if steering_data:
        result["steering"] = analyze_steering_smoothness(
            steering_data, dist_data, tick_rate, track_data
        )
    else:
        result["steering"] = {"available": False, "reason": "SteeringWheelAngle channel not found"}
    
    if throttle_data:
        result["throttle"] = analyze_throttle_smoothness(
            throttle_data, dist_data, tick_rate, track_data
        )
    else:
        result["throttle"] = {"available": False, "reason": "Throttle channel not found"}
    
    if brake_data:
        result["brake"] = analyze_brake_smoothness(
            brake_data, dist_data, tick_rate, track_data
        )
    else:
        result["brake"] = {"available": False, "reason": "Brake channel not found"}
    
    ibt.close()
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Analyze input smoothness from IBT telemetry")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, help="Track ID for corner-specific analysis")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = analyze_input_smoothness(ibt_path, args.track)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()
