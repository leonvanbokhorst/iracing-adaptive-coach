#!/usr/bin/env python3
"""
Demo: Corner-Specific Analysis Enhancement

Shows what the new corner-context feature looks like on Master Lonn's data.
"""

import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.core.track_data_loader import load_track_data
from tools.core.corner_identifier import identify_location, get_progress_description


def enhance_comparison_with_corners(comparison_json_path, track_id):
    """Add corner context to existing comparison JSON"""
    
    # Load existing comparison
    with open(comparison_json_path, 'r') as f:
        comparison = json.load(f)
    
    # Load track data
    track_data = load_track_data(track_id)
    
    print(f"\n{'='*80}")
    print(f"ENHANCED CORNER-SPECIFIC ANALYSIS")
    print(f"Track: {track_data['name']}")
    print(f"{'='*80}\n")
    
    # Enhance distance_comparison points with corner context
    print("📍 KEY TELEMETRY POINTS WITH CORNER CONTEXT:")
    print("-" * 80)
    
    for point in comparison.get('distance_comparison', []):
        dist_pct = point['distance_pct']
        location = identify_location(dist_pct, track_data)
        
        progress = get_progress_description(location['progress_through'])
        speed_diff = point.get('speed_diff', 0)
        
        status = "✅" if speed_diff > 0 else "⚠️" if speed_diff > -1 else "❌"
        
        print(f"\n{int(dist_pct * 100):3d}% | {status} {location['name']:30s} ({location['type']:10s}, {progress:10s})")
        print(f"      | Speed: {point['current_speed']:5.1f} m/s vs {point['reference_speed']:5.1f} m/s")
        print(f"      | Diff:  {speed_diff:+5.2f} m/s")
        
        if 'current_lat_g' in point:
            lat_g_diff = point.get('lat_g_diff', 0)
            print(f"      | Lat G: {point['current_lat_g']:5.2f}G vs {point['reference_lat_g']:5.2f}G ({lat_g_diff:+.2f}G)")
    
    # Analyze speed losses by corner
    print(f"\n\n{'='*80}")
    print("🔍 SPEED LOSS BY CORNER:")
    print("-" * 80)
    
    # Group by corner
    corner_losses = {}
    for point in comparison.get('distance_comparison', []):
        dist_pct = point['distance_pct']
        location = identify_location(dist_pct, track_data)
        corner_name = location['name']
        speed_diff = point.get('speed_diff', 0)
        
        if corner_name not in corner_losses:
            corner_losses[corner_name] = {
                'type': location['type'],
                'speeds': [],
                'points': []
            }
        
        corner_losses[corner_name]['speeds'].append(speed_diff)
        corner_losses[corner_name]['points'].append(point)
    
    # Calculate average loss per corner and sort
    corner_summary = []
    for corner_name, data in corner_losses.items():
        avg_loss = sum(data['speeds']) / len(data['speeds'])
        max_loss = min(data['speeds'])  # Most negative = biggest loss
        
        corner_summary.append({
            'name': corner_name,
            'type': data['type'],
            'avg_loss': avg_loss,
            'max_loss': max_loss,
            'points': len(data['speeds'])
        })
    
    # Sort by average loss
    corner_summary.sort(key=lambda x: x['avg_loss'])
    
    print(f"\n{'Corner':<35s} {'Type':<10s} {'Avg Loss':>10s} {'Max Loss':>10s}")
    print("-" * 80)
    
    for corner in corner_summary:
        status = "✅" if corner['avg_loss'] > 0 else "⚠️" if corner['avg_loss'] > -1 else "❌"
        print(f"{status} {corner['name']:<33s} {corner['type']:<10s} "
              f"{corner['avg_loss']:+9.2f} m/s {corner['max_loss']:+9.2f} m/s")
    
    # Top 3 problem corners
    print(f"\n\n{'='*80}")
    print("🎯 TOP 3 FOCUS AREAS (Biggest Losses):")
    print("-" * 80)
    
    problem_corners = [c for c in corner_summary if c['avg_loss'] < 0][:3]
    
    for i, corner in enumerate(problem_corners, 1):
        print(f"\n{i}. {corner['name']} ({corner['type']})")
        print(f"   Average speed loss: {corner['avg_loss']:.2f} m/s")
        print(f"   Maximum speed loss: {corner['max_loss']:.2f} m/s")
        
        # Find where the max loss occurs
        for point in corner_losses[corner['name']]['points']:
            if abs(point['speed_diff'] - corner['max_loss']) < 0.01:
                location = identify_location(point['distance_pct'], track_data)
                progress = get_progress_description(location['progress_through'])
                print(f"   Worst point: {progress} ({point['distance_pct']:.0%} lap distance)")
                
                if 'current_lat_g' in point:
                    print(f"   Lateral G: {point['current_lat_g']:.2f}G (Eric: {point['reference_lat_g']:.2f}G)")
                    if point['current_lat_g'] > point['reference_lat_g']:
                        print(f"   ⚠️  You're working HARDER ({point['lat_g_diff']:+.2f}G more) but going SLOWER!")
                        print(f"   💡 Diagnosis: Line issue or overdriving (fighting the car)")
                
                break
    
    print(f"\n{'='*80}\n")


def main():
    # Demo with Master Lonn's Winton data
    comparison_file = project_root / "weeks" / "week03" / "comparison" / "lonn-vs-eric-wong-telemetry-comparison.json"
    track_id = "winton-national"
    
    if not comparison_file.exists():
        print(f"Error: Comparison file not found: {comparison_file}")
        sys.exit(1)
    
    enhance_comparison_with_corners(comparison_file, track_id)


if __name__ == "__main__":
    main()

