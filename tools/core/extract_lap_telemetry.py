#!/usr/bin/env python3
"""
Extract single lap telemetry from IBT to CSV for comparison.

Usage:
    python tools/core/extract_lap_telemetry.py <file.ibt> --lap fastest -o output.csv
    python tools/core/extract_lap_telemetry.py <file.ibt> --lap 14 -o output.csv
    
Output: CSV file with telemetry columns matching Garage 61 export format
"""

import sys
import json
import argparse
from pathlib import Path
import csv

try:
    from irsdk import IBT
except ImportError:
    print(json.dumps({"error": "pyirsdk not installed. Run: uv add pyirsdk"}))
    sys.exit(1)


def find_lap_boundaries(dist_data: list) -> list:
    """Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0."""
    boundaries = []
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def get_lap_info(session_time: list, lap_boundaries: list, lap_selector: str) -> dict:
    """Get lap info based on selector (number or 'fastest')."""
    lap_times = []
    for i in range(len(lap_boundaries) - 1):
        start_idx = lap_boundaries[i]
        end_idx = lap_boundaries[i + 1]
        lap_time = session_time[end_idx] - session_time[start_idx]
        if 30 < lap_time < 300:  # Valid lap (30s to 5min)
            lap_times.append({
                "number": i + 1,
                "time": lap_time,
                "start_idx": start_idx,
                "end_idx": end_idx,
            })
    
    if not lap_times:
        return None
    
    if lap_selector == "fastest":
        return min(lap_times, key=lambda x: x["time"])
    elif lap_selector == "slowest":
        return max(lap_times, key=lambda x: x["time"])
    else:
        lap_num = int(lap_selector)
        matching = [l for l in lap_times if l["number"] == lap_num]
        return matching[0] if matching else None


def extract_lap_telemetry(ibt_path: str, lap_selector: str, output_path: str = None):
    """
    Extract telemetry for a specific lap from IBT file.
    
    Args:
        ibt_path: Path to .ibt file
        lap_selector: 'fastest', 'slowest', or lap number
        output_path: Optional output CSV path
    
    Returns:
        dict with success/error and lap info
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    # Get lap boundaries
    dist_data = ibt.get_all("LapDistPct")
    session_time = ibt.get_all("SessionTime")
    lap_boundaries = find_lap_boundaries(dist_data)
    
    if len(lap_boundaries) < 2:
        ibt.close()
        return {"error": "Not enough laps found in session"}
    
    # Find the requested lap
    lap_info = get_lap_info(session_time, lap_boundaries, lap_selector)
    
    if not lap_info:
        ibt.close()
        return {"error": f"Lap '{lap_selector}' not found"}
    
    start_idx = lap_info["start_idx"]
    end_idx = lap_info["end_idx"]
    
    # Extract telemetry channels (matching Garage 61 export format)
    channels = {
        "Speed": ibt.get_all("Speed"),
        "LapDistPct": ibt.get_all("LapDistPct"),
        "Lat": ibt.get_all("Lat"),
        "Lon": ibt.get_all("Lon"),
        "Brake": ibt.get_all("Brake"),
        "Throttle": ibt.get_all("Throttle"),
        "RPM": ibt.get_all("RPM"),
        "SteeringWheelAngle": ibt.get_all("SteeringWheelAngle"),
        "Gear": ibt.get_all("Gear"),
        "LatAccel": ibt.get_all("LatAccel"),
        "LongAccel": ibt.get_all("LongAccel"),
        "YawRate": ibt.get_all("YawRate"),
    }
    
    ibt.close()
    
    # Build rows for this lap
    rows = []
    for i in range(start_idx, end_idx):
        row = {}
        for channel, data in channels.items():
            if data is not None:
                value = data[i]
                # Keep raw iRacing units to match G61 format:
                # - Speed: m/s (G61 uses m/s)
                # - LatAccel/LongAccel: m/s² (G61 uses m/s²)
                # - SteeringWheelAngle: radians (G61 uses radians)
                # No conversion needed - IBT and G61 use same units
                pass
                row[channel] = value
        rows.append(row)
    
    # Format lap time
    lap_time = lap_info["time"]
    lap_time_formatted = f"{int(lap_time // 60)}:{lap_time % 60:06.3f}"
    
    result = {
        "success": True,
        "lap_number": lap_info["number"],
        "lap_time": round(lap_time, 3),
        "lap_time_formatted": lap_time_formatted,
        "samples": len(rows),
    }
    
    # Write CSV if output path provided
    if output_path:
        fieldnames = list(rows[0].keys()) if rows else []
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        result["output_file"] = output_path
    else:
        # Return the data directly
        result["telemetry"] = rows
    
    return result


def main():
    parser = argparse.ArgumentParser(description="Extract lap telemetry from IBT to CSV")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--lap", type=str, default="fastest",
                        help="Lap to extract: 'fastest', 'slowest', or lap number (default: fastest)")
    parser.add_argument("--output", "-o", type=str, help="Output CSV file path")
    
    args = parser.parse_args()
    
    if not Path(args.ibt_file).exists():
        print(json.dumps({"error": f"File not found: {args.ibt_file}"}))
        sys.exit(1)
    
    result = extract_lap_telemetry(args.ibt_file, args.lap, args.output)
    
    if "error" in result:
        print(json.dumps(result))
        sys.exit(1)
    
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
