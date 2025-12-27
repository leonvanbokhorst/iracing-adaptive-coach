#!/usr/bin/env python3
"""
Corner Identifier (FACTS ONLY)

Maps telemetry lap distance percentages to specific track corners/straights.
Pure data matching - no interpretation, no coaching.

Track Data Source:
    Corner/straight definitions from Lovely Sim Racing Track Data Project
    https://github.com/Lovely-Sim-Racing/lovely-track-data

Usage:
    from tools.core.corner_identifier import identify_location, get_corner_at
    
    location = identify_location(0.375, track_data)
    # Returns: {'type': 'turn', 'name': 'Turn 5', ...}

Output: Dictionary with location facts
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any, List

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.core.track_data_loader import load_track_data


def identify_location(lap_dist_pct: float, track_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify which corner/straight/sector a lap distance percentage corresponds to.
    
    Args:
        lap_dist_pct: Lap distance as percentage (0.0 to 1.0)
        track_data: Track data dictionary from load_track_data()
    
    Returns:
        Dictionary with location information:
        {
            'type': 'turn' | 'straight' | 'transition',
            'name': str,
            'start': float,
            'end': float,
            'length_pct': float,
            'progress_through': float (0.0-1.0, how far through this element),
            'sector': str (which sector this is in)
        }
    """
    # Normalize to 0.0-1.0 range
    lap_dist_pct = lap_dist_pct % 1.0
    
    # Check turns first (usually higher priority)
    for turn in track_data.get('turn', []):
        if turn['start'] <= lap_dist_pct <= turn['end']:
            length = turn['end'] - turn['start']
            progress = (lap_dist_pct - turn['start']) / length if length > 0 else 0.5
            
            return {
                'type': 'turn',
                'name': turn['name'],
                'start': turn['start'],
                'end': turn['end'],
                'length_pct': length,
                'progress_through': progress,
                'sector': _get_sector_at(lap_dist_pct, track_data)
            }
    
    # Check straights
    for straight in track_data.get('straight', []):
        if straight['start'] <= lap_dist_pct <= straight['end']:
            length = straight['end'] - straight['start']
            progress = (lap_dist_pct - straight['start']) / length if length > 0 else 0.5
            
            return {
                'type': 'straight',
                'name': straight['name'],
                'start': straight['start'],
                'end': straight['end'],
                'length_pct': length,
                'progress_through': progress,
                'sector': _get_sector_at(lap_dist_pct, track_data)
            }
    
    # If not in any defined corner/straight, it's a transition
    return {
        'type': 'transition',
        'name': 'Transition',
        'start': lap_dist_pct,
        'end': lap_dist_pct,
        'length_pct': 0.0,
        'progress_through': 0.0,
        'sector': _get_sector_at(lap_dist_pct, track_data)
    }


def _get_sector_at(lap_dist_pct: float, track_data: Dict[str, Any]) -> str:
    """
    Determine which sector a lap distance percentage is in.
    
    Args:
        lap_dist_pct: Lap distance as percentage (0.0 to 1.0)
        track_data: Track data dictionary
    
    Returns:
        Sector name (e.g., "1", "2", "3", "4")
    """
    sectors = track_data.get('sector', [])
    if not sectors:
        return "Unknown"
    
    # Sectors are marked by their END points
    # Find the first sector marker >= lap_dist_pct
    for i, sector in enumerate(sectors):
        if lap_dist_pct <= sector['marker']:
            return sector['name']
    
    # If past all markers, we're in the last sector
    return sectors[-1]['name'] if sectors else "Unknown"


def get_corner_at(lap_dist_pct: float, track_id: str) -> Dict[str, Any]:
    """
    Convenience function: load track data and identify location in one call.
    
    Args:
        lap_dist_pct: Lap distance as percentage (0.0 to 1.0)
        track_id: Track identifier (e.g., 'winton-national')
    
    Returns:
        Location dictionary from identify_location()
    """
    track_data = load_track_data(track_id)
    return identify_location(lap_dist_pct, track_data)


def get_progress_description(progress: float) -> str:
    """
    Convert progress through corner (0.0-1.0) to human-readable description.
    
    Args:
        progress: Progress through element (0.0 = start, 1.0 = end)
    
    Returns:
        Human-readable description: "entry", "mid-corner", "exit"
    """
    if progress < 0.33:
        return "entry"
    elif progress < 0.67:
        return "mid-corner"
    else:
        return "exit"


def annotate_telemetry_with_corners(
    telemetry_data: List[Dict[str, Any]], 
    track_data: Dict[str, Any],
    lap_dist_key: str = 'LapDistPct'
) -> List[Dict[str, Any]]:
    """
    Add corner information to telemetry data points.
    
    Args:
        telemetry_data: List of telemetry dictionaries with lap distance
        track_data: Track data dictionary
        lap_dist_key: Key name for lap distance in telemetry data
    
    Returns:
        List of telemetry dictionaries with added 'corner_info' key
    """
    annotated = []
    
    for point in telemetry_data:
        if lap_dist_key not in point:
            # Skip points without lap distance
            annotated.append(point)
            continue
        
        lap_dist = point[lap_dist_key]
        corner_info = identify_location(lap_dist, track_data)
        
        # Add corner info to the point
        annotated_point = point.copy()
        annotated_point['corner_info'] = corner_info
        annotated_point['corner_name'] = corner_info['name']
        annotated_point['corner_type'] = corner_info['type']
        annotated_point['corner_progress'] = get_progress_description(corner_info['progress_through'])
        
        annotated.append(annotated_point)
    
    return annotated


def get_corner_summary(track_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Get summary of all corners with their properties.
    
    Args:
        track_data: Track data dictionary
    
    Returns:
        List of corner summaries with sector and length info
    """
    corners = []
    
    for turn in track_data.get('turn', []):
        length_pct = turn['end'] - turn['start']
        corners.append({
            'name': turn['name'],
            'type': 'turn',
            'start': turn['start'],
            'end': turn['end'],
            'length_pct': length_pct,
            'sector': _get_sector_at((turn['start'] + turn['end']) / 2, track_data)
        })
    
    for straight in track_data.get('straight', []):
        length_pct = straight['end'] - straight['start']
        corners.append({
            'name': straight['name'],
            'type': 'straight',
            'start': straight['start'],
            'end': straight['end'],
            'length_pct': length_pct,
            'sector': _get_sector_at((straight['start'] + straight['end']) / 2, track_data)
        })
    
    # Sort by start position
    corners.sort(key=lambda x: x['start'])
    
    return corners


def main():
    """Test the corner identifier."""
    import sys
    import json
    
    if len(sys.argv) < 3:
        print("Usage: python corner_identifier.py <track_id> <lap_dist_pct>")
        print("\nExample: python corner_identifier.py winton-national 0.375")
        sys.exit(1)
    
    track_id = sys.argv[1]
    lap_dist_pct = float(sys.argv[2])
    
    try:
        # Load track data
        track_data = load_track_data(track_id)
        
        # Identify location
        location = identify_location(lap_dist_pct, track_data)
        
        print(f"\n=== Location at {lap_dist_pct:.1%} lap distance ===")
        print(f"Type: {location['type']}")
        print(f"Name: {location['name']}")
        print(f"Sector: {location['sector']}")
        
        if location['type'] != 'transition':
            print(f"Range: {location['start']:.1%} - {location['end']:.1%}")
            print(f"Length: {location['length_pct']:.1%} of lap")
            print(f"Progress: {location['progress_through']:.0%} through {location['type']}")
            print(f"Position: {get_progress_description(location['progress_through'])}")
        
        # Test some known positions from Master Lonn's data
        print(f"\n=== Testing Key Telemetry Points ===")
        test_points = [
            (0.1, "10% - Should be in T1-T2 chicane"),
            (0.2, "20% - Should be approaching T3"),
            (0.4, "40% - Should be mid-T5 (THE PROBLEM AREA!)"),
            (0.5, "50% - Should be in T7-T8 area"),
            (0.7, "70% - Should be at T10 brake zone")
        ]
        
        for dist, description in test_points:
            loc = identify_location(dist, track_data)
            print(f"{dist:.0%}: {loc['name']} ({loc['type']}, {get_progress_description(loc['progress_through'])}) - {description}")
        
        # Output JSON
        print(f"\nJSON Output:")
        print(json.dumps(location, indent=2))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

