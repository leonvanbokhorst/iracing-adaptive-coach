#!/usr/bin/env python3
"""
Core Tool: IBT File Parser (FACTS ONLY)

Parses iRacing's native IBT telemetry files for deep analysis.
Extracts channels that G61 CSV doesn't provide.

Usage:
    python tools/core/parse_ibt.py <telemetry.ibt>
    python tools/core/parse_ibt.py <telemetry.ibt> --channels  # List available channels
    python tools/core/parse_ibt.py <telemetry.ibt> --extract Speed,Brake,YawRate  # Extract specific

Output: JSON with telemetry data and metadata
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


# Channels we care about for coaching (grouped by purpose)
COACHING_CHANNELS = {
    # Core driving inputs
    "inputs": [
        "Throttle",      # 0-1 throttle position
        "Brake",         # 0-1 brake position
        "Clutch",        # 0-1 clutch position
        "SteeringWheelAngle",  # Steering angle in radians
        "Gear",          # Current gear
    ],
    
    # Speed and position
    "motion": [
        "Speed",         # Vehicle speed m/s
        "LapDistPct",    # Track position 0-1
        "Lap",           # Current lap number
        "LapCurrentLapTime",  # Current lap time
    ],
    
    # G-forces (the good stuff)
    "g_forces": [
        "LatAccel",      # Lateral acceleration m/s^2
        "LongAccel",     # Longitudinal acceleration m/s^2
        "VertAccel",     # Vertical acceleration m/s^2
    ],
    
    # Vehicle dynamics (GOLD for technique analysis)
    "dynamics": [
        "Yaw",           # Yaw orientation rad
        "YawRate",       # Yaw rate rad/s - OVERSTEER DETECTION!
        "Pitch",         # Pitch orientation rad
        "PitchRate",     # Pitch rate rad/s
        "Roll",          # Roll orientation rad
        "RollRate",      # Roll rate rad/s
    ],
    
    # Brake analysis
    "braking": [
        "BrakeABSactive",     # ABS TRIGGERED! Boolean
        "LFbrakeLinePress",   # Individual brake pressures
        "RFbrakeLinePress",
        "LRbrakeLinePress",
        "RRbrakeLinePress",
    ],
    
    # Tire temps (Left/Middle/Right carcass per tire)
    "tire_temps": [
        "LFtempCL", "LFtempCM", "LFtempCR",  # Left Front
        "RFtempCL", "RFtempCM", "RFtempCR",  # Right Front
        "LRtempCL", "LRtempCM", "LRtempCR",  # Left Rear
        "RRtempCL", "RRtempCM", "RRtempCR",  # Right Rear
    ],
    
    # Shock deflection (weight transfer visualization)
    "suspension": [
        "LFshockDefl",   # Shock deflection in meters
        "RFshockDefl",
        "LRshockDefl",
        "RRshockDefl",
    ],
    
    # Delta times (game-calculated!)
    "deltas": [
        "LapDeltaToBestLap",        # Delta to personal best
        "LapDeltaToBestLap_OK",     # Is delta valid?
        "LapDeltaToOptimalLap",     # Delta to THEORETICAL BEST
        "LapDeltaToOptimalLap_OK",  # Is delta valid?
        "LapDeltaToBestLap_DD",     # Rate of change of delta
        "LapDeltaToOptimalLap_DD",  # Rate of change of delta to optimal
    ],
    
    # Lap info
    "lap_info": [
        "LapBestLapTime",    # Best lap time this session
        "LapLastLapTime",    # Last completed lap time
        "SessionTime",       # Session time in seconds
    ],
    
    # Engine
    "engine": [
        "RPM",           # Engine RPM
        "FuelLevel",     # Fuel remaining (liters)
        "OilTemp",       # Oil temperature
        "WaterTemp",     # Water temperature
    ],
    
    # Environment
    "environment": [
        "TrackTempCrew",  # Track temperature
        "AirTemp",        # Air temperature
    ],
}

# Flatten for easy lookup
ALL_COACHING_CHANNELS = []
for group in COACHING_CHANNELS.values():
    ALL_COACHING_CHANNELS.extend(group)


def parse_ibt_file(ibt_path: str, channels: Optional[list] = None) -> dict:
    """
    Parse IBT file and extract telemetry data.
    
    Args:
        ibt_path: Path to .ibt file
        channels: List of specific channels to extract. None = all coaching channels.
        
    Returns:
        dict with metadata and telemetry data
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    # Get available channels
    available = ibt.var_headers_names or []
    
    # Determine which channels to extract
    if channels:
        extract_channels = [c for c in channels if c in available]
        missing = [c for c in channels if c not in available]
    else:
        extract_channels = [c for c in ALL_COACHING_CHANNELS if c in available]
        missing = [c for c in ALL_COACHING_CHANNELS if c not in available]
    
    # Get sample count
    sample_count = ibt._disk_header.session_record_count if ibt._disk_header else 0
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    
    # Extract data
    telemetry = {}
    for channel in extract_channels:
        try:
            data = ibt.get_all(channel)
            if data is not None:
                telemetry[channel] = data
        except Exception as e:
            # Skip channels that fail to extract
            pass
    
    # Build result
    result = {
        "metadata": {
            "file": str(Path(ibt_path).name),
            "sample_count": sample_count,
            "tick_rate_hz": tick_rate,
            "duration_seconds": round(sample_count / tick_rate, 2) if tick_rate > 0 else 0,
            "channels_extracted": len(telemetry),
            "channels_requested": len(extract_channels),
            "channels_missing": missing[:10] if len(missing) > 10 else missing,  # Truncate if too many
        },
        "available_channels": available,
        "telemetry": telemetry,
    }
    
    ibt.close()
    return result


def list_channels(ibt_path: str) -> dict:
    """List all available channels in an IBT file, grouped by coaching category."""
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    ibt.close()
    
    # Group by coaching category
    grouped = {}
    for group_name, channels in COACHING_CHANNELS.items():
        present = [c for c in channels if c in available]
        missing = [c for c in channels if c not in available]
        grouped[group_name] = {
            "available": present,
            "missing": missing,
        }
    
    # Find channels not in our coaching list
    all_coaching = set(ALL_COACHING_CHANNELS)
    other_channels = sorted(available - all_coaching)
    
    return {
        "total_channels": len(available),
        "coaching_channels": grouped,
        "other_channels": other_channels[:50],  # First 50 others
        "other_count": len(other_channels),
    }


def extract_summary(ibt_path: str) -> dict:
    """
    Quick summary extraction - just the key coaching metrics.
    Lighter than full extraction.
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    sample_count = ibt._disk_header.session_record_count if ibt._disk_header else 0
    
    summary = {
        "samples": sample_count,
        "duration_s": round(sample_count / 60, 2),  # Assume 60Hz
    }
    
    # Quick stats for key channels
    def get_stats(channel):
        if channel not in available:
            return None
        data = ibt.get_all(channel)
        if data is None or len(data) == 0:
            return None
        import statistics
        clean_data = [x for x in data if x is not None and x == x]  # Remove None and NaN
        if not clean_data:
            return None
        return {
            "min": round(min(clean_data), 4),
            "max": round(max(clean_data), 4),
            "mean": round(statistics.mean(clean_data), 4),
        }
    
    # ABS triggers (count True values)
    if "BrakeABSactive" in available:
        abs_data = ibt.get_all("BrakeABSactive")
        if abs_data:
            summary["abs_triggers"] = sum(1 for x in abs_data if x)
    
    # Speed stats
    summary["speed"] = get_stats("Speed")
    
    # YawRate stats (oversteer indicator)
    summary["yaw_rate"] = get_stats("YawRate")
    
    # Best lap time
    if "LapBestLapTime" in available:
        best = ibt.get(sample_count - 1, "LapBestLapTime") if sample_count > 0 else None
        if best and best > 0:
            summary["best_lap_time"] = round(best, 3)
    
    # Lap count
    if "Lap" in available:
        lap = ibt.get(sample_count - 1, "Lap") if sample_count > 0 else None
        if lap:
            summary["laps"] = int(lap)
    
    ibt.close()
    return summary


def main():
    parser = argparse.ArgumentParser(description="Parse iRacing IBT telemetry files")
    parser.add_argument("ibt_file", help="Path to .ibt file")
    parser.add_argument("--channels", action="store_true", 
                        help="List available channels (no extraction)")
    parser.add_argument("--extract", type=str, 
                        help="Comma-separated list of channels to extract")
    parser.add_argument("--summary", action="store_true",
                        help="Quick summary only (faster)")
    parser.add_argument("--output", "-o", type=str,
                        help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    ibt_path = args.ibt_file
    if not Path(ibt_path).exists():
        print(json.dumps({"error": f"File not found: {ibt_path}"}))
        sys.exit(1)
    
    # Execute requested action
    if args.channels:
        result = list_channels(ibt_path)
    elif args.summary:
        result = extract_summary(ibt_path)
    else:
        channels = args.extract.split(",") if args.extract else None
        result = parse_ibt_file(ibt_path, channels)
    
    # Output
    output_json = json.dumps(result, indent=2)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(json.dumps({"success": f"Written to {args.output}"}))
    else:
        print(output_json)


if __name__ == "__main__":
    main()

