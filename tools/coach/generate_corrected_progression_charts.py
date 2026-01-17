#!/usr/bin/env python3
"""
Generate corrected progression charts with actual historical iRating data.

DEPRECATED: This script contains hardcoded historical data from Season 1 2026.
            For current seasons, use visualize_standings_progression.py instead.
            Kept for reference only.

iRacing exports show current iRating in historical week filters, not the 
historical iRating at that point in time. This script uses the actual 
recorded values from learning_memory.json.

Usage:
    python tools/coach/generate_corrected_progression_charts.py
"""

import warnings
warnings.warn(
    "generate_corrected_progression_charts.py is deprecated. "
    "Use visualize_standings_progression.py for current data.",
    DeprecationWarning,
    stacklevel=2
)

import matplotlib.pyplot as plt
from pathlib import Path

# Actual historical data from learning_memory.json and standings reports
PROGRESSION_DATA = {
    1: {
        'track': 'Jefferson',
        'irating': 1377,  # End of week 01
        'position': 749,
        'total_drivers': 8977,
        'points': 80,
        'wins': 1,
        'starts': 2,
    },
    2: {
        'track': 'Rudskogen', 
        'irating': 1494,  # End of week 02
        'position': 459,
        'total_drivers': 15787,
        'points': 148,
        'wins': 1,
        'starts': 6,
    },
    3: {
        'track': 'Winton',
        'irating': 1601,  # End of week 03
        'position': 209,
        'total_drivers': 21567,
        'points': 235,
        'wins': 2,
        'starts': 8,
    },
    4: {
        'track': 'Lime Rock',
        'irating': 1672,  # End of week 04
        'position': 129,
        'total_drivers': 26375,
        'points': 329,
        'wins': 2,
        'starts': 9,
    },
    5: {
        'track': 'Oschersleben',
        'irating': 1738,  # End of week 05
        'position': 106,
        'total_drivers': 27864,
        'points': 397,
        'wins': 2,
        'starts': 11,
    },
}

STARTING_IRATING = 1238


def create_irating_progression(output_dir: Path):
    """Create iRating progression chart with correct historical data"""
    weeks = list(PROGRESSION_DATA.keys())
    iratings = [PROGRESSION_DATA[w]['irating'] for w in weeks]
    tracks = [PROGRESSION_DATA[w]['track'] for w in weeks]
    
    # Add starting point
    weeks_with_start = [0] + weeks
    iratings_with_start = [STARTING_IRATING] + iratings
    
    # Calculate changes
    changes = [iratings_with_start[i] - iratings_with_start[i-1] for i in range(1, len(iratings_with_start))]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot actual progression
    ax.plot(weeks_with_start, iratings_with_start, marker='o', linewidth=2.5, markersize=10, 
            color='#2E86AB', label='iRating')
    
    # Add trend line
    avg_change = (iratings[-1] - STARTING_IRATING) / len(weeks)
    trend = [STARTING_IRATING + avg_change * i for i in range(len(weeks_with_start))]
    ax.plot(weeks_with_start, trend, linestyle='--', linewidth=1.5, 
            color='#A23B72', alpha=0.7, label=f'Avg Trend ({avg_change:+.0f}/week)')
    
    # Annotate weekly changes
    for i, (week, change) in enumerate(zip(weeks, changes)):
        color = '#06A77D' if change > 0 else '#D62246'
        ax.annotate(f'+{change}', 
                   xy=(week, iratings[i]), 
                   xytext=(0, 15),
                   textcoords='offset points',
                   ha='center',
                   fontsize=10,
                   color=color,
                   weight='bold')
    
    # Mark milestones
    ax.axhline(y=1500, color='#888', linestyle=':', alpha=0.5, label='1500 threshold')
    ax.axhline(y=1800, color='#888', linestyle=':', alpha=0.5)
    
    # Mark start and current
    ax.scatter(0, STARTING_IRATING, s=200, color='#F18F01', 
              marker='s', zorder=5, label=f'Start: {STARTING_IRATING}')
    ax.scatter(weeks[-1], iratings[-1], s=200, color='#06A77D', 
              marker='*', zorder=5, label=f'Current: {iratings[-1]}')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('iRating', fontsize=12, weight='bold')
    ax.set_title(f'iRating Progression: {STARTING_IRATING} → {iratings[-1]} (+{iratings[-1]-STARTING_IRATING})', 
                fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    # Set x-axis ticks
    ax.set_xticks(weeks_with_start)
    ax.set_xticklabels(['Start'] + [f'W{w}' for w in weeks])
    
    # Set y limits with some padding
    ax.set_ylim(1150, 1850)
    
    plt.tight_layout()
    
    output_path = output_dir / 'irating_progression.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")
    return {'start': STARTING_IRATING, 'end': iratings[-1], 'gain': iratings[-1] - STARTING_IRATING}


def create_position_climb(output_dir: Path):
    """Create position climb visualization"""
    weeks = list(PROGRESSION_DATA.keys())
    positions = [PROGRESSION_DATA[w]['position'] for w in weeks]
    total_drivers = [PROGRESSION_DATA[w]['total_drivers'] for w in weeks]
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Invert y-axis so lower position (better) is higher on chart
    ax.invert_yaxis()
    
    # Plot progression
    ax.plot(weeks, positions, marker='o', linewidth=2.5, markersize=10,
           color='#2E86AB', label='Position')
    
    # Fill area to show drivers beaten
    ax.fill_between(weeks, positions, [td for td in total_drivers], 
                    alpha=0.2, color='#06A77D')
    
    # Annotate position changes
    for i in range(1, len(weeks)):
        change = positions[i-1] - positions[i]  # Positive = moved up
        color = '#06A77D' if change > 0 else '#D62246'
        symbol = '↑' if change > 0 else '↓'
        ax.annotate(f'{symbol}{abs(change)}', 
                   xy=(weeks[i], positions[i]),
                   xytext=(0, -20),
                   textcoords='offset points',
                   ha='center',
                   fontsize=10,
                   color=color,
                   weight='bold')
    
    # Add field size annotations
    for i, (week, pos, total) in enumerate(zip(weeks, positions, total_drivers)):
        percentile = (1 - pos/total) * 100
        ax.annotate(f'Top {100-percentile:.1f}%\n({total:,} drivers)', 
                   xy=(week, pos),
                   xytext=(0, 25),
                   textcoords='offset points',
                   ha='center',
                   fontsize=8,
                   color='#666')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('Position (lower = better)', fontsize=12, weight='bold')
    ax.set_title(f'Position Climb: P{positions[0]} → P{positions[-1]} (+{positions[0]-positions[-1]} positions)', 
                fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    
    # Set x-axis ticks
    ax.set_xticks(weeks)
    ax.set_xticklabels([f'W{w}' for w in weeks])
    
    plt.tight_layout()
    
    output_path = output_dir / 'position_climb.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")
    return {'start': positions[0], 'end': positions[-1], 'gained': positions[0] - positions[-1]}


def create_percentile_progression(output_dir: Path):
    """Create percentile progression chart"""
    weeks = list(PROGRESSION_DATA.keys())
    
    # Calculate percentiles
    position_percentiles = []
    irating_percentiles = []
    
    # iRating percentile reference points (approximate from distribution)
    # Based on week 04 standings report: 1672 = 89.4%
    irating_percentile_map = {
        1238: 50,   # Starting point estimate
        1377: 66,   # Week 01
        1494: 79,   # Week 02
        1601: 87,   # Week 03
        1672: 89,   # Week 04
        1738: 92,   # Week 05
    }
    
    for week in weeks:
        data = PROGRESSION_DATA[week]
        pos_pct = (1 - data['position']/data['total_drivers']) * 100
        position_percentiles.append(pos_pct)
        irating_percentiles.append(irating_percentile_map.get(data['irating'], 85))
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Plot both lines
    ax.plot(weeks, position_percentiles, marker='o', linewidth=2.5, markersize=10,
           color='#2E86AB', label='Position Percentile')
    ax.plot(weeks, irating_percentiles, marker='s', linewidth=2.5, markersize=10,
           color='#F18F01', label='iRating Percentile')
    
    # Annotate values
    for i, week in enumerate(weeks):
        ax.annotate(f'{position_percentiles[i]:.1f}%', 
                   xy=(week, position_percentiles[i]),
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   color='#2E86AB')
        ax.annotate(f'{irating_percentiles[i]:.0f}%', 
                   xy=(week, irating_percentiles[i]),
                   xytext=(0, -15),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   color='#F18F01')
    
    # Highlight the gap (outperforming)
    ax.fill_between(weeks, irating_percentiles, position_percentiles,
                    where=[p > i for p, i in zip(position_percentiles, irating_percentiles)],
                    alpha=0.2, color='#06A77D', label='Outperforming iRating')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('Percentile (%)', fontsize=12, weight='bold')
    ax.set_title('Percentile Progression: Results vs Rating', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    ax.set_xticks(weeks)
    ax.set_xticklabels([f'W{w}' for w in weeks])
    ax.set_ylim(50, 102)
    
    plt.tight_layout()
    
    output_path = output_dir / 'percentile_progression.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")


def main():
    output_dir = Path(__file__).parent.parent.parent / 'weeks' / 'progression' / 'assets'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎨 Generating corrected progression charts...\n")
    
    irating_stats = create_irating_progression(output_dir)
    position_stats = create_position_climb(output_dir)
    create_percentile_progression(output_dir)
    
    print(f"\n📈 Summary:")
    print(f"   iRating: {irating_stats['start']} → {irating_stats['end']} (+{irating_stats['gain']})")
    print(f"   Position: P{position_stats['start']} → P{position_stats['end']} (+{position_stats['gained']} positions)")
    print(f"\n✅ All charts saved to: {output_dir}")


if __name__ == '__main__':
    main()
