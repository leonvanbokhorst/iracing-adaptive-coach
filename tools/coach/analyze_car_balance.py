#!/usr/bin/env python3
"""
Coach Tool: Car Balance Analysis (Understeer/Oversteer Detection)

Detects understeer and oversteer from IBT telemetry by analyzing
the relationship between steering input and car response.

Key Metrics:
1. Steering Response Ratio - Expected vs actual yaw rate
2. Steering Corrections - Countersteer patterns (oversteer indicator)
3. Context Classification - Entry vs exit, brake vs throttle

Usage:
    python tools/coach/analyze_car_balance.py <telemetry.ibt>
    python tools/coach/analyze_car_balance.py <telemetry.ibt> --track oschersleben-gp
    python tools/coach/analyze_car_balance.py <telemetry.ibt> --lap fastest

Output: JSON with balance analysis and corner-by-corner breakdown
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


# =============================================================================
# CONSTANTS
# =============================================================================

# Minimum speed to consider for balance analysis (avoid pit/slow zones)
MIN_ANALYSIS_SPEED_MS = 15  # ~54 km/h

# Minimum steering angle to consider (avoid straights)
MIN_STEERING_DEG = 5  # 5 degrees

# Steering Response Ratio thresholds
# Ratio = Actual_YawRate / Expected_YawRate
UNDERSTEER_THRESHOLD = 0.7       # Car responding < 70% of expected = understeer
UNDERSTEER_MILD = 0.85           # 70-85% = mild understeer (front working hard)
NEUTRAL_MIN = 0.85               # 85-115% = neutral (good balance)
NEUTRAL_MAX = 1.15
HIGH_ROTATION_THRESHOLD = 1.15   # 115-140% = high rotation (on the edge, good but watch it)
OVERSTEER_THRESHOLD = 1.4        # > 140% = oversteer (too much rotation)

# Countersteer detection (steering direction reversal)
COUNTERSTEER_MIN_ANGLE_DEG = 10  # Minimum reversal to count as countersteer
COUNTERSTEER_WINDOW_SAMPLES = 30  # ~0.5 sec at 60Hz

# Severity thresholds for yaw rate spikes (deg/s)
MILD_OVERSTEER_DEG_S = 25      # Noticeable rotation, easy save
MODERATE_OVERSTEER_DEG_S = 40  # Serious rotation, requires quick reaction
SEVERE_OVERSTEER_DEG_S = 55    # Brown pants territory, barely saveable
SPIN_THRESHOLD_DEG_S = 65      # Physics has left the chat - this is a spin

# Tire temperature constants (Celsius for FF1600)
# Reference: guidebook/chapters/06-slip-angle/06g-tire-temperature-diagnostics.md
TIRE_TEMP_OPTIMAL_MIN = 85  # Below = cold, not generating grip
TIRE_TEMP_OPTIMAL_MAX = 100  # Above = overheating, degradation
TIRE_TEMP_CRITICAL = 110  # Danger zone - tire destruction

# Input smoothness thresholds (steering rate in deg/s)
SMOOTH_STEERING_RATE = 150  # Butter smooth, pro level
ACCEPTABLE_STEERING_RATE = 300  # Normal, fine
AGGRESSIVE_STEERING_RATE = 500  # Getting jerky
VIOLENT_STEERING_RATE = 800  # Fighting the wheel


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def load_track_data(track_id: str) -> Optional[dict]:
    """Load track data for corner-specific analysis."""
    track_path = Path(__file__).parent.parent.parent / "tracks" / "track-data" / f"{track_id}.json"
    if track_path.exists():
        with open(track_path) as f:
            return json.load(f)
    return None


def rad_to_deg(rad: float) -> float:
    """Convert radians to degrees."""
    return rad * (180 / math.pi)


def find_lap_boundaries(dist_data: list) -> list:
    """Find lap boundaries by detecting LapDistPct crossing from ~1.0 to ~0.0."""
    boundaries = [0]
    for i in range(1, len(dist_data)):
        if dist_data[i-1] > 0.9 and dist_data[i] < 0.1:
            boundaries.append(i)
    boundaries.append(len(dist_data))
    return boundaries


def get_context(brake: float, throttle: float) -> str:
    """Determine driving context based on pedal inputs."""
    if brake > 0.1:
        return "braking"
    elif throttle > 0.3:
        return "accelerating"
    else:
        return "coasting"


def analyze_tire_temperatures(
    lf_temps: dict,  # {"L": [], "M": [], "R": []}
    rf_temps: dict,
    lr_temps: dict,
    rr_temps: dict,
    steering_data: list = None,
    speed_data: list = None,
) -> dict:
    """
    Analyze tire temperatures for grip and driving style insights.
    
    Temperature spread across L/M/R tells us:
    - Hot inside = understeering (pushing through corners)
    - Hot outside = oversteering or aggressive turn-in
    - Even = good tire usage
    
    Front vs Rear balance tells us overall grip distribution.
    
    We track THREE temp metrics:
    1. Peak temps - Maximum heat (degradation indicator)
    2. Cornering temps - Temps while actually turning (grip indicator)
    3. Session average - Diluted by pit/straights (less useful)
    
    Reference: guidebook/chapters/06-slip-angle/06g-tire-temperature-diagnostics.md
    """
    
    def get_cornering_indices(steering_data: list, speed_data: list) -> list:
        """Find indices where car is cornering (steering > 15°, speed > 60 km/h)."""
        if not steering_data or not speed_data:
            return None
        
        indices = []
        for i in range(len(steering_data)):
            steer_deg = abs(rad_to_deg(steering_data[i]))
            speed_kmh = speed_data[i] * 3.6
            if steer_deg > 15 and speed_kmh > 60:
                indices.append(i)
        return indices if indices else None
    
    def analyze_tire(temps: dict, position: str, cornering_indices: list = None) -> dict:
        """Analyze single tire temperature distribution."""
        if not temps["L"] or not temps["M"] or not temps["R"]:
            return None
        
        # Peak temps (max reached)
        peak_l = max(temps["L"])
        peak_m = max(temps["M"])
        peak_r = max(temps["R"])
        peak_avg = (peak_l + peak_m + peak_r) / 3
        
        # Session averages (includes pit/straights - less useful)
        session_avg_l = statistics.mean(temps["L"])
        session_avg_m = statistics.mean(temps["M"])
        session_avg_r = statistics.mean(temps["R"])
        
        # Cornering temps (when actually turning - most useful for grip analysis)
        if cornering_indices:
            corner_l = [temps["L"][i] for i in cornering_indices if i < len(temps["L"])]
            corner_m = [temps["M"][i] for i in cornering_indices if i < len(temps["M"])]
            corner_r = [temps["R"][i] for i in cornering_indices if i < len(temps["R"])]
            
            if corner_l:
                cornering_avg_l = statistics.mean(corner_l)
                cornering_avg_m = statistics.mean(corner_m)
                cornering_avg_r = statistics.mean(corner_r)
                cornering_max_l = max(corner_l)
                cornering_max_m = max(corner_m)
                cornering_max_r = max(corner_r)
            else:
                cornering_avg_l = cornering_avg_m = cornering_avg_r = None
                cornering_max_l = cornering_max_m = cornering_max_r = None
        else:
            cornering_avg_l = cornering_avg_m = cornering_avg_r = None
            cornering_max_l = cornering_max_m = cornering_max_r = None
        
        # Use cornering temps for analysis if available, otherwise peaks
        if cornering_avg_l is not None:
            analysis_l = cornering_avg_l
            analysis_m = cornering_avg_m
            analysis_r = cornering_avg_r
            analysis_source = "cornering"
        else:
            analysis_l = peak_l
            analysis_m = peak_m
            analysis_r = peak_r
            analysis_source = "peak"
        
        analysis_avg = (analysis_l + analysis_m + analysis_r) / 3
        spread = max(analysis_l, analysis_m, analysis_r) - min(analysis_l, analysis_m, analysis_r)
        
        # Determine hot zone (for driving style diagnosis)
        # L = left edge of tire, R = right edge
        # For left-side tires (LF, LR): L = inside, R = outside
        # For right-side tires (RF, RR): L = outside, R = inside
        temps_map = {"inside": analysis_l, "middle": analysis_m, "outside": analysis_r}
        if position.startswith("R"):  # RF or RR - swap inside/outside
            temps_map = {"inside": analysis_r, "middle": analysis_m, "outside": analysis_l}
        
        hot_zone = max(temps_map, key=temps_map.get)
        
        # Driving style diagnosis based on hot zone
        if spread < 5:
            diagnosis = "balanced"  # Even wear, good technique
        elif hot_zone == "inside":
            diagnosis = "understeer_tendency"  # Pushing = hot inside edge
        elif hot_zone == "outside":
            diagnosis = "aggressive_turn_in"  # Loading outside edge hard
        else:
            diagnosis = "neutral"
        
        # Temperature state based on peak/cornering temps (not session avg)
        if peak_avg < TIRE_TEMP_OPTIMAL_MIN:
            state = "cold"
        elif peak_avg > TIRE_TEMP_CRITICAL:
            state = "critical"
        elif peak_avg > TIRE_TEMP_OPTIMAL_MAX:
            state = "hot"  # Above optimal but not critical
        else:
            state = "optimal"
        
        # FACTS ONLY - no interpretation
        result = {
            # Peak temps (raw maximums)
            "peak_avg_c": round(peak_avg, 1),
            "peak_L_c": round(peak_l, 1),
            "peak_M_c": round(peak_m, 1),
            "peak_R_c": round(peak_r, 1),
            # Session averages
            "session_avg_L_c": round(session_avg_l, 1),
            "session_avg_M_c": round(session_avg_m, 1),
            "session_avg_R_c": round(session_avg_r, 1),
            # Spread (raw number)
            "spread_c": round(spread, 1),
        }
        
        # Add cornering temps if available (raw numbers)
        if cornering_avg_l is not None:
            result["cornering_avg_L_c"] = round(cornering_avg_l, 1)
            result["cornering_avg_M_c"] = round(cornering_avg_m, 1)
            result["cornering_avg_R_c"] = round(cornering_avg_r, 1)
            result["cornering_max_L_c"] = round(cornering_max_l, 1)
            result["cornering_max_M_c"] = round(cornering_max_m, 1)
            result["cornering_max_R_c"] = round(cornering_max_r, 1)
        
        return result
    
    # Get cornering indices for more accurate temp analysis
    cornering_indices = get_cornering_indices(steering_data, speed_data)
    
    result = {
        "left_front": analyze_tire(lf_temps, "LF", cornering_indices),
        "right_front": analyze_tire(rf_temps, "RF", cornering_indices),
        "left_rear": analyze_tire(lr_temps, "LR", cornering_indices),
        "right_rear": analyze_tire(rr_temps, "RR", cornering_indices),
    }
    
    # Filter out None values (missing data)
    result = {k: v for k, v in result.items() if v is not None}
    
    if not result:
        return {"available": False}
    
    # Add cornering sample count
    if cornering_indices:
        result["cornering_samples"] = len(cornering_indices)
    
    # Front vs Rear balance (using peak temps)
    front_temps = []
    rear_temps = []
    
    if result.get("left_front"):
        front_temps.append(result["left_front"]["peak_avg_c"])
    if result.get("right_front"):
        front_temps.append(result["right_front"]["peak_avg_c"])
    if result.get("left_rear"):
        rear_temps.append(result["left_rear"]["peak_avg_c"])
    if result.get("right_rear"):
        rear_temps.append(result["right_rear"]["peak_avg_c"])
    
    if front_temps and rear_temps:
        front_avg = statistics.mean(front_temps)
        rear_avg = statistics.mean(rear_temps)
        f_r_delta = front_avg - rear_avg
        
        # FACTS ONLY - no interpretation
        result["front_rear_balance"] = {
            "front_avg_c": round(front_avg, 1),
            "rear_avg_c": round(rear_avg, 1),
            "delta_c": round(f_r_delta, 1),
        }
    
    result["available"] = True
    return result


def analyze_input_smoothness(steering_data: list, tick_rate: int = 60) -> dict:
    """
    Analyze steering input smoothness - FACTS ONLY.
    
    Calculates steering rate (how fast the wheel moves).
    Little Padawan interprets what the numbers mean.
    
    Returns:
        dict with raw steering rate data
    """
    if len(steering_data) < 2:
        return {"available": False}
    
    # Convert to degrees
    steering_deg = [rad_to_deg(s) for s in steering_data]
    
    # Calculate steering rate (deg/s) between samples
    steering_rates = []
    for i in range(1, len(steering_deg)):
        rate = abs(steering_deg[i] - steering_deg[i-1]) * tick_rate
        steering_rates.append(rate)
    
    if not steering_rates:
        return {"available": False}
    
    avg_rate = statistics.mean(steering_rates)
    max_rate = max(steering_rates)
    std_rate = statistics.stdev(steering_rates) if len(steering_rates) > 1 else 0
    
    # Count samples in rate bands (raw counts, no interpretation)
    samples_under_150 = sum(1 for r in steering_rates if r <= 150)
    samples_150_300 = sum(1 for r in steering_rates if 150 < r <= 300)
    samples_300_500 = sum(1 for r in steering_rates if 300 < r <= 500)
    samples_over_500 = sum(1 for r in steering_rates if r > 500)
    
    total = len(steering_rates)
    
    # FACTS ONLY - no scores, no diagnosis
    return {
        "available": True,
        "total_samples": total,
        "avg_steering_rate_deg_s": round(avg_rate, 1),
        "max_steering_rate_deg_s": round(max_rate, 1),
        "std_steering_rate_deg_s": round(std_rate, 1),
        "rate_distribution": {
            "under_150_deg_s_pct": round(samples_under_150 / total * 100, 1),
            "150_to_300_deg_s_pct": round(samples_150_300 / total * 100, 1),
            "300_to_500_deg_s_pct": round(samples_300_500 / total * 100, 1),
            "over_500_deg_s_pct": round(samples_over_500 / total * 100, 1),
        },
        "samples_over_500_deg_s": samples_over_500,
    }


def analyze_delta_correlation(
    delta_data: list,
    balance_events: list,  # list of {"sample": int, "type": str, ...}
    tick_rate: int = 60,
    window_samples: int = 30,  # 0.5 sec window
) -> dict:
    """
    Correlate balance events with lap time delta - FACTS ONLY.
    
    Measures delta change during events. Little Padawan interprets.
    
    Args:
        delta_data: LapDeltaToSessionBestLap data
        balance_events: Events from balance analysis
        tick_rate: Sample rate
        window_samples: Samples to analyze around event
    
    Returns:
        dict with raw delta measurements
    """
    if not delta_data or not balance_events:
        return {"available": False}
    
    understeer_deltas = []
    oversteer_deltas = []
    spin_deltas = []
    
    for event in balance_events:
        sample = event.get("sample", 0)
        event_type = event.get("type", event.get("severity", "unknown"))
        
        # Get delta before and after event
        start = max(0, sample - window_samples)
        end = min(len(delta_data), sample + window_samples)
        
        if end <= start:
            continue
        
        delta_before = delta_data[start]
        delta_after = delta_data[end - 1]
        delta_change = delta_after - delta_before
        
        # Classify by event type (raw classification based on data)
        if "understeer" in str(event_type).lower() or event.get("response_ratio", 1.0) < UNDERSTEER_THRESHOLD:
            understeer_deltas.append(delta_change)
        elif "spin" in str(event_type).lower():
            spin_deltas.append(delta_change)
        elif "oversteer" in str(event_type).lower() or event.get("response_ratio", 1.0) > OVERSTEER_THRESHOLD:
            oversteer_deltas.append(delta_change)
    
    # FACTS ONLY - raw numbers, no interpretation
    result = {"available": True}
    
    if understeer_deltas:
        result["understeer_delta"] = {
            "event_count": len(understeer_deltas),
            "total_delta_s": round(sum(understeer_deltas), 3),
            "avg_delta_s": round(statistics.mean(understeer_deltas), 3),
            "max_delta_s": round(max(understeer_deltas), 3),
        }
    
    if oversteer_deltas:
        result["oversteer_delta"] = {
            "event_count": len(oversteer_deltas),
            "total_delta_s": round(sum(oversteer_deltas), 3),
            "avg_delta_s": round(statistics.mean(oversteer_deltas), 3),
            "max_delta_s": round(max(oversteer_deltas), 3),
        }
    
    if spin_deltas:
        result["spin_delta"] = {
            "event_count": len(spin_deltas),
            "total_delta_s": round(sum(spin_deltas), 3),
            "avg_delta_s": round(statistics.mean(spin_deltas), 3),
            "max_delta_s": round(max(spin_deltas), 3),
        }
    
    return result


# =============================================================================
# CORE ANALYSIS FUNCTIONS
# =============================================================================

def calculate_expected_yaw_rate(steering_deg: float, speed_ms: float, wheelbase: float = 2.3) -> float:
    """
    Calculate expected yaw rate for given steering and speed.
    
    Uses simplified bicycle model:
    YawRate = (Speed * tan(SteeringAngle)) / Wheelbase
    
    Args:
        steering_deg: Steering wheel angle in degrees (at wheel, not rack)
        speed_ms: Vehicle speed in m/s
        wheelbase: Vehicle wheelbase in meters (FF1600 ≈ 2.3m)
    
    Returns:
        Expected yaw rate in deg/s
    """
    # Steering ratio: wheel angle to front wheel angle (typical ~12:1 to 16:1)
    steering_ratio = 14.0
    front_wheel_angle_deg = abs(steering_deg) / steering_ratio
    front_wheel_angle_rad = math.radians(front_wheel_angle_deg)
    
    # Avoid division by zero and unrealistic angles
    if front_wheel_angle_rad < 0.001 or speed_ms < 1:
        return 0.0
    
    # Bicycle model: yaw_rate = v * tan(delta) / L
    yaw_rate_rad_s = speed_ms * math.tan(front_wheel_angle_rad) / wheelbase
    return abs(rad_to_deg(yaw_rate_rad_s))


def analyze_steering_response(
    steering_data: list,
    yaw_data: list,
    speed_data: list,
    dist_data: list,
    brake_data: list,
    throttle_data: list,
) -> dict:
    """
    Analyze steering response to detect understeer and oversteer.
    
    Separates:
    - Controllable oversteer (saveable slides)
    - Actual spins (physics has left the chat)
    
    Returns:
        dict with balance metrics and events
    """
    understeer_events = []
    oversteer_events = []
    high_rotation_events = []  # On the edge - good rotation but watch it
    spin_events = []  # Separate tracking for actual spins
    neutral_samples = 0
    understeer_samples = 0
    high_rotation_samples = 0  # The "on the edge" zone
    oversteer_samples = 0
    spin_samples = 0
    total_analyzed = 0
    
    response_ratios = []
    
    # Track transitions: where does good rotation tip into oversteer?
    transition_events = []
    prev_state = None
    
    for i in range(len(steering_data)):
        steering_deg = abs(rad_to_deg(steering_data[i]))
        yaw_deg_s = abs(rad_to_deg(yaw_data[i]))
        speed_ms = speed_data[i]
        
        # Skip if not in analysis zone
        if speed_ms < MIN_ANALYSIS_SPEED_MS or steering_deg < MIN_STEERING_DEG:
            continue
        
        total_analyzed += 1
        
        # First check: Is this a spin? (yaw rate too high to be controllable)
        if yaw_deg_s > SPIN_THRESHOLD_DEG_S:
            spin_samples += 1
            context = get_context(
                brake_data[i] if brake_data else 0,
                throttle_data[i] if throttle_data else 0
            )
            spin_events.append({
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "yaw_deg_s": round(yaw_deg_s, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
                "type": "spin",
            })
            continue  # Don't count spins in balance analysis
        
        # Calculate expected yaw rate
        expected_yaw = calculate_expected_yaw_rate(steering_deg, speed_ms)
        if expected_yaw < 1.0:
            continue
        
        # Calculate response ratio
        ratio = yaw_deg_s / expected_yaw
        response_ratios.append(ratio)
        
        # Classify
        context = get_context(
            brake_data[i] if brake_data else 0,
            throttle_data[i] if throttle_data else 0
        )
        
        # Classify the current state (raw data, no interpretation)
        if ratio < UNDERSTEER_THRESHOLD:
            current_state = "understeer"
            understeer_samples += 1
            event = {
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "response_ratio": round(ratio, 2),
                "steering_deg": round(steering_deg, 1),
                "actual_yaw_deg_s": round(yaw_deg_s, 1),
                "expected_yaw_deg_s": round(expected_yaw, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
            }
            understeer_events.append(event)
            
        elif ratio > OVERSTEER_THRESHOLD:
            current_state = "oversteer"
            oversteer_samples += 1
            event = {
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "response_ratio": round(ratio, 2),
                "steering_deg": round(steering_deg, 1),
                "actual_yaw_deg_s": round(yaw_deg_s, 1),
                "expected_yaw_deg_s": round(expected_yaw, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
            }
            oversteer_events.append(event)
        
        elif ratio > HIGH_ROTATION_THRESHOLD:
            # HIGH ROTATION ZONE: 1.15-1.4 ratio
            # This is "on the edge" - good rotation but one step from oversteer
            current_state = "high_rotation"
            high_rotation_samples += 1
            event = {
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "response_ratio": round(ratio, 2),
                "steering_deg": round(steering_deg, 1),
                "actual_yaw_deg_s": round(yaw_deg_s, 1),
                "expected_yaw_deg_s": round(expected_yaw, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
            }
            high_rotation_events.append(event)
            
        else:
            current_state = "neutral"
            neutral_samples += 1
        
        # Track transitions to oversteer (raw data)
        if prev_state == "high_rotation" and current_state == "oversteer":
            transition_events.append({
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "from_state": "high_rotation",
                "to_state": "oversteer",
                "ratio_at_transition": round(ratio, 2),
                "yaw_deg_s": round(yaw_deg_s, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
            })
        elif prev_state == "neutral" and current_state == "oversteer":
            transition_events.append({
                "sample": i,
                "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                "from_state": "neutral",
                "to_state": "oversteer",
                "ratio_at_transition": round(ratio, 2),
                "yaw_deg_s": round(yaw_deg_s, 1),
                "speed_kmh": round(speed_ms * 3.6, 1),
                "context": context,
            })
        
        prev_state = current_state
    
    # Calculate percentages (raw numbers)
    balance_analyzed = total_analyzed - spin_samples
    if balance_analyzed > 0:
        understeer_pct = (understeer_samples / balance_analyzed) * 100
        high_rotation_pct = (high_rotation_samples / balance_analyzed) * 100
        oversteer_pct = (oversteer_samples / balance_analyzed) * 100
        neutral_pct = (neutral_samples / balance_analyzed) * 100
    else:
        understeer_pct = high_rotation_pct = oversteer_pct = neutral_pct = 0
    
    # Response ratio stats (raw numbers)
    avg_response_ratio = statistics.mean(response_ratios) if response_ratios else 1.0
    std_response_ratio = statistics.stdev(response_ratios) if len(response_ratios) > 1 else 0
    
    # Group spin events by track location (raw counts)
    spin_zones = {}
    for spin in spin_events:
        if spin["track_pct"]:
            bucket = int(spin["track_pct"] / 10) * 10
            key = f"{bucket}-{bucket+10}%"
            spin_zones[key] = spin_zones.get(key, 0) + 1
    
    # Group transitions by track location (raw counts)
    transition_zones = {}
    for trans in transition_events:
        if trans["track_pct"]:
            bucket = int(trans["track_pct"] / 10) * 10
            key = f"{bucket}-{bucket+10}%"
            transition_zones[key] = transition_zones.get(key, 0) + 1
    
    # FACTS ONLY - raw numbers, no interpretation
    return {
        "samples_analyzed": total_analyzed,
        "samples_excluding_spins": balance_analyzed,
        "avg_response_ratio": round(avg_response_ratio, 2),
        "std_response_ratio": round(std_response_ratio, 2),
        "balance_distribution_pct": {
            "understeer": round(understeer_pct, 1),
            "neutral": round(neutral_pct, 1),
            "high_rotation": round(high_rotation_pct, 1),
            "oversteer": round(oversteer_pct, 1),
        },
        "event_counts": {
            "understeer": len(understeer_events),
            "high_rotation": len(high_rotation_events),
            "oversteer": len(oversteer_events),
            "spins": len(spin_events),
        },
        "transition_count": len(transition_events),
        "transition_zones": transition_zones,
        "transition_events": transition_events[:15],
        "spin_zones": spin_zones,
        "spin_events": spin_events[:10],
        "understeer_events": understeer_events[:20],
        "high_rotation_events": high_rotation_events[:20],
        "oversteer_events": oversteer_events[:20],
    }


def detect_countersteer_events(steering_data: list, dist_data: list) -> list:
    """
    Detect countersteer patterns indicating oversteer corrections.
    
    Countersteer = rapid steering direction reversal.
    Pattern: Turning right → sudden turn left → return to right
    """
    events = []
    steering_deg = [rad_to_deg(s) for s in steering_data]
    
    for i in range(COUNTERSTEER_WINDOW_SAMPLES, len(steering_deg) - COUNTERSTEER_WINDOW_SAMPLES):
        # Look for sign change with significant magnitude
        current = steering_deg[i]
        before = steering_deg[i - COUNTERSTEER_WINDOW_SAMPLES // 2]
        after = steering_deg[i + COUNTERSTEER_WINDOW_SAMPLES // 2]
        
        # Check for reversal pattern: same sign before/after, opposite at i
        if before * after > 0 and current * before < 0:
            reversal_magnitude = abs(current - before)
            if reversal_magnitude > COUNTERSTEER_MIN_ANGLE_DEG:
                events.append({
                    "sample": i,
                    "track_pct": round(dist_data[i] * 100, 2) if dist_data else None,
                    "reversal_deg": round(reversal_magnitude, 1),
                    "type": "countersteer_detected",
                })
    
    return events


def analyze_corner_balance(
    steering_data: list,
    yaw_data: list,
    speed_data: list,
    dist_data: list,
    brake_data: list,
    throttle_data: list,
    turn: dict,
) -> dict:
    """Analyze balance for a specific corner, separating spins from saves."""
    start_pct = turn["start"]
    end_pct = turn["end"]
    
    understeer_count = 0
    oversteer_count = 0
    spin_count = 0
    total_samples = 0
    max_yaw = 0
    max_saveable_yaw = 0  # Highest yaw that wasn't a spin
    entry_issues = []
    exit_issues = []
    
    for i, dist in enumerate(dist_data):
        if not (start_pct <= dist <= end_pct):
            continue
        
        total_samples += 1
        steering_deg = abs(rad_to_deg(steering_data[i]))
        yaw_deg_s = abs(rad_to_deg(yaw_data[i]))
        speed_ms = speed_data[i]
        
        if yaw_deg_s > max_yaw:
            max_yaw = yaw_deg_s
        
        # Check for spin first
        if yaw_deg_s > SPIN_THRESHOLD_DEG_S:
            spin_count += 1
            continue  # Don't analyze spins as balance issues
        
        if yaw_deg_s > max_saveable_yaw:
            max_saveable_yaw = yaw_deg_s
        
        if speed_ms < MIN_ANALYSIS_SPEED_MS or steering_deg < MIN_STEERING_DEG:
            continue
        
        expected_yaw = calculate_expected_yaw_rate(steering_deg, speed_ms)
        if expected_yaw < 1.0:
            continue
        
        ratio = yaw_deg_s / expected_yaw
        
        # Track position within corner (0-1)
        corner_progress = (dist - start_pct) / (end_pct - start_pct)
        phase = "entry" if corner_progress < 0.5 else "exit"
        
        if ratio < UNDERSTEER_THRESHOLD:
            understeer_count += 1
            if phase == "entry":
                entry_issues.append("understeer")
            else:
                exit_issues.append("understeer")
                
        elif ratio > OVERSTEER_THRESHOLD:
            oversteer_count += 1
            if phase == "entry":
                entry_issues.append("oversteer")
            else:
                exit_issues.append("oversteer")
    
    # FACTS ONLY - raw counts, no diagnosis
    result = {
        "samples": total_samples,
        "understeer_count": understeer_count,
        "oversteer_count": oversteer_count,
        "spin_count": spin_count,
        "max_yaw_deg_s": round(max_yaw, 1),
        "max_saveable_yaw_deg_s": round(max_saveable_yaw, 1),
        "entry_understeer_count": entry_issues.count("understeer"),
        "entry_oversteer_count": entry_issues.count("oversteer"),
        "exit_understeer_count": exit_issues.count("understeer"),
        "exit_oversteer_count": exit_issues.count("oversteer"),
    }
    
    return result


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_car_balance(ibt_path: str, track_id: Optional[str] = None, lap: str = "all") -> dict:
    """
    Main analysis function for car balance.
    
    Args:
        ibt_path: Path to IBT file
        track_id: Track ID for corner-specific analysis
        lap: Which lap to analyze ("all", "fastest", or lap number)
    
    Returns:
        dict with comprehensive balance analysis including:
        - Steering response ratio (understeer/oversteer detection)
        - Tire temperature correlation (grip and driving style)
        - Input smoothness score (steering aggression)
        - Delta correlation (time lost to balance issues)
    """
    ibt = IBT()
    
    try:
        ibt.open(ibt_path)
    except Exception as e:
        return {"error": f"Failed to open IBT file: {str(e)}"}
    
    available = set(ibt.var_headers_names or [])
    
    # Check required channels
    required = ["SteeringWheelAngle", "YawRate", "Speed", "LapDistPct"]
    missing = [c for c in required if c not in available]
    if missing:
        ibt.close()
        return {"error": f"Missing required channels: {missing}"}
    
    # Load core data
    steering_data = ibt.get_all("SteeringWheelAngle")
    yaw_data = ibt.get_all("YawRate")
    speed_data = ibt.get_all("Speed")
    dist_data = ibt.get_all("LapDistPct")
    brake_data = ibt.get_all("Brake") if "Brake" in available else None
    throttle_data = ibt.get_all("Throttle") if "Throttle" in available else None
    
    # Load delta data for time loss correlation
    delta_data = None
    if "LapDeltaToSessionBestLap" in available:
        delta_data = ibt.get_all("LapDeltaToSessionBestLap")
    
    # Load tire temperature data
    tire_temps = {
        "LF": {"L": None, "M": None, "R": None},
        "RF": {"L": None, "M": None, "R": None},
        "LR": {"L": None, "M": None, "R": None},
        "RR": {"L": None, "M": None, "R": None},
    }
    
    # iRacing tire temp channels
    # NOTE: Surface temps (LFtempL) are dynamic and useful for driving style analysis
    # Carcass temps (LFtempCL) mostly stay at base value, only spike under load
    # VRS uses surface temps - so should we!
    temp_channels = {
        "LF": ["LFtempL", "LFtempM", "LFtempR"],  # Surface temps (dynamic)
        "RF": ["RFtempL", "RFtempM", "RFtempR"],
        "LR": ["LRtempL", "LRtempM", "LRtempR"],
        "RR": ["RRtempL", "RRtempM", "RRtempR"],
    }
    
    # Load surface temps (preferred for driving style analysis)
    for corner, channels in temp_channels.items():
        for i, pos in enumerate(["L", "M", "R"]):
            surface_ch = channels[i]
            carcass_ch = surface_ch.replace("temp", "tempC")  # e.g., LFtempL -> LFtempCL
            
            # Prefer surface temps, fall back to carcass
            if surface_ch in available:
                tire_temps[corner][pos] = ibt.get_all(surface_ch)
            elif carcass_ch in available:
                tire_temps[corner][pos] = ibt.get_all(carcass_ch)
    
    # Load ambient conditions
    ambient = {}
    if "TrackTempCrew" in available:
        track_temp = ibt.get_all("TrackTempCrew")
        ambient["track_temp_c"] = round(statistics.mean(track_temp), 1) if track_temp else None
    if "AirTemp" in available:
        air_temp = ibt.get_all("AirTemp")
        ambient["air_temp_c"] = round(statistics.mean(air_temp), 1) if air_temp else None
    if "TrackUsage" in available or "SessionFlags" in available:
        # Track rubber buildup indicator
        ambient["note"] = "Track rubber state not directly available in telemetry"
    
    sample_count = len(steering_data)
    tick_rate = ibt._header.tick_rate if ibt._header else 60
    
    # Load track data if available
    track_data = load_track_data(track_id) if track_id else None
    
    # Main analysis
    result = {
        "file": Path(ibt_path).name,
        "track_id": track_id,
        "samples": sample_count,
        "duration_seconds": round(sample_count / tick_rate, 1),
    }
    
    # Add ambient conditions if available
    if ambient:
        result["ambient_conditions"] = ambient
    
    # Overall balance analysis
    result["overall_balance"] = analyze_steering_response(
        steering_data, yaw_data, speed_data, dist_data, brake_data, throttle_data
    )
    
    # ===========================================================================
    # NEW: Input Smoothness Analysis
    # ===========================================================================
    result["input_smoothness"] = analyze_input_smoothness(steering_data, tick_rate)
    
    # ===========================================================================
    # NEW: Tire Temperature Analysis (using cornering temps, not session avg)
    # ===========================================================================
    result["tire_analysis"] = analyze_tire_temperatures(
        tire_temps["LF"], tire_temps["RF"], tire_temps["LR"], tire_temps["RR"],
        steering_data, speed_data
    )
    
    # ===========================================================================
    # NEW: Delta Correlation (time lost to balance events)
    # ===========================================================================
    if delta_data:
        # Collect all balance events for delta correlation
        all_events = []
        balance = result["overall_balance"]
        
        # Add understeer events
        for event in balance.get("understeer_samples", []):
            event["type"] = "understeer"
            all_events.append(event)
        
        # Add oversteer events
        for event in balance.get("oversteer_samples", []):
            event["type"] = "oversteer"
            all_events.append(event)
        
        # Add spin events
        for event in balance.get("spins", {}).get("events", []):
            event["type"] = "spin"
            all_events.append(event)
        
        result["delta_correlation"] = analyze_delta_correlation(
            delta_data, all_events, tick_rate
        )
    else:
        result["delta_correlation"] = {"available": False, "note": "No delta data in telemetry"}
    
    # Countersteer detection (oversteer saves)
    countersteer_events = detect_countersteer_events(steering_data, dist_data)
    result["countersteer_events"] = {
        "count": len(countersteer_events),
        "samples": countersteer_events[:15],  # First 15
    }
    
    # Corner-by-corner analysis (raw facts per corner)
    if track_data and "turn" in track_data:
        corners = {}
        for turn in track_data["turn"]:
            corner_analysis = analyze_corner_balance(
                steering_data, yaw_data, speed_data, dist_data,
                brake_data, throttle_data, turn
            )
            corners[turn["name"]] = corner_analysis
        result["corners"] = corners
    
    ibt.close()
    return result


# =============================================================================
# CLI
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Analyze car balance (understeer/oversteer) from IBT telemetry"
    )
    parser.add_argument("ibt_file", help="Path to IBT telemetry file")
    parser.add_argument("--track", help="Track ID for corner analysis (e.g., oschersleben-gp)")
    parser.add_argument("--lap", default="all", help="Lap to analyze: 'all', 'fastest', or lap number")
    parser.add_argument("--pretty", action="store_true", help="Pretty print JSON output")
    
    args = parser.parse_args()
    
    result = analyze_car_balance(args.ibt_file, args.track, args.lap)
    
    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))


if __name__ == "__main__":
    main()

