#!/usr/bin/env python3
"""
Weekly Standings Comparison Tool

Compares two weeks of standings to track progression:
- Position changes
- iRating movement
- Division changes
- Points progression
- Performance trends

Usage:
    python tools/coach/compare_weekly_standings.py <week1_csv> <week2_csv> <custid>
    
Example:
    python tools/coach/compare_weekly_standings.py \
        data/standings/week01/season-driver_*.csv \
        data/standings/week02/season-driver_*.csv \
        981717

Output:
    JSON with week-over-week changes and trends
"""

import sys
import json
import subprocess
from pathlib import Path


def run_analyzer(csv_path, custid):
    """Run the standings analyzer tool"""
    result = subprocess.run(
        ['uv', 'run', 'python', 'tools/coach/analyze_standings.py', csv_path, str(custid)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    if result.returncode != 0:
        print(f"Error running analyzer: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    
    return json.loads(result.stdout)


def calculate_changes(week1_data, week2_data):
    """Calculate changes between two weeks"""
    w1 = week1_data['driver']
    w2 = week2_data['driver']
    
    changes = {
        'position': {
            'week1': w1['position'],
            'week2': w2['position'],
            'change': w1['position'] - w2['position'],  # Positive = moved up
            'direction': 'up' if w1['position'] > w2['position'] else 'down' if w1['position'] < w2['position'] else 'same'
        },
        'irating': {
            'week1': w1['irating'],
            'week2': w2['irating'],
            'change': w2['irating'] - w1['irating'],
            'percent_change': round((w2['irating'] - w1['irating']) / w1['irating'] * 100, 2)
        },
        'division': {
            'week1': w1['division'],
            'week2': w2['division'],
            'change': w1['division'] - w2['division'],  # Positive = promoted (lower div number = better)
            'promoted': w1['division'] > w2['division']
        },
        'points': {
            'week1': w1['points'],
            'week2': w2['points'],
            'change': w2['points'] - w1['points']
        },
        'races': {
            'week1_starts': w1['starts'],
            'week2_starts': w2['starts'],
            'new_races': w2['starts'] - w1['starts']
        },
        'wins': {
            'week1': w1['wins'],
            'week2': w2['wins'],
            'new_wins': w2['wins'] - w1['wins']
        },
        'poles': {
            'week1': w1['poles'],
            'week2': w2['poles'],
            'new_poles': w2['poles'] - w1['poles']
        },
        'incidents': {
            'week1_per_start': w1.get('incidents_per_start', 0),
            'week2_per_start': w2.get('incidents_per_start', 0),
            'change': w2.get('incidents_per_start', 0) - w1.get('incidents_per_start', 0)
        },
        'avg_finish': {
            'week1': w1['avgfinish'],
            'week2': w2['avgfinish'],
            'change': w2['avgfinish'] - w1['avgfinish'],  # Negative = better
            'improving': w2['avgfinish'] < w1['avgfinish']
        }
    }
    
    # Percentile changes
    changes['percentile_changes'] = {}
    
    for metric in ['position', 'points', 'irating', 'wins', 'poles']:
        if metric in week1_data['percentiles'] and metric in week2_data['percentiles']:
            w1_pct = week1_data['percentiles'][metric]['better_than_percent']
            w2_pct = week2_data['percentiles'][metric]['better_than_percent']
            
            changes['percentile_changes'][metric] = {
                'week1': w1_pct,
                'week2': w2_pct,
                'change': w2_pct - w1_pct,
                'improving': w2_pct > w1_pct
            }
    
    return changes


def generate_comparison_report(changes, week1_num, week2_num):
    """Generate a human-readable comparison summary"""
    summary = {
        'week_range': f"Week {week1_num} → Week {week2_num}",
        'headline_stats': {},
        'progression': {},
        'insights': []
    }
    
    # Headline stats
    pos_change = changes['position']['change']
    if pos_change > 0:
        summary['headline_stats']['position'] = f"↑ {pos_change} positions (P{changes['position']['week1']} → P{changes['position']['week2']})"
    elif pos_change < 0:
        summary['headline_stats']['position'] = f"↓ {abs(pos_change)} positions (P{changes['position']['week1']} → P{changes['position']['week2']})"
    else:
        summary['headline_stats']['position'] = f"Steady at P{changes['position']['week2']}"
    
    irating_change = changes['irating']['change']
    if irating_change > 0:
        summary['headline_stats']['irating'] = f"↑ {irating_change} points ({changes['irating']['percent_change']:+.1f}%)"
    elif irating_change < 0:
        summary['headline_stats']['irating'] = f"↓ {abs(irating_change)} points ({changes['irating']['percent_change']:.1f}%)"
    else:
        summary['headline_stats']['irating'] = "No change"
    
    # New races
    new_races = changes['races']['new_races']
    summary['headline_stats']['new_races'] = new_races
    
    # New wins/poles
    if changes['wins']['new_wins'] > 0:
        summary['headline_stats']['new_wins'] = f"+{changes['wins']['new_wins']} wins! 🏆"
    
    if changes['poles']['new_poles'] > 0:
        summary['headline_stats']['new_poles'] = f"+{changes['poles']['new_poles']} poles! 🏁"
    
    # Progression analysis
    summary['progression']['irating'] = {
        'gained': irating_change > 0,
        'lost': irating_change < 0,
        'stable': irating_change == 0,
        'value': irating_change
    }
    
    summary['progression']['position'] = {
        'climbed': pos_change > 0,
        'dropped': pos_change < 0,
        'stable': pos_change == 0,
        'value': pos_change
    }
    
    # Division change
    if changes['division']['promoted']:
        summary['progression']['division'] = f"PROMOTED! Division {changes['division']['week1']} → {changes['division']['week2']} 🎉"
    elif changes['division']['change'] < 0:
        summary['progression']['division'] = f"Relegated: Division {changes['division']['week1']} → {changes['division']['week2']}"
    else:
        summary['progression']['division'] = f"Division {changes['division']['week2']} (stable)"
    
    # Insights
    if new_races == 0:
        summary['insights'].append("⚠️ No new races this week - no data to track progression")
    else:
        # iRating per new start
        irating_per_start = irating_change / new_races if new_races > 0 else 0
        summary['insights'].append(f"Average iRating change per new start: {irating_per_start:+.1f}")
        
        # Points change (note: points system is complex, not simple per-race)
        points_change = changes['points']['change']
        if points_change > 5:
            summary['insights'].append(f"Season points increased: {changes['points']['week1']:.1f} → {changes['points']['week2']:.1f} (+{points_change:.1f})")
        elif points_change < -5:
            summary['insights'].append(f"⚠️ Season points decreased: {changes['points']['week1']:.1f} → {changes['points']['week2']:.1f} ({points_change:.1f})")
        
        # Incident rate trend
        inc_change = changes['incidents']['change']
        if abs(inc_change) > 0.5:
            if inc_change > 0:
                summary['insights'].append(f"⚠️ Incident rate increased: {changes['incidents']['week1_per_start']:.2f} → {changes['incidents']['week2_per_start']:.2f} per start")
            else:
                summary['insights'].append(f"✅ Incident rate improved: {changes['incidents']['week1_per_start']:.2f} → {changes['incidents']['week2_per_start']:.2f} per start")
        
        # Percentile improvements
        big_gains = []
        for metric, data in changes['percentile_changes'].items():
            if data['change'] > 5:  # 5+ percentile jump
                big_gains.append(f"{metric.title()} ({data['change']:+.1f}%)")
        
        if big_gains:
            summary['insights'].append(f"📈 Big percentile gains in: {', '.join(big_gains)}")
    
    return summary


def main():
    if len(sys.argv) < 4:
        print("Usage: compare_weekly_standings.py <week1_csv> <week2_csv> <custid>")
        sys.exit(1)
    
    week1_csv = sys.argv[1]
    week2_csv = sys.argv[2]
    custid = sys.argv[3]
    
    # Extract week numbers from paths
    week1_num = int(Path(week1_csv).parts[-2].replace('week', '')) if 'week' in week1_csv else 1
    week2_num = int(Path(week2_csv).parts[-2].replace('week', '')) if 'week' in week2_csv else 2
    
    print(f"📊 Analyzing Week {week1_num} vs Week {week2_num}...")
    
    # Run analysis on both weeks
    week1_data = run_analyzer(week1_csv, custid)
    week2_data = run_analyzer(week2_csv, custid)
    
    # Calculate changes
    changes = calculate_changes(week1_data, week2_data)
    
    # Generate summary
    summary = generate_comparison_report(changes, week1_num, week2_num)
    
    # Output full comparison
    output = {
        'weeks': {
            'week1': week1_num,
            'week2': week2_num
        },
        'changes': changes,
        'summary': summary,
        'week1_data': week1_data,
        'week2_data': week2_data
    }
    
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()

