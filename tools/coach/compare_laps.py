#!/usr/bin/env python3
"""
Coach Tool: Compare Two Laps from Same Session

Compares any two laps from an IBT file to identify what changed.
Key for self-improvement: "What did I do differently when I was fast?"

Usage:
    python tools/coach/compare_laps.py <telemetry.ibt> --lap-a 3 --lap-b 5
    python tools/coach/compare_laps.py <telemetry.ibt> --lap-a fastest --lap-b 2
    python tools/coach/compare_laps.py <telemetry.ibt> --lap-a fastest --lap-b slowest --track oschersleben-gp

Output: JSON with corner-by-corner comparison and technique differences
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
    """Load track data for corner-specific analysis."""
    track_file = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_file.exists():
        with open(track_file) as f:
            return json.load(f)
    return None


def find_lap_boundaries(dist_data: list) -> list:
    """Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0."""
    boundaries = []
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    return boundaries


def get_lap_data(ibt: IBT, lap_boundaries: list, session_time: list, lap_selector: str | int) -> dict:
    """Get lap info based on selector (number, 'fastest', 'slowest')."""
    lap_times = []
    for i in range(len(lap_boundaries) - 1):
        start_idx = lap_boundaries[i]
        end_idx = lap_boundaries[i + 1]
        lap_time = session_time[end_idx] - session_time[start_idx]
        if 60 < lap_time < 180:  # Valid lap
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


def analyze_corner_difference(
    ibt: IBT,
    lap_a: dict,
    lap_b: dict,
    turn: dict,
    dist_data: list,
    session_time: list,
) -> dict:
    """Analyze technique differences in a specific corner between two laps."""
    
    turn_start = turn["start"]
    turn_end = turn["end"]
    
    # Get data for both laps in this corner
    def get_corner_data(lap_info):
        start_idx = lap_info["start_idx"]
        end_idx = lap_info["end_idx"]
        
        corner_samples = []
        for i in range(start_idx, end_idx):
            if turn_start <= dist_data[i] <= turn_end:
                corner_samples.append(i)
        
        if not corner_samples:
            return None
        
        # Extract metrics
        speed_data = ibt.get_all("Speed")
        brake_data = ibt.get_all("Brake")
        throttle_data = ibt.get_all("Throttle")
        yaw_data = ibt.get_all("YawRate")
        lat_data = ibt.get_all("LatAccel")
        
        speeds = [speed_data[i] * 3.6 for i in corner_samples]
        brakes = [brake_data[i] * 100 for i in corner_samples]
        throttles = [throttle_data[i] * 100 for i in corner_samples]
        yaw_rates = [abs(yaw_data[i]) * (180/3.14159) for i in corner_samples]
        lat_gs = [abs(lat_data[i]) / 9.80665 for i in corner_samples]
        
        # Time through corner
        entry_time = session_time[corner_samples[0]]
        exit_time = session_time[corner_samples[-1]]
        
        return {
            "time": exit_time - entry_time,
            "entry_speed": speeds[0],
            "min_speed": min(speeds),
            "exit_speed": speeds[-1],
            "max_brake": max(brakes),
            "max_throttle": max(throttles),
            "max_yaw_rate": max(yaw_rates),
            "max_lat_g": max(lat_gs),
        }
    
    data_a = get_corner_data(lap_a)
    data_b = get_corner_data(lap_b)
    
    if not data_a or not data_b:
        return None
    
    # Calculate differences (positive = A is more/faster)
    time_diff = data_b["time"] - data_a["time"]  # Positive = A faster
    
    return {
        "time_delta": round(time_diff, 3),
        "faster_lap": "A" if time_diff > 0 else "B",
        "lap_a": {
            "time": round(data_a["time"], 3),
            "entry_speed": round(data_a["entry_speed"], 1),
            "min_speed": round(data_a["min_speed"], 1),
            "exit_speed": round(data_a["exit_speed"], 1),
            "max_brake": round(data_a["max_brake"], 1),
            "max_lat_g": round(data_a["max_lat_g"], 2),
            "max_yaw": round(data_a["max_yaw_rate"], 1),
        },
        "lap_b": {
            "time": round(data_b["time"], 3),
            "entry_speed": round(data_b["entry_speed"], 1),
            "min_speed": round(data_b["min_speed"], 1),
            "exit_speed": round(data_b["exit_speed"], 1),
            "max_brake": round(data_b["max_brake"], 1),
            "max_lat_g": round(data_b["max_lat_g"], 2),
            "max_yaw": round(data_b["max_yaw_rate"], 1),
        },
        "differences": {
            "entry_speed": round(data_a["entry_speed"] - data_b["entry_speed"], 1),
            "min_speed": round(data_a["min_speed"] - data_b["min_speed"], 1),
            "exit_speed": round(data_a["exit_speed"] - data_b["exit_speed"], 1),
            "max_brake": round(data_a["max_brake"] - data_b["max_brake"], 1),
            "max_lat_g": round(data_a["max_lat_g"] - data_b["max_lat_g"], 2),
        }
    }


def generate_insight(corner_name: str, diff: dict) -> Optional[str]:
    """Generate human-readable insight from corner comparison."""
    if not diff or abs(diff["time_delta"]) < 0.05:
        return None
    
    faster = "A" if diff["time_delta"] > 0 else "B"
    slower = "B" if faster == "A" else "A"
    delta = abs(diff["time_delta"])
    
    # Find the key difference
    diffs = diff["differences"]
    insights = []
    
    if abs(diffs["min_speed"]) > 2:
        speed_diff = diffs["min_speed"]
        if speed_diff > 0:
            insights.append(f"Lap A carried {speed_diff:.0f} km/h more mid-corner")
        else:
            insights.append(f"Lap B carried {-speed_diff:.0f} km/h more mid-corner")
    
    if abs(diffs["entry_speed"]) > 3:
        entry_diff = diffs["entry_speed"]
        if entry_diff > 0:
            insights.append(f"Lap A entered {entry_diff:.0f} km/h faster")
        else:
            insights.append(f"Lap B entered {-entry_diff:.0f} km/h faster")
    
    if abs(diffs["exit_speed"]) > 3:
        exit_diff = diffs["exit_speed"]
        if exit_diff > 0:
            insights.append(f"Lap A exited {exit_diff:.0f} km/h faster")
        else:
            insights.append(f"Lap B exited {-exit_diff:.0f} km/h faster")
    
    if not insights:
        return None
    
    return f"{corner_name}: {' | '.join(insights)} → {delta:.3f}s gain for Lap {faster}"


def compare_laps(
    ibt_path: str,
    lap_a_selector: str | int,
    lap_b_selector: str | int,
    track_id: Optional[str] = None
) -> dict:
    """
    Compare two laps from the same session.
    
    Returns corner-by-corner comparison with technique insights.
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    # Get required data
    dist_data = ibt.get_all("LapDistPct")
    session_time = ibt.get_all("SessionTime")
    
    # Find laps
    lap_boundaries = find_lap_boundaries(dist_data)
    
    if len(lap_boundaries) < 2:
        ibt.close()
        return {"error": "Not enough laps found"}
    
    lap_a = get_lap_data(ibt, lap_boundaries, session_time, lap_a_selector)
    lap_b = get_lap_data(ibt, lap_boundaries, session_time, lap_b_selector)
    
    if not lap_a:
        ibt.close()
        return {"error": f"Lap A ({lap_a_selector}) not found"}
    
    if not lap_b:
        ibt.close()
        return {"error": f"Lap B ({lap_b_selector}) not found"}
    
    if lap_a["number"] == lap_b["number"]:
        ibt.close()
        return {"error": "Cannot compare lap to itself"}
    
    # Load track data for corner analysis
    track_data = load_track_data(track_id) if track_id else None
    
    # Overall comparison
    time_delta = lap_b["time"] - lap_a["time"]  # Positive = A faster
    
    result = {
        "comparison": {
            "lap_a": {
                "number": lap_a["number"],
                "time": round(lap_a["time"], 3),
                "time_formatted": f"{int(lap_a['time'] // 60)}:{lap_a['time'] % 60:06.3f}",
            },
            "lap_b": {
                "number": lap_b["number"],
                "time": round(lap_b["time"], 3),
                "time_formatted": f"{int(lap_b['time'] // 60)}:{lap_b['time'] % 60:06.3f}",
            },
            "delta": round(time_delta, 3),
            "faster_lap": "A" if time_delta > 0 else "B",
        },
    }
    
    # Corner-by-corner analysis if track data available
    if track_data and "turn" in track_data:
        corner_analysis = {}
        insights = []
        biggest_gains = []
        
        for turn in track_data["turn"]:
            diff = analyze_corner_difference(ibt, lap_a, lap_b, turn, dist_data, session_time)
            if diff:
                corner_analysis[turn["name"]] = diff
                
                insight = generate_insight(turn["name"], diff)
                if insight:
                    insights.append(insight)
                
                if abs(diff["time_delta"]) > 0.1:
                    biggest_gains.append({
                        "corner": turn["name"],
                        "delta": diff["time_delta"],
                        "faster": diff["faster_lap"],
                    })
        
        result["corners"] = corner_analysis
        result["insights"] = insights
        result["biggest_differences"] = sorted(biggest_gains, key=lambda x: abs(x["delta"]), reverse=True)[:5]
        
        # Summary stats
        a_faster_corners = sum(1 for c in corner_analysis.values() if c["faster_lap"] == "A")
        b_faster_corners = sum(1 for c in corner_analysis.values() if c["faster_lap"] == "B")
        
        result["summary"] = {
            "corners_faster_lap_a": a_faster_corners,
            "corners_faster_lap_b": b_faster_corners,
            "track": track_data["name"],
        }
    
    ibt.close()
    return result


def main():
    parser = argparse.ArgumentParser(description="Compare two laps from same IBT session")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--lap-a", type=str, required=True,
                        help="First lap: number, 'fastest', or 'slowest'")
    parser.add_argument("--lap-b", type=str, required=True,
                        help="Second lap: number, 'fastest', or 'slowest'")
    parser.add_argument("--track", type=str, help="Track ID for corner analysis")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    # Parse lap selectors
    lap_a = args.lap_a
    lap_b = args.lap_b
    
    for selector in [lap_a, lap_b]:
        if selector not in ["fastest", "slowest"]:
            try:
                int(selector)
            except ValueError:
                print(json.dumps({"error": f"Invalid lap selector: {selector}"}))
                sys.exit(1)
    
    result = compare_laps(ibt_path, lap_a, lap_b, args.track)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()

