#!/usr/bin/env python3
"""
Standings Progression Visualization

Creates LEARNING-FOCUSED visualizations of season progression:
- iRating trajectory with trend analysis
- Position climb visualization
- Division progression
- Percentile rankings radar

Only generates charts when they help understand patterns and trends.

Usage:
    python tools/coach/visualize_standings_progression.py <week_folders...>
    
Example:
    python tools/coach/visualize_standings_progression.py \
        data/standings/week01 \
        data/standings/week02 \
        data/standings/week03

Output:
    Saves charts to weeks/progression/ folder
"""

import sys
import json
import subprocess
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime


def run_analyzer(csv_path, custid):
    """Run the standings analyzer tool"""
    result = subprocess.run(
        ['uv', 'run', 'python', 'tools/coach/analyze_standings.py', str(csv_path), str(custid)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    if result.returncode != 0:
        print(f"Error running analyzer: {result.stderr}", file=sys.stderr)
        return None
    
    return json.loads(result.stdout)


def collect_weekly_data(week_folders, custid):
    """Collect data from multiple weeks"""
    weekly_data = []
    
    for folder in week_folders:
        folder_path = Path(folder)
        
        # Find CSV in folder
        csv_files = list(folder_path.glob("season-driver_*.csv"))
        
        if not csv_files:
            print(f"⚠️  No standings CSV found in {folder}")
            continue
        
        csv_path = csv_files[0]
        
        # Extract week number
        week_num = int(folder_path.name.replace('week', ''))
        
        print(f"📊 Analyzing Week {week_num:02d}...")
        
        # Run analysis
        data = run_analyzer(csv_path, custid)
        
        if data:
            weekly_data.append({
                'week': week_num,
                'data': data
            })
    
    return sorted(weekly_data, key=lambda x: x['week'])


def create_irating_progression(weekly_data, output_dir):
    """Create iRating progression chart with trend analysis"""
    weeks = [w['week'] for w in weekly_data]
    iratings = [w['data']['driver']['irating'] for w in weekly_data]
    
    # Calculate trend
    if len(weeks) > 1:
        avg_change = (iratings[-1] - iratings[0]) / (len(weeks) - 1)
        trend_line = [iratings[0] + avg_change * i for i in range(len(weeks))]
    else:
        trend_line = iratings
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot actual progression
    ax.plot(weeks, iratings, marker='o', linewidth=2, markersize=8, 
            color='#2E86AB', label='Actual iRating')
    
    # Plot trend line
    if len(weeks) > 1:
        ax.plot(weeks, trend_line, linestyle='--', linewidth=1, 
                color='#A23B72', alpha=0.7, label=f'Trend ({avg_change:+.1f}/week)')
    
    # Highlight gains/losses
    for i in range(1, len(weeks)):
        change = iratings[i] - iratings[i-1]
        color = '#06A77D' if change > 0 else '#D62246'
        ax.annotate(f'{change:+.0f}', 
                   xy=(weeks[i], iratings[i]), 
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   color=color,
                   weight='bold')
    
    # Mark starting and current
    ax.scatter(weeks[0], iratings[0], s=150, color='#F18F01', 
              marker='s', zorder=5, label='Season Start')
    ax.scatter(weeks[-1], iratings[-1], s=150, color='#06A77D', 
              marker='*', zorder=5, label='Current')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('iRating', fontsize=12, weight='bold')
    ax.set_title('iRating Progression - Season 01 2026', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    # Set integer x-axis
    ax.set_xticks(weeks)
    
    plt.tight_layout()
    
    output_path = output_dir / 'irating_progression.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")
    
    return {
        'starting_irating': iratings[0],
        'current_irating': iratings[-1],
        'total_change': iratings[-1] - iratings[0],
        'avg_change_per_week': avg_change if len(weeks) > 1 else 0
    }


def create_position_climb(weekly_data, output_dir):
    """Create position climb visualization"""
    weeks = [w['week'] for w in weekly_data]
    positions = [w['data']['driver']['position'] for w in weekly_data]
    total_drivers = weekly_data[0]['data']['driver']['total_drivers']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Invert y-axis so lower position (better) is higher on chart
    ax.invert_yaxis()
    
    # Plot progression
    ax.plot(weeks, positions, marker='o', linewidth=2, markersize=8,
           color='#2E86AB')
    
    # Fill area to show "distance from bottom"
    ax.fill_between(weeks, positions, total_drivers, 
                    alpha=0.2, color='#06A77D', 
                    label=f'Beating {total_drivers - positions[-1]} drivers')
    
    # Annotate position changes
    for i in range(1, len(weeks)):
        change = positions[i-1] - positions[i]  # Positive = moved up
        if change != 0:
            color = '#06A77D' if change > 0 else '#D62246'
            symbol = '↑' if change > 0 else '↓'
            ax.annotate(f'{symbol}{abs(change)}', 
                       xy=(weeks[i], positions[i]),
                       xytext=(0, -15 if change > 0 else 15),
                       textcoords='offset points',
                       ha='center',
                       fontsize=9,
                       color=color,
                       weight='bold')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('Position (lower is better)', fontsize=12, weight='bold')
    ax.set_title(f'Season Position Climb (out of {total_drivers:,} drivers)', 
                fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best')
    
    # Set integer x-axis
    ax.set_xticks(weeks)
    
    plt.tight_layout()
    
    output_path = output_dir / 'position_climb.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")
    
    return {
        'starting_position': positions[0],
        'current_position': positions[-1],
        'positions_gained': positions[0] - positions[-1]
    }


def create_percentile_progression(weekly_data, output_dir):
    """Create percentile progression for key metrics"""
    weeks = [w['week'] for w in weekly_data]
    
    # Metrics to track
    metrics = ['points', 'wins', 'poles', 'irating']
    metric_labels = {
        'points': 'Points',
        'wins': 'Wins',
        'poles': 'Poles',
        'irating': 'iRating'
    }
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#06A77D']
    
    for i, metric in enumerate(metrics):
        percentiles = []
        for w in weekly_data:
            if metric in w['data']['percentiles']:
                percentiles.append(w['data']['percentiles'][metric]['better_than_percent'])
            else:
                percentiles.append(None)
        
        # Filter out None values
        valid_weeks = [weeks[j] for j in range(len(weeks)) if percentiles[j] is not None]
        valid_percentiles = [p for p in percentiles if p is not None]
        
        if valid_percentiles:
            ax.plot(valid_weeks, valid_percentiles, 
                   marker='o', linewidth=2, markersize=6,
                   color=colors[i], label=metric_labels[metric])
    
    # Reference lines
    ax.axhline(y=50, color='gray', linestyle=':', alpha=0.5, label='Median (50th %ile)')
    ax.axhline(y=75, color='gray', linestyle='--', alpha=0.5, label='Top Quartile (75th %ile)')
    ax.axhline(y=90, color='gray', linestyle='-.', alpha=0.5, label='Elite (90th %ile)')
    
    ax.set_xlabel('Week', fontsize=12, weight='bold')
    ax.set_ylabel('Better Than (Percentile)', fontsize=12, weight='bold')
    ax.set_title('Percentile Rankings Progression', fontsize=14, weight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', ncol=2)
    ax.set_ylim(0, 100)
    
    # Set integer x-axis
    ax.set_xticks(weeks)
    
    plt.tight_layout()
    
    output_path = output_dir / 'percentile_progression.png'
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")


def generate_summary_report(weekly_data, stats, output_dir):
    """Generate a markdown summary with the visualizations"""
    first_week = weekly_data[0]['week']
    last_week = weekly_data[-1]['week']
    
    report = f"""# Season Progression Report (Week {first_week:02d} → Week {last_week:02d})

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Weeks Analyzed:** {len(weekly_data)}

---

## 📈 Progression Summary

### iRating Journey

![iRating Progression](assets/irating_progression.png)

- **Starting iRating:** {stats['irating']['starting_irating']}
- **Current iRating:** {stats['irating']['current_irating']}
- **Total Gain:** {stats['irating']['total_change']:+.0f} points
- **Average per Week:** {stats['irating']['avg_change_per_week']:+.1f} points

### Position Climb

![Position Climb](assets/position_climb.png)

- **Starting Position:** {stats['position']['starting_position']:,}
- **Current Position:** {stats['position']['current_position']:,}
- **Positions Gained:** {stats['position']['positions_gained']:+,}

### Percentile Rankings

![Percentile Progression](assets/percentile_progression.png)

Track your standing across multiple metrics week-over-week.

---

## 📊 Week-by-Week Breakdown

"""
    
    for week_info in weekly_data:
        week = week_info['week']
        driver = week_info['data']['driver']
        
        report += f"""### Week {week:02d}

- **Position:** {driver['position']:,} / {driver['total_drivers']:,}
- **iRating:** {driver['irating']}
- **Points:** {driver['points']:.1f}
- **Wins:** {driver['wins']}
- **Starts:** {driver['starts']}
- **Incidents/Race:** {driver.get('incidents_per_race', 0):.2f}

"""
    
    report += """---

**Note:** These visualizations help identify trends and patterns in your season progression. Use them to:
- Spot momentum shifts (accelerating or plateauing improvement)
- Identify metrics that need focus (lagging percentiles)
- Track consistency (smooth progression vs volatile swings)
- Set realistic goals based on your actual trajectory
"""
    
    # Save report
    report_path = output_dir / 'progression-report.md'
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"✅ Saved: {report_path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: visualize_standings_progression.py <week_folder1> [week_folder2] ...")
        print("\nExample:")
        print("  python tools/coach/visualize_standings_progression.py data/standings/week01 data/standings/week02")
        sys.exit(1)
    
    week_folders = sys.argv[1:]
    custid = 981717  # Master Lonn's custid
    
    print(f"🎨 Creating progression visualizations for {len(week_folders)} weeks...")
    
    # Collect data from all weeks
    weekly_data = collect_weekly_data(week_folders, custid)
    
    if len(weekly_data) < 1:
        print("❌ Not enough data to create visualizations (need at least 1 week)")
        sys.exit(1)
    
    # Create output directory with assets subfolder
    base_dir = Path('weeks/progression')
    base_dir.mkdir(parents=True, exist_ok=True)
    output_dir = base_dir / 'assets'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n📊 Generating charts...")
    
    # Create visualizations
    irating_stats = create_irating_progression(weekly_data, output_dir)
    position_stats = create_position_climb(weekly_data, output_dir)
    create_percentile_progression(weekly_data, output_dir)
    
    # Generate summary report
    stats = {
        'irating': irating_stats,
        'position': position_stats
    }
    
    generate_summary_report(weekly_data, stats, base_dir)
    
    print(f"\n✅ All visualizations saved to: {output_dir}")
    print(f"\n📈 Key Insights:")
    print(f"   iRating: {irating_stats['starting_irating']} → {irating_stats['current_irating']} ({irating_stats['total_change']:+.0f})")
    print(f"   Position: {position_stats['starting_position']:,} → {position_stats['current_position']:,} ({position_stats['positions_gained']:+,})")


if __name__ == '__main__':
    main()

