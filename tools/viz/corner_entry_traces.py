#!/usr/bin/env python3
"""
Visualization Tool: Corner Entry Traces

Shows brake, steering, and speed traces for each corner entry.
Visualizes the relationship between braking and steering (trail braking patterns).

This is MORE useful than a single "trail braking ratio" because:
- You can SEE where you release brake relative to steering input
- You can compare lap-to-lap patterns
- Context matters: some corners want early release, some want deep trail

Usage:
    uv run python tools/viz/corner_entry_traces.py <telemetry.ibt> --track oschersleben-gp
    uv run python tools/viz/corner_entry_traces.py <telemetry.ibt> --track oschersleben-gp --corner "T2 Hotel Exit"
    uv run python tools/viz/corner_entry_traces.py <telemetry.ibt> --track oschersleben-gp --lap 5

Output: 
    - PNG visualization per corner (or selected corner)
    - JSON with per-corner entry metrics (for coaching)
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

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for corner definitions."""
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


def extract_corner_entry_data(
    corner_start: float,
    corner_end: float,
    lap_start_idx: int,
    lap_end_idx: int,
    dist_data: list,
    brake_data: list,
    throttle_data: list,
    steering_data: list,
    speed_data: list,
    track_length: float,
    approach_pct: float = 0.05  # How far before corner to include
) -> Optional[dict]:
    """
    Extract trace data for a corner entry zone.
    
    Returns dict with distance, brake, throttle, steering, speed arrays for the zone.
    """
    # Define the zone: from (corner_start - approach) to corner_end
    zone_start = corner_start - approach_pct
    if zone_start < 0:
        zone_start += 1.0
    
    # Collect samples in zone
    samples = []
    for i in range(lap_start_idx, lap_end_idx):
        pct = dist_data[i]
        
        # Handle wraparound
        if zone_start > corner_start:
            in_zone = pct >= zone_start or pct <= corner_end
        else:
            in_zone = zone_start <= pct <= corner_end
        
        if in_zone:
            # Calculate distance from corner start (meters)
            if zone_start > corner_start and pct >= zone_start:
                rel_pct = pct - 1.0 - corner_start  # Negative = before corner
            else:
                rel_pct = pct - corner_start
            
            dist_m = rel_pct * track_length
            
            samples.append({
                "dist_m": dist_m,
                "brake_pct": brake_data[i] * 100,
                "throttle_pct": throttle_data[i] * 100,
                "steering_rad": abs(steering_data[i]),
                "speed_kmh": speed_data[i] * 3.6,
            })
    
    if len(samples) < 10:
        return None
    
    # Sort by distance
    samples.sort(key=lambda x: x["dist_m"])
    
    return {
        "dist_m": [s["dist_m"] for s in samples],
        "brake_pct": [s["brake_pct"] for s in samples],
        "throttle_pct": [s["throttle_pct"] for s in samples],
        "steering_rad": [s["steering_rad"] for s in samples],
        "speed_kmh": [s["speed_kmh"] for s in samples],
    }


def analyze_corner_entry(trace_data: dict) -> dict:
    """
    Analyze a corner entry trace for coaching insights.
    
    Returns metrics about brake release point, steering overlap, etc.
    """
    dist = trace_data["dist_m"]
    brake = trace_data["brake_pct"]
    steering = trace_data["steering_rad"]
    speed = trace_data["speed_kmh"]
    
    # Find brake release point (where brake drops below 5%)
    brake_release_dist = None
    for i, (d, b) in enumerate(zip(dist, brake)):
        if b < 5 and any(brake[j] > 10 for j in range(max(0, i-5), i)):
            brake_release_dist = d
            break
    
    # Find turn-in point (where steering exceeds 0.05 rad ~3 degrees)
    turn_in_dist = None
    for d, s in zip(dist, steering):
        if s > 0.05:
            turn_in_dist = d
            break
    
    # Find overlap zone (braking while steering)
    overlap_samples = sum(1 for b, s in zip(brake, steering) if b > 5 and s > 0.05)
    overlap_pct = overlap_samples / len(brake) * 100 if brake else 0
    
    # Calculate min speed and its location
    min_speed = min(speed)
    min_speed_idx = speed.index(min_speed)
    min_speed_dist = dist[min_speed_idx]
    
    # Entry speed (at start of zone)
    entry_speed = speed[0] if speed else 0
    
    # Max brake pressure in zone
    max_brake = max(brake) if brake else 0
    
    # Max steering in zone
    max_steering = max(steering) if steering else 0
    
    return {
        "brake_release_dist_m": round(brake_release_dist, 1) if brake_release_dist else None,
        "turn_in_dist_m": round(turn_in_dist, 1) if turn_in_dist else None,
        "overlap_samples": overlap_samples,
        "overlap_pct": round(overlap_pct, 1),
        "entry_speed_kmh": round(entry_speed, 1),
        "min_speed_kmh": round(min_speed, 1),
        "min_speed_dist_m": round(min_speed_dist, 1),
        "max_brake_pct": round(max_brake, 1),
        "max_steering_rad": round(max_steering, 3),
    }


def plot_corner_entry(
    corner_name: str,
    lap_traces: list,
    output_path: str,
    track_name: str = ""
):
    """
    Plot corner entry traces as mean line with min-max range band.
    Shows variance clearly without spaghetti lines.
    """
    if not HAS_MATPLOTLIB:
        print(json.dumps({"error": "matplotlib not installed. Run: uv add matplotlib"}))
        return
    
    import numpy as np
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    # Interpolate all traces to common distance grid
    all_dists = []
    for lap_num, trace in lap_traces:
        all_dists.extend(trace["dist_m"])
    
    dist_min = min(all_dists)
    dist_max = max(all_dists)
    common_dist = np.linspace(dist_min, dist_max, 200)
    
    # Interpolate each trace to common grid
    brake_interp = []
    throttle_interp = []
    steering_interp = []
    speed_interp = []
    
    for lap_num, trace in lap_traces:
        brake_interp.append(np.interp(common_dist, trace["dist_m"], trace["brake_pct"]))
        throttle_interp.append(np.interp(common_dist, trace["dist_m"], trace["throttle_pct"]))
        steering_interp.append(np.interp(common_dist, trace["dist_m"], 
                                         [s * 57.3 for s in trace["steering_rad"]]))  # to degrees
        speed_interp.append(np.interp(common_dist, trace["dist_m"], trace["speed_kmh"]))
    
    brake_arr = np.array(brake_interp)
    throttle_arr = np.array(throttle_interp)
    steering_arr = np.array(steering_interp)
    speed_arr = np.array(speed_interp)
    
    # Calculate mean and range
    brake_mean = np.mean(brake_arr, axis=0)
    brake_min = np.min(brake_arr, axis=0)
    brake_max = np.max(brake_arr, axis=0)
    
    throttle_mean = np.mean(throttle_arr, axis=0)
    throttle_min = np.min(throttle_arr, axis=0)
    throttle_max = np.max(throttle_arr, axis=0)
    
    steering_mean = np.mean(steering_arr, axis=0)
    steering_min = np.min(steering_arr, axis=0)
    steering_max = np.max(steering_arr, axis=0)
    
    speed_mean = np.mean(speed_arr, axis=0)
    speed_min = np.min(speed_arr, axis=0)
    speed_max = np.max(speed_arr, axis=0)
    
    # Plot with range bands
    # Brake (red for intuitive "stop" color)
    axes[0].fill_between(common_dist, brake_min, brake_max, alpha=0.3, color='red', label='Range')
    axes[0].plot(common_dist, brake_mean, color='red', linewidth=2, label='Mean')
    
    # Throttle (green for intuitive "go" color)
    axes[1].fill_between(common_dist, throttle_min, throttle_max, alpha=0.3, color='green', label='Range')
    axes[1].plot(common_dist, throttle_mean, color='green', linewidth=2, label='Mean')
    
    # Steering (orange)
    axes[2].fill_between(common_dist, steering_min, steering_max, alpha=0.3, color='orange', label='Range')
    axes[2].plot(common_dist, steering_mean, color='orange', linewidth=2, label='Mean')
    
    # Speed (blue)
    axes[3].fill_between(common_dist, speed_min, speed_max, alpha=0.3, color='blue', label='Range')
    axes[3].plot(common_dist, speed_mean, color='blue', linewidth=2, label='Mean')
    
    # Add corner start line
    for ax in axes:
        ax.axvline(x=0, color='gray', linestyle='--', alpha=0.7, linewidth=2, label='Corner Start')
    
    # Labels and formatting
    axes[0].set_ylabel("Brake (%)")
    axes[0].set_ylim(0, 105)
    axes[0].grid(True, alpha=0.3)
    axes[0].legend(loc='upper right', fontsize=9)
    
    axes[1].set_ylabel("Throttle (%)")
    axes[1].set_ylim(0, 105)
    axes[1].grid(True, alpha=0.3)
    axes[1].legend(loc='upper right', fontsize=9)
    
    axes[2].set_ylabel("Steering (deg)")
    axes[2].grid(True, alpha=0.3)
    axes[2].legend(loc='upper right', fontsize=9)
    
    axes[3].set_ylabel("Speed (km/h)")
    axes[3].set_xlabel("Distance from corner start (m)")
    axes[3].grid(True, alpha=0.3)
    axes[3].legend(loc='upper right', fontsize=9)
    
    # Title with lap count
    title = f"Corner Entry Analysis: {corner_name} ({len(lap_traces)} laps)"
    if track_name:
        title += f"\n{track_name}"
    fig.suptitle(title, fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()


def analyze_corner_entries(
    ibt_path: str,
    track_id: str,
    corner_filter: Optional[str] = None,
    lap_filter: Optional[int] = None,
    output_dir: Optional[str] = None
) -> dict:
    """
    Analyze corner entries for all corners (or filtered).
    
    Returns JSON data and optionally generates visualizations.
    """
    # Load track data
    track_data = load_track_data(track_id)
    if not track_data:
        return {"error": f"Track data not found for: {track_id}"}
    
    track_length = track_data.get("length", 3600)
    track_name = track_data.get("name", track_id)
    
    # Open IBT
    ibt = IBT()
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    required = ["LapDistPct", "Brake", "Throttle", "SteeringWheelAngle", "Speed"]
    for ch in required:
        if ch not in available:
            ibt.close()
            return {"error": f"Required channel '{ch}' not found"}
    
    # Extract data
    dist_data = ibt.get_all("LapDistPct")
    brake_data = ibt.get_all("Brake")
    throttle_data = ibt.get_all("Throttle")
    steering_data = ibt.get_all("SteeringWheelAngle")
    speed_data = ibt.get_all("Speed")
    
    # Find laps
    lap_boundaries = find_lap_boundaries(dist_data)
    
    ibt.close()
    
    if len(lap_boundaries) < 2:
        return {"error": "Not enough laps found"}
    
    # Filter corners if requested
    corners = track_data.get("turn", [])
    if corner_filter:
        corners = [c for c in corners if corner_filter.lower() in c["name"].lower()]
    
    if not corners:
        return {"error": f"No corners found matching: {corner_filter}"}
    
    # Analyze each corner
    results = {
        "metadata": {
            "file": Path(ibt_path).name,
            "track": track_name,
            "track_id": track_id,
            "track_length_m": track_length,
            "laps_found": len(lap_boundaries) - 1,
        },
        "corners": {}
    }
    
    for corner in corners:
        corner_name = corner["name"]
        corner_start = corner["start"]
        corner_end = corner["end"]
        
        lap_traces = []
        lap_metrics = []
        
        for lap_idx in range(len(lap_boundaries) - 1):
            lap_num = lap_idx + 1
            
            # Skip if specific lap requested
            if lap_filter and lap_num != lap_filter:
                continue
            
            lap_start = lap_boundaries[lap_idx]
            lap_end = lap_boundaries[lap_idx + 1]
            
            trace = extract_corner_entry_data(
                corner_start, corner_end,
                lap_start, lap_end,
                dist_data, brake_data, throttle_data, steering_data, speed_data,
                track_length
            )
            
            if trace:
                lap_traces.append((lap_num, trace))
                metrics = analyze_corner_entry(trace)
                metrics["lap"] = lap_num
                lap_metrics.append(metrics)
        
        if not lap_metrics:
            continue
        
        # Calculate consistency across laps
        if len(lap_metrics) > 1:
            release_dists = [m["brake_release_dist_m"] for m in lap_metrics if m["brake_release_dist_m"]]
            overlap_pcts = [m["overlap_pct"] for m in lap_metrics]
            
            consistency = {
                "brake_release_sigma_m": round(statistics.stdev(release_dists), 1) if len(release_dists) > 1 else None,
                "overlap_avg_pct": round(statistics.mean(overlap_pcts), 1),
                "overlap_sigma_pct": round(statistics.stdev(overlap_pcts), 1) if len(overlap_pcts) > 1 else None,
            }
        else:
            consistency = {}
        
        results["corners"][corner_name] = {
            "zone": {"start": corner_start, "end": corner_end},
            "laps": lap_metrics,
            "consistency": consistency,
        }
        
        # Generate visualization if output dir specified
        if output_dir and lap_traces and HAS_MATPLOTLIB:
            safe_name = corner_name.replace(" ", "_").replace("/", "-")
            plot_path = Path(output_dir) / f"corner_entry_{safe_name}.png"
            plot_corner_entry(corner_name, lap_traces, str(plot_path), track_name)
            results["corners"][corner_name]["plot"] = str(plot_path)
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Analyze corner entry traces")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, required=True, help="Track ID")
    parser.add_argument("--corner", type=str, help="Filter to specific corner (partial match)")
    parser.add_argument("--lap", type=int, help="Analyze specific lap only")
    parser.add_argument("--output", "-o", type=str, help="Output JSON file")
    parser.add_argument("--plots", type=str, help="Output directory for plots")
    
    args = parser.parse_args()
    
    if not Path(args.ibt_file).exists():
        print(json.dumps({"error": f"File not found: {args.ibt_file}"}))
        sys.exit(1)
    
    # Create plots directory if specified
    if args.plots:
        Path(args.plots).mkdir(parents=True, exist_ok=True)
    
    result = analyze_corner_entries(
        args.ibt_file,
        args.track,
        args.corner,
        args.lap,
        args.plots
    )
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()
