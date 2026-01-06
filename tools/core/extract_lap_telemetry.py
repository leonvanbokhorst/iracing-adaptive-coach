#!/usr/bin/env python3
"""
Core Tool: Extract Single Lap Telemetry from IBT

Extracts detailed telemetry for a specific lap from an IBT file.
Can export as JSON or CSV for comparison with other laps or alien data.

Usage:
    python tools/core/extract_lap_telemetry.py <telemetry.ibt> --lap 3
    python tools/core/extract_lap_telemetry.py <telemetry.ibt> --lap fastest
    python tools/core/extract_lap_telemetry.py <telemetry.ibt> --lap 3 --csv output.csv

Output: JSON with telemetry arrays or CSV file
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Optional

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


# Channels to extract for lap telemetry
TELEMETRY_CHANNELS = [
    "LapDistPct",           # Track position (0-1)
    "Speed",                # m/s
    "Throttle",             # 0-1
    "Brake",                # 0-1
    "Gear",                 # Gear number
    "RPM",                  # Engine RPM
    "SteeringWheelAngle",   # Radians
    "LatAccel",             # m/s^2
    "LongAccel",            # m/s^2
    "YawRate",              # rad/s
]

# Optional channels (include if available)
OPTIONAL_CHANNELS = [
    "Clutch",
    "VertAccel",
    "Yaw",
    "Pitch",
    "Roll",
]


def find_lap_boundaries(dist_data: list) -> list:
    """Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0."""
    boundaries = []
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def extract_lap_telemetry(
    ibt_path: str, 
    lap_number: int | str = "fastest",
    resample_distance: bool = False,
    distance_step: float = 0.001  # 0.1% track increments
) -> dict:
    """
    Extract telemetry for a specific lap.
    
    Args:
        ibt_path: Path to IBT file
        lap_number: Lap number (1-indexed) or "fastest"
        resample_distance: If True, resample to fixed distance intervals
        distance_step: Distance increment for resampling (0.001 = 0.1% track)
    
    Returns:
        Dict with lap info and telemetry arrays
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    if "LapDistPct" not in available or "SessionTime" not in available:
        ibt.close()
        return {"error": "Required channels (LapDistPct, SessionTime) not found"}
    
    # Get basic data for lap detection
    dist_data = ibt.get_all("LapDistPct")
    session_time = ibt.get_all("SessionTime")
    
    # Find lap boundaries
    lap_boundaries = find_lap_boundaries(dist_data)
    
    if len(lap_boundaries) < 2:
        ibt.close()
        return {"error": "Not enough complete laps found"}
    
    # Calculate lap times to find fastest
    lap_times = []
    for i in range(len(lap_boundaries) - 1):
        start_idx = lap_boundaries[i]
        end_idx = lap_boundaries[i + 1]
        lap_time = session_time[end_idx] - session_time[start_idx]
        lap_times.append({
            "lap_number": i + 1,
            "lap_time": lap_time,
            "start_idx": start_idx,
            "end_idx": end_idx,
            "valid": 60 < lap_time < 180
        })
    
    # Select lap
    valid_laps = [l for l in lap_times if l["valid"]]
    
    if not valid_laps:
        ibt.close()
        return {"error": "No valid laps found"}
    
    if lap_number == "fastest":
        selected_lap = min(valid_laps, key=lambda x: x["lap_time"])
    else:
        lap_num = int(lap_number)
        matching = [l for l in lap_times if l["lap_number"] == lap_num]
        if not matching:
            ibt.close()
            return {"error": f"Lap {lap_num} not found. Available: {[l['lap_number'] for l in lap_times]}"}
        selected_lap = matching[0]
    
    start_idx = selected_lap["start_idx"]
    end_idx = selected_lap["end_idx"]
    lap_time = selected_lap["lap_time"]
    
    # Extract telemetry channels
    telemetry = {}
    channels_extracted = []
    
    for channel in TELEMETRY_CHANNELS + OPTIONAL_CHANNELS:
        if channel in available:
            full_data = ibt.get_all(channel)
            lap_data = full_data[start_idx:end_idx]
            telemetry[channel] = lap_data
            channels_extracted.append(channel)
    
    # Apply unit conversions for human readability
    if "Speed" in telemetry:
        telemetry["Speed_kmh"] = [v * 3.6 for v in telemetry["Speed"]]
    
    if "Throttle" in telemetry:
        telemetry["Throttle_pct"] = [v * 100 for v in telemetry["Throttle"]]
    
    if "Brake" in telemetry:
        telemetry["Brake_pct"] = [v * 100 for v in telemetry["Brake"]]
    
    if "SteeringWheelAngle" in telemetry:
        telemetry["Steering_deg"] = [v * (180 / 3.14159) for v in telemetry["SteeringWheelAngle"]]
    
    if "YawRate" in telemetry:
        telemetry["YawRate_deg_s"] = [v * (180 / 3.14159) for v in telemetry["YawRate"]]
    
    if "LatAccel" in telemetry:
        G = 9.80665
        telemetry["LatAccel_G"] = [v / G for v in telemetry["LatAccel"]]
    
    if "LongAccel" in telemetry:
        G = 9.80665
        telemetry["LongAccel_G"] = [v / G for v in telemetry["LongAccel"]]
    
    # Build result
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    
    result = {
        "lap": {
            "number": selected_lap["lap_number"],
            "time": round(lap_time, 3),
            "time_formatted": f"{int(lap_time // 60)}:{lap_time % 60:06.3f}",
            "samples": end_idx - start_idx,
            "sample_rate_hz": tick_rate,
            "start_idx": start_idx,
            "end_idx": end_idx,
        },
        "available_laps": [
            {
                "lap": l["lap_number"],
                "time": f"{int(l['lap_time'] // 60)}:{l['lap_time'] % 60:06.3f}",
                "valid": l["valid"]
            }
            for l in lap_times
        ],
        "channels_extracted": channels_extracted,
        "telemetry": telemetry,
    }
    
    ibt.close()
    return result


def export_to_csv(result: dict, csv_path: str):
    """Export telemetry to CSV format (similar to G61 format)."""
    import csv
    
    if "error" in result:
        return
    
    telemetry = result["telemetry"]
    samples = result["lap"]["samples"]
    
    # Determine columns (prefer human-readable versions)
    columns = []
    column_map = {
        "LapDistPct": "LapDistPct",
        "Speed_kmh": "Speed",
        "Throttle_pct": "Throttle", 
        "Brake_pct": "Brake",
        "Gear": "Gear",
        "RPM": "RPM",
        "Steering_deg": "SteeringWheelAngle",
        "LatAccel_G": "LatAccel",
        "LongAccel_G": "LongAccel",
        "YawRate_deg_s": "YawRate",
    }
    
    # Use available columns
    for ibt_key, csv_name in column_map.items():
        if ibt_key in telemetry:
            columns.append((ibt_key, csv_name))
    
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([col[1] for col in columns])
        
        # Data rows
        for i in range(samples):
            row = []
            for ibt_key, _ in columns:
                value = telemetry[ibt_key][i]
                row.append(round(value, 6) if isinstance(value, float) else value)
            writer.writerow(row)
    
    print(json.dumps({"success": f"Exported {samples} samples to {csv_path}"}))


def main():
    parser = argparse.ArgumentParser(description="Extract lap telemetry from IBT file")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--lap", type=str, default="fastest", 
                        help="Lap number or 'fastest' (default: fastest)")
    parser.add_argument("--csv", type=str, help="Export to CSV file")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file")
    parser.add_argument("--list-laps", action="store_true", help="Only list available laps")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    # Handle lap number parsing
    lap_number = args.lap
    if lap_number != "fastest":
        try:
            lap_number = int(lap_number)
        except ValueError:
            print(json.dumps({"error": f"Invalid lap number: {lap_number}"}))
            sys.exit(1)
    
    result = extract_lap_telemetry(ibt_path, lap_number)
    
    # List laps only
    if args.list_laps:
        if "available_laps" in result:
            print(json.dumps({"laps": result["available_laps"]}, indent=2))
        else:
            print(json.dumps(result, indent=2))
        return
    
    # Export to CSV
    if args.csv:
        export_to_csv(result, args.csv)
        return
    
    # Regular JSON output (without full telemetry arrays for readability)
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        # For stdout, summarize telemetry instead of dumping arrays
        output = {k: v for k, v in result.items() if k != "telemetry"}
        output["telemetry_channels"] = list(result.get("telemetry", {}).keys())
        output["telemetry_samples"] = result["lap"]["samples"]
        print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()

