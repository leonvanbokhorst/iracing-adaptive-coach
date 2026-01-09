#!/usr/bin/env python3
"""
Coach Tool: Brake Point Drift Detector (FACTS with CONTEXT)

Analyzes lap-to-lap consistency of brake application points.
Shows if brake points move around (inconsistent) or are locked in.

Key insight: You might have consistent LAP TIMES but inconsistent TECHNIQUE.
This tool exposes whether you're braking in the same spot every lap.

Detection method:
1. For each corner zone, scan BACKWARDS from corner entry
2. Find where brake pressure first exceeds threshold (10%)
3. Record track position and speed at that point
4. Compare across laps

Usage:
    python tools/coach/detect_brake_point_drift.py <telemetry.ibt> --track oschersleben-gp
    python tools/coach/detect_brake_point_drift.py <telemetry.ibt> --track oschersleben-gp --threshold 0.15

Output: JSON with brake point consistency per corner
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
    boundaries = [0]
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def find_brake_point_for_corner(
    corner_start_pct: float,
    lap_start_idx: int,
    lap_end_idx: int,
    dist_data: list,
    brake_data: list,
    speed_data: list,
    brake_threshold: float = 0.10,
    search_window_pct: float = 0.15
) -> Optional[dict]:
    """
    Find brake application point before a corner.
    
    Searches backwards from corner entry to find where braking starts.
    
    Args:
        corner_start_pct: Track position where corner begins (0-1)
        lap_start_idx: Sample index where this lap starts
        lap_end_idx: Sample index where this lap ends
        dist_data: LapDistPct data
        brake_data: Brake pedal data (0-1)
        speed_data: Speed data (m/s)
        brake_threshold: Minimum brake pressure to count as "braking" (0.10 = 10%)
        search_window_pct: How far before corner to search (0.15 = 15% of track)
    
    Returns:
        Dict with brake point info, or None if not found
    """
    # Define search zone: from (corner_start - window) to corner_start
    search_start_pct = corner_start_pct - search_window_pct
    
    # Handle wraparound (corner near start/finish)
    if search_start_pct < 0:
        search_start_pct += 1.0
    
    # Find samples in search zone
    search_samples = []
    for i in range(lap_start_idx, lap_end_idx):
        pct = dist_data[i]
        # Handle wraparound case
        if search_start_pct > corner_start_pct:
            # Corner is near start/finish, search zone wraps
            if pct >= search_start_pct or pct <= corner_start_pct:
                search_samples.append(i)
        else:
            # Normal case
            if search_start_pct <= pct <= corner_start_pct:
                search_samples.append(i)
    
    if len(search_samples) < 5:
        return None  # Not enough data
    
    # Sort by track position (ascending)
    search_samples.sort(key=lambda i: dist_data[i] if dist_data[i] > 0.5 or corner_start_pct < 0.5 
                        else dist_data[i] + 1)
    
    # Find first sample where brake exceeds threshold
    brake_start_idx = None
    for i in search_samples:
        if brake_data[i] >= brake_threshold:
            brake_start_idx = i
            break
    
    if brake_start_idx is None:
        # No braking found
        return {
            "brake_start_pct": None,
            "speed_at_brake_kmh": None,
            "max_brake_pressure": round(max(brake_data[i] for i in search_samples), 3),
            "no_braking": True,
        }
    
    # Find peak brake pressure in the zone
    corner_samples = [i for i in range(lap_start_idx, lap_end_idx) 
                      if corner_start_pct - 0.02 <= dist_data[i] <= corner_start_pct + 0.10]
    max_brake = max((brake_data[i] for i in corner_samples), default=0)
    
    return {
        "brake_start_pct": round(dist_data[brake_start_idx], 5),
        "speed_at_brake_kmh": round(speed_data[brake_start_idx] * 3.6, 1),
        "speed_at_brake_ms": round(speed_data[brake_start_idx], 2),
        "max_brake_pressure": round(max_brake, 3),
        "no_braking": False,
    }


def detect_brake_point_drift(
    ibt_path: str, 
    track_id: str, 
    brake_threshold: float = 0.10
) -> dict:
    """
    Detect brake point consistency for all corners.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID for loading corner definitions
        brake_threshold: Minimum brake pressure to count as braking (0-1)
        
    Returns:
        JSON-serializable dict with brake point analysis
    """
    # Load track data
    track_data = load_track_data(track_id)
    if not track_data:
        return {"error": f"Track data not found for: {track_id}"}
    
    if "turn" not in track_data or not track_data["turn"]:
        return {"error": f"No corner definitions in track data for: {track_id}"}
    
    track_length = track_data.get("length", 3600)
    
    # Open IBT file
    ibt = IBT()
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    required = ["LapDistPct", "Brake", "Speed"]
    for ch in required:
        if ch not in available:
            ibt.close()
            return {"error": f"Required channel '{ch}' not found in IBT file"}
    
    # Extract data
    dist_data = ibt.get_all("LapDistPct")
    brake_data = ibt.get_all("Brake")
    speed_data = ibt.get_all("Speed")
    
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
        corner_start = turn["start"]
        
        brake_points = []
        
        # Analyze each lap
        for lap_idx in range(len(lap_boundaries) - 1):
            lap_number = lap_idx + 1
            lap_start = lap_boundaries[lap_idx]
            lap_end = lap_boundaries[lap_idx + 1]
            
            bp_data = find_brake_point_for_corner(
                corner_start,
                lap_start, lap_end,
                dist_data, brake_data, speed_data,
                brake_threshold
            )
            
            if bp_data and not bp_data.get("no_braking"):
                bp_data["lap"] = lap_number
                brake_points.append(bp_data)
        
        # Calculate consistency metrics
        if len(brake_points) >= 2:
            positions = [bp["brake_start_pct"] for bp in brake_points]
            speeds = [bp["speed_at_brake_kmh"] for bp in brake_points]
            pressures = [bp["max_brake_pressure"] for bp in brake_points]
            
            pos_sigma = statistics.stdev(positions)
            pos_sigma_m = pos_sigma * track_length
            pos_range = max(positions) - min(positions)
            pos_range_m = pos_range * track_length
            
            speed_sigma = statistics.stdev(speeds)
            
            consistency = {
                "sigma_track_pct": round(pos_sigma, 5),
                "sigma_meters": round(pos_sigma_m, 1),
                "drift_range_pct": round(pos_range, 5),
                "drift_range_m": round(pos_range_m, 1),
                "speed_sigma_kmh": round(speed_sigma, 1),
                "avg_brake_pressure": round(statistics.mean(pressures), 3),
                "max_brake_pressure": round(max(pressures), 3),
                "laps_analyzed": len(brake_points),
            }
            
            # Find earliest and latest brake points
            earliest = min(brake_points, key=lambda x: x["brake_start_pct"])
            latest = max(brake_points, key=lambda x: x["brake_start_pct"])
            consistency["earliest_brake_lap"] = earliest["lap"]
            consistency["latest_brake_lap"] = latest["lap"]
            consistency["earliest_brake_m_before_corner"] = round(
                (corner_start - earliest["brake_start_pct"]) * track_length, 1
            )
            consistency["latest_brake_m_before_corner"] = round(
                (corner_start - latest["brake_start_pct"]) * track_length, 1
            )
            
        elif len(brake_points) == 1:
            consistency = {
                "laps_analyzed": 1,
            }
        else:
            # No braking detected
            consistency = {
                "laps_analyzed": 0,
            }
        
        corners[corner_name] = {
            "corner_start_pct": corner_start,
            "brake_points": brake_points,
            "consistency": consistency,
        }
        
        # Add average metrics if we have data
        if brake_points:
            corners[corner_name]["avg_brake_point_pct"] = round(
                statistics.mean(bp["brake_start_pct"] for bp in brake_points), 5
            )
            corners[corner_name]["avg_brake_point_m_before_corner"] = round(
                (corner_start - corners[corner_name]["avg_brake_point_pct"]) * track_length, 1
            )
            corners[corner_name]["avg_speed_at_brake_kmh"] = round(
                statistics.mean(bp["speed_at_brake_kmh"] for bp in brake_points), 1
            )
    
    ibt.close()
    
    # Build summary
    total_corners = len([c for c in corners.values() if c["consistency"]["laps_analyzed"] > 0])
    
    result = {
        "metadata": {
            "file": Path(ibt_path).name,
            "track": track_data["name"],
            "track_id": track_id,
            "track_length_m": track_length,
            "brake_threshold": brake_threshold,
            "laps_found": len(lap_boundaries) - 1,
        },
        "summary": {
            "braking_corners_analyzed": total_corners,
        },
        "corners": corners,
    }
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Detect brake point drift from IBT telemetry")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, required=True,
                        help="Track ID (e.g., oschersleben-gp)")
    parser.add_argument("--threshold", type=float, default=0.10,
                        help="Brake pressure threshold (0-1, default 0.10)")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = detect_brake_point_drift(ibt_path, args.track, args.threshold)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()
