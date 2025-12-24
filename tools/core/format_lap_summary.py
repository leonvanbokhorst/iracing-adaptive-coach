#!/usr/bin/env python3
"""
Lap List Formatter

Condenses lap-by-lap lists to show outliers only (best/worst/median/trend).
Prevents visual clutter in reports.

Usage:
    from tools.core.format_lap_summary import format_lap_summary
    
    summary = format_lap_summary([90.2, 91.5, 90.8, 91.1, 150.3, 89.9, 90.5])
    print(summary['markdown'])
"""

import statistics
from typing import List, Dict, Tuple, Optional


def format_lap_summary(
    lap_times: List[float],
    show_full_list: bool = False,
    include_lap_numbers: bool = True
) -> Dict:
    """
    Format lap times into condensed summary.
    
    Args:
        lap_times: List of lap times in seconds
        show_full_list: If True, include full list in collapsible section
        include_lap_numbers: If True, include lap numbers for best/worst
    
    Returns:
        Dictionary with:
        - markdown: Formatted markdown string
        - best: (time, lap_number)
        - worst: (time, lap_number)
        - median: float
        - std_dev: float
        - trend: str
    """
    
    if not lap_times:
        return {
            'markdown': 'No lap data available.',
            'best': None,
            'worst': None,
            'median': None,
            'std_dev': None,
            'trend': None
        }
    
    # Find best and worst
    best_time = min(lap_times)
    worst_time = max(lap_times)
    best_idx = lap_times.index(best_time) + 1
    worst_idx = lap_times.index(worst_time) + 1
    
    # Calculate stats
    median_time = statistics.median(lap_times)
    std_dev = statistics.stdev(lap_times) if len(lap_times) > 1 else 0.0
    
    # Detect trend
    if len(lap_times) >= 4:
        first_half = lap_times[:len(lap_times)//2]
        second_half = lap_times[len(lap_times)//2:]
        first_avg = statistics.mean(first_half)
        second_avg = statistics.mean(second_half)
        
        if second_avg < first_avg - 0.5:
            trend = "Getting faster"
        elif second_avg > first_avg + 0.5:
            trend = "Getting slower"
        else:
            trend = "Consistent"
    else:
        trend = "Insufficient data"
    
    # Format times
    def format_time(seconds: float) -> str:
        """Format seconds to M:SS.mmm"""
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}:{secs:05.2f}"
    
    # Build markdown
    markdown = f"### Lap Times ({len(lap_times)} clean laps)\n\n"
    markdown += "| Stat | Value |\n"
    markdown += "|------|-------|\n"
    
    if include_lap_numbers:
        markdown += f"| **Best** | **{format_time(best_time)}** (lap {best_idx}) |\n"
        markdown += f"| Median | {format_time(median_time)} |\n"
        markdown += f"| Worst | {format_time(worst_time)} (lap {worst_idx}) |\n"
    else:
        markdown += f"| **Best** | **{format_time(best_time)}** |\n"
        markdown += f"| Median | {format_time(median_time)} |\n"
        markdown += f"| Worst | {format_time(worst_time)} |\n"
    
    markdown += f"| σ | {std_dev:.3f}s |\n\n"
    
    if trend != "Insufficient data":
        markdown += f"Trend: {trend} ({format_time(statistics.mean(lap_times[:len(lap_times)//2]))} → {format_time(statistics.mean(lap_times[len(lap_times)//2:]))})\n"
    
    # Add full list if requested
    if show_full_list:
        markdown += "\n<details>\n<summary>All lap times</summary>\n\n"
        for i, lap_time in enumerate(lap_times, 1):
            marker = " ← NEW PB!" if lap_time == best_time else ""
            markdown += f"{i}. {format_time(lap_time)}{marker}\n"
        markdown += "\n</details>\n"
    
    return {
        'markdown': markdown,
        'best': (best_time, best_idx),
        'worst': (worst_time, worst_idx),
        'median': median_time,
        'std_dev': std_dev,
        'trend': trend
    }


if __name__ == '__main__':
    # Test example
    test_laps = [91.501, 89.970, 89.445, 89.199, 91.580, 88.940, 89.112, 88.858, 88.572, 88.960]
    
    result = format_lap_summary(test_laps, show_full_list=True)
    print(result['markdown'])
    print(f"\nBest: {result['best']}")
    print(f"Worst: {result['worst']}")
    print(f"Trend: {result['trend']}")

