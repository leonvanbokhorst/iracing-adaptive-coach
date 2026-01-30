#!/usr/bin/env python3
"""
Coach Tool: IBT Technique Analysis (FACTS with CONTEXT)

Analyzes IBT telemetry for driving technique insights.
Extracts actionable coaching data from raw IBT channels.

This goes BEYOND what G61 gives us:
- ABS trigger analysis (only for cars WITH ABS - not FF1600!)
- Oversteer detection via YawRate
- Tire temp analysis (driving style fingerprint)
- Weight transfer via shock deflection
- Delta analysis (where you gain/lose vs optimal)

Note: Automatically detects car type from filename and skips
ABS analysis for cars without ABS (FF1600, Skip Barber, etc.)

Usage:
    python tools/coach/analyze_ibt_technique.py <telemetry.ibt>
    python tools/coach/analyze_ibt_technique.py <telemetry.ibt> --track oschersleben-gp

Output: JSON with technique analysis facts
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


# Constants
G = 9.80665  # m/s^2

# Cars WITHOUT ABS (pure racing machines)
# Key = substring in IBT filename, lowercase
CARS_WITHOUT_ABS = [
    "raygr",      # Ray FF1600 (Formula Ford)
    "skipbarber", # Skip Barber Formula
    "usf2000",    # USF2000
    "formula vee", # Formula Vee
    "specracer",  # Spec Racer Ford
    "mx5",        # Mazda MX-5 (no ABS in iRacing)
]


def car_has_abs(ibt_filename: str) -> bool:
    """Check if car has ABS based on filename."""
    filename_lower = ibt_filename.lower()
    for car_id in CARS_WITHOUT_ABS:
        if car_id in filename_lower:
            return False
    return True  # Default: assume ABS exists


def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for corner-specific analysis."""
    track_file = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_file.exists():
        with open(track_file) as f:
            return json.load(f)
    return None


def analyze_abs_triggers(ibt: IBT, available: set, sample_count: int) -> dict:
    """
    Analyze ABS activation patterns.
    
    Returns locations on track where ABS triggered.
    """
    if "BrakeABSactive" not in available or "LapDistPct" not in available:
        return {"available": False}
    
    abs_data = ibt.get_all("BrakeABSactive")
    dist_data = ibt.get_all("LapDistPct")
    lap_data = ibt.get_all("Lap") if "Lap" in available else None
    
    if not abs_data or not dist_data:
        return {"available": False}
    
    # Find ABS trigger events
    triggers = []
    trigger_positions = []
    
    for i, (abs_active, dist) in enumerate(zip(abs_data, dist_data)):
        if abs_active:
            triggers.append({
                "sample": i,
                "track_pct": round(dist * 100, 2),
                "lap": lap_data[i] if lap_data else None,
            })
            trigger_positions.append(dist)
    
    # Group by track zones (10% buckets)
    zone_counts = {f"{i*10}-{(i+1)*10}%": 0 for i in range(10)}
    for pos in trigger_positions:
        bucket = int(pos * 10)
        if bucket >= 10:
            bucket = 9
        key = f"{bucket*10}-{(bucket+1)*10}%"
        zone_counts[key] += 1
    
    # Find hotspots (zones with most triggers)
    hotspots = sorted(zone_counts.items(), key=lambda x: x[1], reverse=True)[:3]
    hotspots = [{"zone": z, "count": c} for z, c in hotspots if c > 0]
    
    return {
        "available": True,
        "total_triggers": len(triggers),
        "triggers_per_lap": round(len(triggers) / max(1, lap_data[-1] if lap_data else 1), 2),
        "zone_breakdown": zone_counts,
        "hotspots": hotspots,
        "trigger_samples": triggers[:20],  # First 20 for detail
    }


def analyze_oversteer(ibt: IBT, available: set, sample_count: int) -> dict:
    """
    Analyze oversteer/understeer via YawRate.
    
    High yaw rate = car is rotating (oversteer).
    Low yaw rate through corners = understeer.
    """
    if "YawRate" not in available:
        return {"available": False}
    
    yaw_data = ibt.get_all("YawRate")
    dist_data = ibt.get_all("LapDistPct") if "LapDistPct" in available else None
    speed_data = ibt.get_all("Speed") if "Speed" in available else None
    
    if not yaw_data:
        return {"available": False}
    
    # Convert to deg/s for human readability
    yaw_deg_s = [abs(y) * (180 / 3.14159) for y in yaw_data]
    
    # Stats
    max_yaw = max(yaw_deg_s)
    avg_yaw = statistics.mean(yaw_deg_s)
    
    # Find oversteer events (yaw rate > threshold)
    # Threshold: > 30 deg/s is notable rotation
    oversteer_threshold = 30.0
    oversteer_events = []
    
    for i, yaw in enumerate(yaw_deg_s):
        if yaw > oversteer_threshold:
            event = {
                "sample": i,
                "yaw_rate_deg_s": round(yaw, 1),
            }
            if dist_data:
                event["track_pct"] = round(dist_data[i] * 100, 2)
            if speed_data:
                event["speed_kmh"] = round(speed_data[i] * 3.6, 1)
            oversteer_events.append(event)
    
    # Group by track position
    zone_counts = {}
    if dist_data:
        for i, yaw in enumerate(yaw_deg_s):
            if yaw > oversteer_threshold:
                bucket = int(dist_data[i] * 10)
                if bucket >= 10:
                    bucket = 9
                key = f"{bucket*10}-{(bucket+1)*10}%"
                zone_counts[key] = zone_counts.get(key, 0) + 1
    
    return {
        "available": True,
        "max_yaw_rate_deg_s": round(max_yaw, 1),
        "avg_yaw_rate_deg_s": round(avg_yaw, 1),
        "oversteer_events": len(oversteer_events),
        "oversteer_threshold_deg_s": oversteer_threshold,
        "oversteer_zones": zone_counts,
        "notable_events": oversteer_events[:10],  # First 10
    }


def analyze_tire_temps(ibt: IBT, available: set) -> dict:
    """
    Analyze tire temperature distribution.
    
    L/M/R temps reveal driving style:
    - Outside hotter = understeering, scrubbing
    - Inside hotter = overdriving turn-in
    - Even = balanced
    
    NOTE: iRacing IBT files do NOT log real-time tire temps continuously.
    Temps are only updated at specific events (pit stops, session end).
    Use peak temps as indicator of max operating temps.
    For live temps during driving, use VRS or other tools.
    """
    tire_channels = {
        "LF": ["LFtempCL", "LFtempCM", "LFtempCR"],
        "RF": ["RFtempCL", "RFtempCM", "RFtempCR"],
        "LR": ["LRtempCL", "LRtempCM", "LRtempCR"],
        "RR": ["RRtempCL", "RRtempCM", "RRtempCR"],
    }
    
    result = {"available": False, "tires": {}, "note": "IBT tire temps are snapshot values (pit/session end), not live. Use VRS for real-time temps."}
    
    for tire, channels in tire_channels.items():
        if not all(c in available for c in channels):
            continue
        
        result["available"] = True
        
        temps_peak = {}
        cold_temp = None
        
        for i, pos in enumerate(["inside", "middle", "outside"]):
            data = ibt.get_all(channels[i])
            if data:
                temps_peak[pos] = round(max(data), 1)
                # Detect cold baseline (most common value, usually start temp)
                if cold_temp is None:
                    cold_temp = round(min(data), 1)
        
        if temps_peak:
            # Calculate balance from peak temps
            inside = temps_peak.get("inside", 0)
            outside = temps_peak.get("outside", 0)
            diff = inside - outside
            
            if diff > 5:
                balance = "inside_hot"  # Overdriving turn-in
            elif diff < -5:
                balance = "outside_hot"  # Understeering/scrubbing
            else:
                balance = "balanced"
            
            result["tires"][tire] = {
                "temps_peak_C": temps_peak,  # Peak temps (most useful)
                "cold_start_C": cold_temp,   # Reference cold temp
                "in_out_diff": round(diff, 1),
                "balance": balance,
            }
    
    return result


def analyze_weight_transfer(ibt: IBT, available: set) -> dict:
    """
    Analyze weight transfer via shock deflection.
    
    - Front compress = braking
    - Rear compress = acceleration
    - Diagonal = cornering
    """
    shock_channels = ["LFshockDefl", "RFshockDefl", "LRshockDefl", "RRshockDefl"]
    
    if not all(c in available for c in shock_channels):
        return {"available": False}
    
    shocks = {c: ibt.get_all(c) for c in shock_channels}
    
    if not all(shocks.values()):
        return {"available": False}
    
    # Convert to mm for readability
    shock_mm = {k: [v * 1000 for v in data] for k, data in shocks.items()}
    
    # Stats per shock
    stats = {}
    for shock, data in shock_mm.items():
        stats[shock] = {
            "min_mm": round(min(data), 2),
            "max_mm": round(max(data), 2),
            "range_mm": round(max(data) - min(data), 2),
            "avg_mm": round(statistics.mean(data), 2),
        }
    
    # Calculate transfer patterns
    # Front vs Rear loading
    front_avg = statistics.mean(shock_mm["LFshockDefl"] + shock_mm["RFshockDefl"])
    rear_avg = statistics.mean(shock_mm["LRshockDefl"] + shock_mm["RRshockDefl"])
    
    return {
        "available": True,
        "shocks": stats,
        "front_rear_balance": round(front_avg - rear_avg, 2),
        "interpretation": {
            "front_rear_diff_mm": round(front_avg - rear_avg, 2),
            "note": "Positive = more front load (braking bias), Negative = more rear load (accel bias)"
        }
    }


def analyze_delta_to_optimal(ibt: IBT, available: set, sample_count: int) -> dict:
    """
    Analyze delta to optimal lap (game-calculated theoretical best).
    
    Shows WHERE you're gaining/losing time vs your own potential.
    """
    if "LapDeltaToOptimalLap" not in available or "LapDeltaToOptimalLap_OK" not in available:
        return {"available": False}
    
    delta_data = ibt.get_all("LapDeltaToOptimalLap")
    valid_data = ibt.get_all("LapDeltaToOptimalLap_OK")
    dist_data = ibt.get_all("LapDistPct") if "LapDistPct" in available else None
    
    if not delta_data or not valid_data:
        return {"available": False}
    
    # Get delta rate of change if available
    delta_dd = ibt.get_all("LapDeltaToOptimalLap_DD") if "LapDeltaToOptimalLap_DD" in available else None
    
    # Filter to valid samples
    valid_deltas = [(i, d, dist_data[i] if dist_data else None) 
                    for i, (d, v) in enumerate(zip(delta_data, valid_data)) if v]
    
    if not valid_deltas:
        return {"available": True, "no_valid_data": True}
    
    # Final delta (end of session/lap)
    final_delta = valid_deltas[-1][1]
    
    # Find where time was lost/gained (using rate of change)
    losing_zones = {}
    gaining_zones = {}
    
    if delta_dd and dist_data:
        for i, dd in enumerate(delta_dd):
            if valid_data[i] and dist_data[i]:
                bucket = int(dist_data[i] * 10)
                if bucket >= 10:
                    bucket = 9
                key = f"{bucket*10}-{(bucket+1)*10}%"
                
                if dd > 0.001:  # Losing time (delta increasing)
                    losing_zones[key] = losing_zones.get(key, 0) + 1
                elif dd < -0.001:  # Gaining time (delta decreasing)
                    gaining_zones[key] = gaining_zones.get(key, 0) + 1
    
    return {
        "available": True,
        "final_delta_to_optimal_s": round(final_delta, 3),
        "losing_time_zones": losing_zones,
        "gaining_time_zones": gaining_zones,
        "interpretation": "Positive delta = slower than optimal, Negative = faster (unlikely)"
    }


def analyze_ibt_technique(ibt_path: str, track_id: Optional[str] = None) -> dict:
    """
    Full technique analysis from IBT file.
    
    Returns coaching-relevant facts derived from IBT data.
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    sample_count = ibt._disk_header.session_record_count if ibt._disk_header else 0
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    
    # Load track data if provided
    track_data = load_track_data(track_id) if track_id else None
    
    # Session info
    best_lap = None
    laps = None
    if "LapBestLapTime" in available and sample_count > 0:
        best_lap = ibt.get(sample_count - 1, "LapBestLapTime")
        if best_lap and best_lap > 0:
            best_lap = round(best_lap, 3)
        else:
            best_lap = None
    if "Lap" in available and sample_count > 0:
        laps = ibt.get(sample_count - 1, "Lap")
    
    # Check if car has ABS
    filename = Path(ibt_path).name
    has_abs = car_has_abs(filename)
    
    # Run all analyses
    result = {
        "metadata": {
            "file": filename,
            "samples": sample_count,
            "duration_seconds": round(sample_count / tick_rate, 2),
            "tick_rate_hz": tick_rate,
            "best_lap_time": best_lap,
            "laps": laps,
            "track": track_data["name"] if track_data else None,
            "car_has_abs": has_abs,
        },
        "oversteer_analysis": analyze_oversteer(ibt, available, sample_count),
        "tire_temps": analyze_tire_temps(ibt, available),
        "weight_transfer": analyze_weight_transfer(ibt, available),
        "delta_analysis": analyze_delta_to_optimal(ibt, available, sample_count),
    }
    
    # Only include ABS analysis for cars that have it
    if has_abs:
        result["abs_analysis"] = analyze_abs_triggers(ibt, available, sample_count)
    else:
        result["abs_analysis"] = {"available": False, "reason": "Car does not have ABS"}
    
    # Add corner-specific analysis if track data available
    if track_data and "turn" in track_data:
        result["corners"] = analyze_corners(ibt, available, track_data, has_abs)
    
    ibt.close()
    return result


def analyze_corners(ibt: IBT, available: set, track_data: dict, has_abs: bool = True) -> dict:
    """Map analyses to specific corners using track data."""
    if "LapDistPct" not in available:
        return {"available": False}
    
    dist_data = ibt.get_all("LapDistPct")
    abs_data = ibt.get_all("BrakeABSactive") if (has_abs and "BrakeABSactive" in available) else None
    yaw_data = ibt.get_all("YawRate") if "YawRate" in available else None
    
    corners = {}
    
    for turn in track_data.get("turn", []):
        start = turn["start"]
        end = turn["end"]
        name = turn["name"]
        
        # Count events in this corner
        oversteer_count = 0
        abs_count = 0 if has_abs else None  # None = not applicable
        
        for i, dist in enumerate(dist_data):
            if start <= dist <= end:
                if abs_data and abs_data[i]:
                    abs_count += 1
                if yaw_data and abs(yaw_data[i]) * (180/3.14159) > 30:
                    oversteer_count += 1
        
        corner_data = {
            "track_pct": f"{start*100:.0f}%-{end*100:.0f}%",
            "oversteer_events": oversteer_count,
        }
        # Only include ABS data if car has ABS
        if has_abs:
            corner_data["abs_triggers"] = abs_count
        
        corners[name] = corner_data
    
    return {"available": True, "corners": corners}


def main():
    parser = argparse.ArgumentParser(description="Analyze IBT telemetry for driving technique")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--track", type=str, help="Track ID for corner-specific analysis")
    parser.add_argument("--output", "-o", type=str, help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    result = analyze_ibt_technique(ibt_path, args.track)
    
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()

