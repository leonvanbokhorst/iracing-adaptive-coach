#!/usr/bin/env python3
"""
Track Data Loader (FACTS ONLY)

Loads and parses track data JSON files containing corner/straight definitions.
Little Padawan uses this to map telemetry data to specific track locations.

Track Data Source:
    All track data sourced from Lovely Sim Racing Track Data Project
    https://github.com/Lovely-Sim-Racing/lovely-track-data
    © 2025 Lovely Sim Racing | Licensed under CC BY-NC-SA 4.0

Usage:
    from tools.core.track_data_loader import load_track_data
    
    track_data = load_track_data('winton-national')
    # Returns parsed track data with corners, straights, sectors

Output: Dictionary with track data structure
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_track_data_path() -> Path:
    """Get the path to the track data directory."""
    # Assume we're in tools/core/ and need to go up to tracks/track-data/
    current_file = Path(__file__)
    project_root = current_file.parent.parent.parent
    track_data_dir = project_root / "tracks" / "track-data"
    return track_data_dir


def find_track_data_file(track_id: str) -> Optional[Path]:
    """
    Find track data JSON file by track ID.
    
    Args:
        track_id: Track identifier (e.g. 'winton-national', 'rudskogen')
    
    Returns:
        Path to JSON file if found, None otherwise
    """
    track_data_dir = get_track_data_path()
    
    # Try exact match first
    exact_path = track_data_dir / f"{track_id}.json"
    if exact_path.exists():
        return exact_path
    
    # Try case-insensitive search
    for json_file in track_data_dir.glob("*.json"):
        if json_file.stem.lower() == track_id.lower():
            return json_file
    
    return None


def load_track_data(track_id: str) -> Dict[str, Any]:
    """
    Load track data from JSON file.
    
    Args:
        track_id: Track identifier (e.g. 'winton-national', 'rudskogen')
    
    Returns:
        Dictionary with track data:
        {
            'name': str,
            'trackId': str,
            'country': str,
            'length': float (meters),
            'turn': List[{name, start, end}],
            'straight': List[{name, start, end}],
            'sector': List[{name, marker}]
        }
    
    Raises:
        FileNotFoundError: If track data file not found
        json.JSONDecodeError: If JSON is invalid
    """
    track_file = find_track_data_file(track_id)
    
    if not track_file:
        available_tracks = list_available_tracks()
        raise FileNotFoundError(
            f"Track data not found for '{track_id}'.\n"
            f"Available tracks: {', '.join(available_tracks)}"
        )
    
    with open(track_file, 'r') as f:
        track_data = json.load(f)
    
    return track_data


def list_available_tracks() -> List[str]:
    """
    List all available track data files.
    
    Returns:
        List of track IDs (filenames without .json)
    """
    track_data_dir = get_track_data_path()
    
    if not track_data_dir.exists():
        return []
    
    tracks = [f.stem for f in track_data_dir.glob("*.json")]
    return sorted(tracks)


def get_track_info(track_id: str) -> Dict[str, Any]:
    """
    Get basic track information.
    
    Args:
        track_id: Track identifier
    
    Returns:
        Dictionary with basic info:
        {
            'name': str,
            'country': str,
            'length': float,
            'num_turns': int,
            'num_straights': int,
            'num_sectors': int
        }
    """
    track_data = load_track_data(track_id)
    
    return {
        'name': track_data.get('name', 'Unknown'),
        'country': track_data.get('country', 'Unknown'),
        'length': track_data.get('length', 0),
        'num_turns': len(track_data.get('turn', [])),
        'num_straights': len(track_data.get('straight', [])),
        'num_sectors': len(track_data.get('sector', []))
    }


def main():
    """Test the track data loader."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python track_data_loader.py <track_id>")
        print("\nAvailable tracks:")
        for track in list_available_tracks():
            print(f"  - {track}")
        sys.exit(1)
    
    track_id = sys.argv[1]
    
    try:
        # Load track data
        track_data = load_track_data(track_id)
        
        # Get basic info
        info = get_track_info(track_id)
        
        print(f"\n=== {info['name']} ===")
        print(f"Country: {info['country']}")
        print(f"Length: {info['length']}m")
        print(f"Turns: {info['num_turns']}")
        print(f"Straights: {info['num_straights']}")
        print(f"Sectors: {info['num_sectors']}")
        
        print(f"\nTurn List:")
        for turn in track_data['turn']:
            length_pct = (turn['end'] - turn['start']) * 100
            print(f"  {turn['start']:.1%} - {turn['end']:.1%} ({length_pct:.1f}%): {turn['name']}")
        
        print(f"\nStraight List:")
        for straight in track_data['straight']:
            length_pct = (straight['end'] - straight['start']) * 100
            print(f"  {straight['start']:.1%} - {straight['end']:.1%} ({length_pct:.1f}%): {straight['name']}")
        
        # Output JSON for tools
        print(f"\nJSON Output:")
        print(json.dumps(track_data, indent=2))
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

