#!/usr/bin/env python3
"""
Weekly Standings Report Generator

Analyzes season standings and generates a comprehensive markdown report
with statistics, rankings, and insights.

Usage:
    python tools/coach/generate_weekly_standings_report.py <week_number> <standings_csv>
    
Example:
    python tools/coach/generate_weekly_standings_report.py 1 data/standings/week01/season-driver_*.csv

Output:
    Creates markdown report in weeks/weekXX/standings-report.md
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime


def run_analyzer(csv_path, custid):
    """Run the standings analyzer tool"""
    result = subprocess.run(
        ['uv', 'run', 'python', 'tools/coach/analyze_standings.py', csv_path, str(custid)],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent
    )
    
    if result.returncode != 0:
        print(f"Error running analyzer: {result.stderr}")
        sys.exit(1)
    
    return json.loads(result.stdout)


def format_percentile_badge(percentile):
    """Create a visual badge for percentile"""
    if percentile >= 95:
        return "🏆"
    elif percentile >= 90:
        return "⭐"
    elif percentile >= 75:
        return "✨"
    elif percentile >= 50:
        return "📈"
    else:
        return "📊"


def generate_report(week_number, analysis, irating_start=None):
    """Generate markdown report from analysis data"""
    driver = analysis['driver']
    percentiles = analysis['percentiles']
    divisions = analysis['divisions']
    irating_dist = analysis['irating_distribution']
    incidents = analysis['incident_analysis']
    country = analysis['country_analysis']
    correlations = analysis['correlations']
    div_comparison = analysis['division_comparison']
    
    # Calculate iRating change if we have starting iRating
    irating_change = ""
    if irating_start:
        change = driver['irating'] - irating_start
        irating_change = f" (+{change} from starting {irating_start})" if change > 0 else f" ({change} from starting {irating_start})"
    
    # Points explanation based on iRacing system
    # Note: "Starts" in standings = weeks with participation or counted results
    # Points = sum of weekly scores (each week averages best 25% of races)
    # NOT simply "points per race" - that's misleading!
    
    report = f"""# Week {week_number:02d} Season Standings Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Season:** 01 2026
**Series:** Formula 1600 Rookie Series

---

## 📊 Your Season Stats

**Position:** {driver['position']} / {driver['total_drivers']} drivers (Top {percentiles['position']['percentile']:.1f}%)

### Core Stats

| Metric | Value | Percentile | Better Than |
|--------|-------|------------|-------------|
| **iRating** | {driver['irating']}{irating_change} | {percentiles['irating']['percentile']:.1f}% | {percentiles['irating']['better_than_percent']:.1f}% of drivers |
| **Points** | {driver['points']:.1f} | {percentiles['points']['percentile']:.1f}% | {percentiles['points']['better_than_percent']:.1f}% of drivers {format_percentile_badge(percentiles['points']['percentile'])} |
| **Division** | {driver['division']} | - | - |
| **Avg Finish** | {driver['avgfinish']:.1f} | {percentiles['avgfinish']['percentile']:.1f}% | {percentiles['avgfinish']['better_than_percent']:.1f}% finish better |
| **Avg Start** | {driver['avgstart']:.1f} | {percentiles['avgstart']['percentile']:.1f}% | {percentiles['avgstart']['better_than_percent']:.1f}% qualify worse {format_percentile_badge(percentiles['avgstart']['percentile'])} |

### Race Results

| Metric | Value | Percentile | Better Than |
|--------|-------|------------|-------------|
| **Wins** 🏆 | {driver['wins']} | {percentiles['wins']['percentile']:.1f}% | {percentiles['wins']['better_than_percent']:.1f}% of drivers {format_percentile_badge(percentiles['wins']['percentile'])} |
| **Poles** 🏁 | {driver['poles']} | {percentiles['poles']['percentile']:.1f}% | {percentiles['poles']['better_than_percent']:.1f}% of drivers {format_percentile_badge(percentiles['poles']['percentile'])} |
| **Top 5s** | {driver['topfive']} | {percentiles['topfive']['percentile']:.1f}% | {percentiles['topfive']['better_than_percent']:.1f}% of drivers |
| **Starts** | {driver['starts']} | - | - |

### Incident Analysis

| Metric | Your Value | Series Avg | Your Standing |
|--------|------------|------------|---------------|
| **Incidents/Start** | {driver.get('incidents_per_start', 0):.2f} | {incidents['avg_incidents_per_race']:.2f} | **{((1 - percentiles['incidents']['percentile']/100) * 100):.1f}% cleaner** than average |
| **Total Incidents** | {driver['incidents']} | - | Better than {percentiles['incidents']['better_than_percent']:.1f}% of drivers |

**Clean Drivers (0 incidents):** {incidents['clean_drivers']} ({incidents['clean_percentage']:.1f}% of field)

---

## 🇳🇱 Dutch Drivers Analysis

**Total Dutch Drivers:** {country['total_drivers']}

| Metric | Dutch Avg | Global Avg | Difference |
|--------|-----------|------------|------------|
| **iRating** | {country['avg_irating']:.0f} | {country['avg_irating_all']:.0f} | {(country['avg_irating'] - country['avg_irating_all']):+.0f} |
| **Incidents/Race** | {country['avg_incidents_per_race']:.2f} | {incidents['avg_incidents_per_race']:.2f} | {(country['avg_incidents_per_race'] - incidents['avg_incidents_per_race']):.2f} |
| **Total Wins** | {country['total_wins']} | - | - |
| **Total Poles** | {country['total_poles']} | - | - |

### Top 5 Dutch Drivers

"""
    
    for i, dutch_driver in enumerate(country['top_drivers'], 1):
        report += f"{i}. **{dutch_driver['name']}** - P{dutch_driver['position']} - iRating {dutch_driver['irating']} - Div {dutch_driver['division']} - {dutch_driver['wins']} wins\n"
    
    report += f"""
**Your Dutch Ranking:** Beating {country['total_drivers'] - sum(1 for d in country['top_drivers'] if d['position'] < driver['position'])} other Dutch drivers

---

## 📈 Division {driver['division']} Analysis

**Drivers in Your Division:** {div_comparison['your_division_stats']['drivers']}

| Metric | Your Value | Division Avg | Your Standing |
|--------|------------|--------------|---------------|
| **iRating** | {driver['irating']} | {div_comparison['your_division_stats']['avg_irating']:.0f} | {'**Above average** ✅' if driver['irating'] > div_comparison['your_division_stats']['avg_irating'] else 'Below average'} |
| **Incidents/Start** | {driver.get('incidents_per_start', 0):.2f} | {div_comparison['your_division_stats']['avg_incidents_per_race']:.2f} | {'**Cleaner than average** ✅' if driver.get('incidents_per_start', 0) < div_comparison['your_division_stats']['avg_incidents_per_race'] else 'More incidents than average'} |
| **Points** | {driver['points']:.1f} | {div_comparison['your_division_stats']['avg_points']:.1f} | {'**Above average** 🏆' if driver['points'] > div_comparison['your_division_stats']['avg_points'] else 'Below average'} |

### Division Ladder

| Division | Drivers | Avg iRating | Incidents/Race | Avg Points |
|----------|---------|-------------|----------------|------------|
"""
    
    for div_num in sorted(div_comparison['all_divisions'].keys()):
        div_data = div_comparison['all_divisions'][div_num]
        marker = " **← YOU**" if div_num == driver['division'] else ""
        report += f"| {div_num} | {div_data['drivers']} | {div_data['avg_irating']:.0f} | {div_data['avg_incidents_per_race']:.2f} | {div_data['avg_points']:.1f} |{marker}\n"
    
    report += f"""

---

## 📊 iRating Distribution

**Your iRating:** {driver['irating']} (Percentile: {percentiles['irating']['percentile']:.1f}%)

| Percentile | iRating |
|------------|---------|
| 99th (Elite) | {irating_dist['percentiles']['p99']} |
| 95th | {irating_dist['percentiles']['p95']} |
| 90th | {irating_dist['percentiles']['p90']} |
| 75th | {irating_dist['percentiles']['p75']} {'**← Next goal**' if driver['irating'] < irating_dist['percentiles']['p75'] else ''} |
| **50th (Median)** | **{irating_dist['percentiles']['p50']}** {'✅' if driver['irating'] > irating_dist['percentiles']['p50'] else ''} |
| 25th | {irating_dist['percentiles']['p25']} {'✅' if driver['irating'] > irating_dist['percentiles']['p25'] else ''} |

**Gap to 75th percentile:** {max(0, irating_dist['percentiles']['p75'] - driver['irating'])} iRating points

### iRating Ranges

"""
    
    for range_name, range_data in irating_dist['ranges'].items():
        low, high = map(int, range_name.split('-'))
        is_your_range = low <= driver['irating'] < high
        marker = " **← YOU**" if is_your_range else ""
        bar = "█" * int(range_data['percentage'] / 2)
        report += f"- **{range_name}:** {range_data['count']} drivers ({range_data['percentage']:.1f}%) {bar}{marker}\n"
    
    report += f"""

---

## 🔬 Statistical Insights

### What Actually Matters? (Correlation Analysis)

"""
    
    for label, corr_data in correlations.items():
        sig_marker = corr_data['significance']
        report += f"**{label}**\n"
        report += f"- Correlation: {corr_data['correlation']:.3f} ({corr_data['interpretation']})\n"
        report += f"- Significance: {sig_marker} (p = {corr_data['p_value']:.6f})\n\n"
    
    report += f"""

**Key Takeaways:**
- Higher iRating → More Points (strong positive correlation)
- iRating → Avg Finish has weak correlation (skill matters but isn't everything)
- Incidents have weak negative effect on points (smart aggression > passive clean)
- Your data proves this: {percentiles['irating']['percentile']:.1f}% iRating percentile but {percentiles['points']['percentile']:.1f}% points percentile!

---

## 🎯 Goals & Targets

### Short-term (Next 2 weeks)
1. **More races** - You're at {driver['starts']} starts, most top drivers have 4-6+ starts
2. **Maintain incident rate** - {driver.get('incidents_per_start', 0):.2f}/start is elite, don't change it
3. **Target avg finish < 3.5** - Currently {driver['avgfinish']:.1f}

### Mid-term (Rest of season)
1. **Break {irating_dist['percentiles']['p75']} iRating** (75th percentile) - {max(0, irating_dist['percentiles']['p75'] - driver['irating'])} points to go
2. **Top 500 overall** - Currently P{driver['position']}
3. **Division 6-7** - Your racecraft suggests you belong higher

### Long-term (Next season)
1. **Top 100** - Maintain current performance trajectory
2. **Division 3-4** - Where your racecraft data suggests you'll settle
3. **2000+ iRating** - Elite tier

---

## 📝 Notes

**About Your Points:**
- **Total Season Points:** {driver['points']:.1f}
- **Starts:** {driver['starts']} (weeks with participation or counted results)
- **Note:** iRacing uses a complex weekly averaging system (best 25% of races per week)
- Points are NOT simply "total/races" - they're based on SOF, field size, and weekly averaging
- See: `docs/standings-and-point-system.md` for full explanation

**Your standout metrics:**
"""
    
    # Find top 3 percentiles
    top_percentiles = sorted(
        [(k, v['better_than_percent']) for k, v in percentiles.items()],
        key=lambda x: x[1],
        reverse=True
    )[:3]
    
    for metric, pct in top_percentiles:
        report += f"- {percentiles[metric]['label']}: {pct:.1f}% better than others {format_percentile_badge(pct)}\n"
    
    report += f"""

**Areas for improvement:**
"""
    
    # Find bottom 3 percentiles
    bottom_percentiles = sorted(
        [(k, v['better_than_percent']) for k, v in percentiles.items()],
        key=lambda x: x[1]
    )[:3]
    
    for metric, pct in bottom_percentiles:
        report += f"- {percentiles[metric]['label']}: {pct:.1f}% better than others\n"
    
    report += f"""

---

**Data Source:** Season standings as of Week {week_number:02d}
**Total Drivers Analyzed:** {driver['total_drivers']}
**Active Drivers (1+ start):** {incidents['total_drivers']}
"""
    
    return report


def main():
    if len(sys.argv) < 3:
        print("Usage: generate_weekly_standings_report.py <week_number> <standings_csv> [starting_irating]")
        print("\nExample:")
        print("  python tools/coach/generate_weekly_standings_report.py 1 data/standings/week01/season-driver_*.csv 1238")
        sys.exit(1)
    
    week_number = int(sys.argv[1])
    csv_path = sys.argv[2]
    
    # Optional starting iRating for tracking progress
    irating_start = None
    if len(sys.argv) > 3:
        irating_start = int(sys.argv[3])
    
    # Master Lonn's custid
    custid = 981717
    
    print(f"🔬 Analyzing Week {week_number:02d} standings...")
    
    # Run analyzer
    analysis = run_analyzer(csv_path, custid)
    
    print(f"📊 Generating report...")
    
    # Generate report
    report = generate_report(week_number, analysis, irating_start)
    
    # Save to week folder
    week_folder = Path(f"weeks/week{week_number:02d}")
    week_folder.mkdir(parents=True, exist_ok=True)
    
    report_path = week_folder / "standings-report.md"
    
    with open(report_path, 'w') as f:
        f.write(report)
    
    print(f"✅ Report saved to: {report_path}")
    print(f"\n🏆 Key Stats:")
    print(f"   Position: {analysis['driver']['position']} / {analysis['driver']['total_drivers']}")
    print(f"   iRating: {analysis['driver']['irating']}")
    print(f"   Points Percentile: {analysis['percentiles']['points']['percentile']:.1f}%")
    print(f"   Incidents/Start: {analysis['driver'].get('incidents_per_start', 0):.2f}")


if __name__ == '__main__':
    main()

