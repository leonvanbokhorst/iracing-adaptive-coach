#!/usr/bin/env python3
"""
Core Tool: Extract Session Data from IBT

Extracts complete session structure from iRacing IBT telemetry files.
Provides lap times, sector times, and session statistics - replacing
the need for G61 session CSV exports.

Usage:
    python tools/core/extract_session_from_ibt.py <telemetry.ibt>
    python tools/core/extract_session_from_ibt.py <telemetry.ibt> --track oschersleben-gp

Output: JSON with full session breakdown
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional
import statistics

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for sector markers and corner info."""
    track_file = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_file.exists():
        with open(track_file) as f:
            return json.load(f)
    return None


def detect_car_from_filename(filename: str) -> str:
    """Detect car name from IBT filename."""
    filename_lower = filename.lower()
    if "raygr" in filename_lower:
        return "Ray FF1600"
    elif "mx5" in filename_lower or "mx-5" in filename_lower:
        return "Mazda MX-5"
    elif "skipbarber" in filename_lower:
        return "Skip Barber Formula"
    # Add more cars as needed
    return "Unknown"


def find_lap_boundaries(dist_data: list) -> list:
    """
    Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0.
    
    Returns list of sample indices where new laps start.
    """
    boundaries = []
    for i in range(1, len(dist_data)):
        # Detect crossing: previous sample > 0.9, current sample < 0.1
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def calculate_sector_times(
    start_idx: int, 
    end_idx: int, 
    dist_data: list, 
    session_time: list,
    sector_markers: list
) -> dict:
    """
    Calculate sector times for a lap using track sector markers.
    
    sector_markers: list of dicts with "marker" (0-1 track position) and "name"
    """
    sectors = {}
    
    # Sort markers by position
    sorted_markers = sorted(sector_markers, key=lambda x: x["marker"])
    
    # Find time at each sector boundary
    sector_times = []
    prev_marker = 0.0
    prev_time = session_time[start_idx]
    
    for marker_info in sorted_markers:
        marker_pos = marker_info["marker"]
        marker_name = marker_info["name"]
        
        # Find sample closest to this marker position
        best_idx = None
        best_diff = float('inf')
        
        for i in range(start_idx, end_idx):
            diff = abs(dist_data[i] - marker_pos)
            if diff < best_diff:
                best_diff = diff
                best_idx = i
        
        if best_idx is not None:
            sector_time = session_time[best_idx] - prev_time
            sectors[f"S{marker_name}"] = round(sector_time, 3)
            prev_time = session_time[best_idx]
    
    return sectors


def calculate_corner_times(
    start_idx: int,
    end_idx: int,
    dist_data: list,
    session_time: list,
    turns: list
) -> dict:
    """
    Calculate time spent in each corner.
    
    Returns dict of corner_name -> time_in_corner
    """
    corners = {}
    
    for turn in turns:
        turn_start = turn["start"]
        turn_end = turn["end"]
        turn_name = turn["name"]
        
        # Find entry and exit times
        entry_time = None
        exit_time = None
        
        for i in range(start_idx, end_idx):
            if entry_time is None and dist_data[i] >= turn_start:
                entry_time = session_time[i]
            if dist_data[i] >= turn_end:
                exit_time = session_time[i]
                break
        
        if entry_time is not None and exit_time is not None:
            corners[turn_name] = round(exit_time - entry_time, 3)
    
    return corners


def is_valid_lap(lap_time: float, expected_range: tuple = (60, 180)) -> bool:
    """Check if lap time is within valid range (not outlap/inlap)."""
    return expected_range[0] < lap_time < expected_range[1]


def is_outlap(lap_number: int, lap_time: float, all_lap_times: list) -> bool:
    """
    Detect if a lap is an outlap (first lap, significantly slower than session pace).
    
    Criteria:
    - Must be lap 1 (first lap is almost always outlap in practice)
    - Must be significantly slower than the median of other laps (>1.5s slower)
    """
    if lap_number != 1:
        return False
    
    if len(all_lap_times) < 3:
        return False  # Not enough data to determine
    
    # Get median of laps 2+ (excluding potential outlap)
    other_laps = all_lap_times[1:]  # Skip first lap
    if not other_laps:
        return False
    
    median_time = sorted(other_laps)[len(other_laps) // 2]
    
    # If lap 1 is more than 1.5s slower than median, it's an outlap
    return lap_time > median_time + 1.5


def extract_session(ibt_path: str, track_id: Optional[str] = None) -> dict:
    """
    Extract complete session data from IBT file.
    
    Returns structured session data with all laps, sectors, and statistics.
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    # Get filename for car detection
    filename = Path(ibt_path).name
    
    # Load track data if provided
    track_data = load_track_data(track_id) if track_id else None
    
    # Extract required channels
    available = set(ibt.var_headers_names or [])
    
    required_channels = ["LapDistPct", "SessionTime"]
    for ch in required_channels:
        if ch not in available:
            ibt.close()
            return {"error": f"Required channel '{ch}' not found in IBT file"}
    
    dist_data = ibt.get_all("LapDistPct")
    session_time = ibt.get_all("SessionTime")
    
    # Get sample rate
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    sample_count = len(dist_data)
    
    # Find lap boundaries
    lap_boundaries = find_lap_boundaries(dist_data)
    
    if len(lap_boundaries) < 2:
        ibt.close()
        return {"error": "Not enough complete laps found in session"}
    
    # First pass: extract all lap times to detect outlaps
    raw_lap_times = []
    for i in range(len(lap_boundaries) - 1):
        start_idx = lap_boundaries[i]
        end_idx = lap_boundaries[i + 1]
        lap_time = session_time[end_idx] - session_time[start_idx]
        if is_valid_lap(lap_time):
            raw_lap_times.append(lap_time)
    
    # Extract each lap (second pass with outlap detection)
    laps = []
    all_lap_times = []  # Only flying laps (excludes outlaps)
    all_sector_times = {f"S{s['name']}": [] for s in track_data.get("sector", [])} if track_data else {}
    all_corner_times = {t["name"]: [] for t in track_data.get("turn", [])} if track_data else {}
    
    for i in range(len(lap_boundaries) - 1):
        start_idx = lap_boundaries[i]
        end_idx = lap_boundaries[i + 1]
        
        lap_time = session_time[end_idx] - session_time[start_idx]
        lap_number = i + 1
        
        # Check if this is an outlap
        outlap_detected = is_outlap(lap_number, lap_time, raw_lap_times)
        
        lap_data = {
            "lap_number": lap_number,
            "lap_time": round(lap_time, 3),
            "lap_time_formatted": f"{int(lap_time // 60)}:{lap_time % 60:06.3f}",
            "start_idx": start_idx,
            "end_idx": end_idx,
            "samples": end_idx - start_idx,
            "valid": is_valid_lap(lap_time),
            "is_outlap": outlap_detected,
        }
        
        # For statistics, only include valid NON-outlap laps (flying laps)
        include_in_stats = lap_data["valid"] and not outlap_detected
        
        # Calculate sector times if track data available
        if track_data and "sector" in track_data:
            sectors = calculate_sector_times(
                start_idx, end_idx, dist_data, session_time, track_data["sector"]
            )
            lap_data["sectors"] = sectors
            
            # Collect for statistics (only flying laps)
            if include_in_stats:
                for sector_name, sector_time in sectors.items():
                    if sector_name in all_sector_times:
                        all_sector_times[sector_name].append(sector_time)
        
        # Calculate corner times if track data available
        if track_data and "turn" in track_data:
            corners = calculate_corner_times(
                start_idx, end_idx, dist_data, session_time, track_data["turn"]
            )
            lap_data["corners"] = corners
            
            # Collect for statistics (only flying laps)
            if include_in_stats:
                for corner_name, corner_time in corners.items():
                    if corner_name in all_corner_times:
                        all_corner_times[corner_name].append(corner_time)
        
        laps.append(lap_data)
        
        if include_in_stats:
            all_lap_times.append(lap_time)
    
    # Calculate session statistics
    valid_laps = [l for l in laps if l["valid"]]
    flying_laps = [l for l in laps if l["valid"] and not l.get("is_outlap", False)]
    outlap_laps = [l for l in laps if l.get("is_outlap", False)]
    
    if not valid_laps:
        ibt.close()
        return {"error": "No valid laps found in session"}
    
    # Best lap from flying laps only (or valid laps if no flying laps detected)
    laps_for_stats = flying_laps if flying_laps else valid_laps
    best_lap = min(laps_for_stats, key=lambda x: x["lap_time"])
    
    # Calculate theoretical optimal (sum of best sectors)
    theoretical_optimal = None
    if all_sector_times:
        sector_bests = {}
        for sector_name, times in all_sector_times.items():
            if times:
                sector_bests[sector_name] = min(times)
        if sector_bests:
            theoretical_optimal = sum(sector_bests.values())
    
    # Sector statistics
    sector_stats = {}
    for sector_name, times in all_sector_times.items():
        if times:
            sector_stats[sector_name] = {
                "best": round(min(times), 3),
                "worst": round(max(times), 3),
                "avg": round(statistics.mean(times), 3),
                "sigma": round(statistics.stdev(times), 3) if len(times) > 1 else 0.0,
                "loss_per_lap": round(statistics.mean(times) - min(times), 3),
            }
    
    # Corner statistics
    corner_stats = {}
    for corner_name, times in all_corner_times.items():
        if times:
            corner_stats[corner_name] = {
                "best": round(min(times), 3),
                "worst": round(max(times), 3),
                "avg": round(statistics.mean(times), 3),
                "sigma": round(statistics.stdev(times), 3) if len(times) > 1 else 0.0,
                "variance_rating": classify_variance(statistics.stdev(times) if len(times) > 1 else 0),
            }
    
    # Build result
    result = {
        "metadata": {
            "file": filename,
            "track": track_data["name"] if track_data else None,
            "track_id": track_id,
            "car": detect_car_from_filename(filename),
            "sample_count": sample_count,
            "sample_rate_hz": tick_rate,
            "duration_seconds": round(sample_count / tick_rate, 1),
            "duration_formatted": format_duration(sample_count / tick_rate),
        },
        "summary": {
            "total_laps": len(laps),
            "valid_laps": len(valid_laps),
            "flying_laps": len(flying_laps),
            "outlaps": len(outlap_laps),
            "invalid_laps": len(laps) - len(valid_laps),
            "best_lap_time": round(best_lap["lap_time"], 3),
            "best_lap_time_formatted": best_lap["lap_time_formatted"],
            "best_lap_number": best_lap["lap_number"],
            "worst_flying_lap_time": round(max(l["lap_time"] for l in laps_for_stats), 3) if laps_for_stats else None,
            "avg_lap_time": round(statistics.mean(all_lap_times), 3) if all_lap_times else None,
            "consistency_sigma": round(statistics.stdev(all_lap_times), 3) if len(all_lap_times) > 1 else 0.0,
            "theoretical_optimal": round(theoretical_optimal, 3) if theoretical_optimal else None,
            "gap_to_optimal": round(best_lap["lap_time"] - theoretical_optimal, 3) if theoretical_optimal else None,
        },
        "laps": laps,
        "sectors": sector_stats,
        "corners": corner_stats,
    }
    
    ibt.close()
    return result


def classify_variance(sigma: float) -> str:
    """Classify corner variance into coaching categories."""
    if sigma < 0.10:
        return "dialed"  # Very consistent
    elif sigma < 0.25:
        return "solid"   # Good consistency
    elif sigma < 0.40:
        return "work_needed"  # Room for improvement
    else:
        return "lottery"  # Inconsistent - focus area!


def format_duration(seconds: float) -> str:
    """Format duration as MM:SS."""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


def main():
    parser = argparse.ArgumentParser(description="Extract session data from IBT file")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, help="Track ID for sector/corner analysis")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    parser.add_argument("--laps-only", action="store_true", help="Only output lap summary")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = extract_session(ibt_path, args.track)
    
    # Optionally simplify output
    if args.laps_only and "laps" in result:
        result = {
            "summary": result.get("summary"),
            "laps": [
                {
                    "lap": l["lap_number"],
                    "time": l["lap_time_formatted"],
                    "valid": l["valid"]
                }
                for l in result["laps"]
            ]
        }
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()

