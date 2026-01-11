#!/usr/bin/env python3
"""
Coach Tool: Apex Point Detector (FACTS with CONTEXT)

Dynamically detects where the driver apexes each corner, lap-by-lap.
Uses telemetry to find the actual driving apex rather than relying on
static track data.

Detection methods:
1. Minimum speed point - Where you're slowest = driving apex
2. Peak lateral G point - Maximum cornering load
3. Maximum steering angle - Deepest into the corner

Usage:
    python tools/coach/detect_apex_points.py <telemetry.ibt> --track oschersleben-gp
    python tools/coach/detect_apex_points.py <telemetry.ibt> --track oschersleben-gp --lap 5

Output: JSON with apex positions per corner per lap
"""

import sys
import json
import argparse
import statistics
from pathlib import Path
from typing import Optional

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


# Constants
G = 9.80665  # m/s^2


def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for corner definitions."""
    track_file = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_file.exists():
        with open(track_file) as f:
            return json.load(f)
    return None


def find_lap_boundaries(dist_data: list) -> list:
    """
    Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0.
    Returns list of sample indices where new laps start.
    """
    boundaries = [0]  # Start from beginning
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def find_apex_in_zone(
    start_pct: float,
    end_pct: float,
    lap_start_idx: int,
    lap_end_idx: int,
    dist_data: list,
    speed_data: list,
    lat_accel_data: Optional[list],
    steering_data: Optional[list],
    tick_rate: int = 60
) -> Optional[dict]:
    """
    Find apex point within a corner zone for a single lap.
    
    Returns dict with apex position and metrics, or None if zone not found.
    """
    # Find samples within this corner zone for this lap
    zone_samples = []
    for i in range(lap_start_idx, lap_end_idx):
        if start_pct <= dist_data[i] <= end_pct:
            zone_samples.append(i)
    
    if len(zone_samples) < 3:
        return None  # Not enough data in zone
    
    # Method 1: Minimum speed (primary apex indicator)
    min_speed_idx = min(zone_samples, key=lambda i: speed_data[i])
    min_speed = speed_data[min_speed_idx]
    apex_pct = dist_data[min_speed_idx]
    
    # Method 2: Peak lateral G (if available)
    peak_lat_g = None
    peak_lat_g_pct = None
    if lat_accel_data:
        # Use absolute value - cornering either direction
        peak_lat_g_idx = max(zone_samples, key=lambda i: abs(lat_accel_data[i]))
        peak_lat_g = abs(lat_accel_data[peak_lat_g_idx]) / G
        peak_lat_g_pct = dist_data[peak_lat_g_idx]
    
    # Method 3: Maximum steering angle (if available)
    max_steering = None
    max_steering_pct = None
    if steering_data:
        # Use absolute value - steering either direction
        max_steering_idx = max(zone_samples, key=lambda i: abs(steering_data[i]))
        max_steering = abs(steering_data[max_steering_idx])  # radians
        max_steering_pct = dist_data[max_steering_idx]
    
    return {
        "apex_pct": round(apex_pct, 4),
        "min_speed_kmh": round(min_speed * 3.6, 1),
        "min_speed_pct": round(dist_data[min_speed_idx], 4),
        "peak_lat_g": round(peak_lat_g, 2) if peak_lat_g else None,
        "peak_lat_g_pct": round(peak_lat_g_pct, 4) if peak_lat_g_pct else None,
        "max_steering_rad": round(max_steering, 3) if max_steering else None,
        "max_steering_pct": round(max_steering_pct, 4) if max_steering_pct else None,
        "samples_in_zone": len(zone_samples),
    }


def detect_apex_points(ibt_path: str, track_id: str, specific_lap: Optional[int] = None) -> dict:
    """
    Detect apex points for all corners across all laps.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID for loading corner definitions
        specific_lap: Optional - analyze only this lap number
        
    Returns:
        JSON-serializable dict with apex analysis
    """
    # Load track data
    track_data = load_track_data(track_id)
    if not track_data:
        return {"error": f"Track data not found for: {track_id}"}
    
    if "turn" not in track_data or not track_data["turn"]:
        return {"error": f"No corner definitions in track data for: {track_id}"}
    
    track_length = track_data.get("length", 3600)  # Default 3.6km
    
    # Open IBT file
    ibt = IBT()
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    required = ["LapDistPct", "Speed"]
    for ch in required:
        if ch not in available:
            ibt.close()
            return {"error": f"Required channel '{ch}' not found in IBT file"}
    
    # Extract data
    dist_data = ibt.get_all("LapDistPct")
    speed_data = ibt.get_all("Speed")
    lat_accel_data = ibt.get_all("LatAccel") if "LatAccel" in available else None
    steering_data = ibt.get_all("SteeringWheelAngle") if "SteeringWheelAngle" in available else None
    
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    sample_count = len(dist_data)
    
    # Find lap boundaries
    lap_boundaries = find_lap_boundaries(dist_data)
    
    if len(lap_boundaries) < 2:
        ibt.close()
        return {"error": "Not enough complete laps found"}
    
    # Analyze each corner
    corners = {}
    
    for turn in track_data["turn"]:
        corner_name = turn["name"]
        start_pct = turn["start"]
        end_pct = turn["end"]
        
        corner_laps = []
        
        # Analyze each lap
        for lap_idx in range(len(lap_boundaries) - 1):
            lap_number = lap_idx + 1
            
            # Skip if specific lap requested and this isn't it
            if specific_lap and lap_number != specific_lap:
                continue
            
            lap_start = lap_boundaries[lap_idx]
            lap_end = lap_boundaries[lap_idx + 1]
            
            apex_data = find_apex_in_zone(
                start_pct, end_pct,
                lap_start, lap_end,
                dist_data, speed_data,
                lat_accel_data, steering_data,
                tick_rate
            )
            
            if apex_data:
                apex_data["lap"] = lap_number
                corner_laps.append(apex_data)
        
        if not corner_laps:
            continue
        
        # Calculate consistency metrics
        apex_positions = [lap["apex_pct"] for lap in corner_laps]
        min_speeds = [lap["min_speed_kmh"] for lap in corner_laps]
        
        consistency = {}
        if len(apex_positions) > 1:
            apex_sigma = statistics.stdev(apex_positions)
            apex_range = max(apex_positions) - min(apex_positions)
            speed_sigma = statistics.stdev(min_speeds)
            
            consistency = {
                "apex_position_sigma": round(apex_sigma, 5),
                "apex_position_sigma_m": round(apex_sigma * track_length, 1),
                "apex_position_range": round(apex_range, 5),
                "apex_position_range_m": round(apex_range * track_length, 1),
                "min_speed_sigma_kmh": round(speed_sigma, 2),
                "laps_analyzed": len(corner_laps),
            }
            
            # Add best/worst lap info
            best_lap = min(corner_laps, key=lambda x: x["min_speed_kmh"])
            worst_lap = max(corner_laps, key=lambda x: x["min_speed_kmh"])
            consistency["slowest_apex_lap"] = best_lap["lap"]
            consistency["fastest_through_lap"] = worst_lap["lap"]
        else:
            consistency = {
                "laps_analyzed": 1,
            }
        
        corners[corner_name] = {
            "zone": {"start": start_pct, "end": end_pct},
            "laps": corner_laps,
            "consistency": consistency,
            "avg_apex_pct": round(statistics.mean(apex_positions), 4),
            "avg_min_speed_kmh": round(statistics.mean(min_speeds), 1),
        }
    
    ibt.close()
    
    # Build summary
    total_corners = len(corners)
    
    result = {
        "metadata": {
            "file": Path(ibt_path).name,
            "track": track_data["name"],
            "track_id": track_id,
            "track_length_m": track_length,
            "sample_rate_hz": tick_rate,
            "total_samples": sample_count,
            "laps_found": len(lap_boundaries) - 1,
        },
        "summary": {
            "corners_analyzed": total_corners,
        },
        "corners": corners,
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect apex points from IBT telemetry")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, required=True, 
                        help="Track ID (e.g., oschersleben-gp)")
    parser.add_argument("--lap", type=int, help="Analyze specific lap only")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = detect_apex_points(ibt_path, args.track, args.lap)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()
