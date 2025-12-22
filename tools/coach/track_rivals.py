#!/usr/bin/env python3
"""
Rival Tracking Tool

Track specific drivers' performance week-over-week to compare against your progression.
Useful for:
- Tracking division rivals
- Following top Dutch drivers
- Monitoring friends/competitors
- Understanding competitive gaps

Usage:
    python tools/coach/track_rivals.py <standings_csv> <your_custid> <rival_custid1> [rival_custid2] ...
    
Example:
    # Track yourself vs Roel de Fouw (top Dutch driver)
    python tools/coach/track_rivals.py \
        data/standings/week01/season-driver_*.csv \
        981717 \
        209147

Output:
    JSON comparison of your stats vs rivals
"""

import sys
import json
import pandas as pd


def load_standings(csv_path):
    """Load standings CSV"""
    df = pd.read_csv(csv_path)
    df.columns = df.columns.str.strip()
    
    # Convert numeric columns
    numeric_cols = ['position', 'points', 'irating', 'avgfinish', 'topfive', 
                    'starts', 'lapslead', 'wins', 'incidents', 'division', 
                    'weekscounted', 'laps', 'poles', 'avgstart']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def find_drivers(df, custids):
    """Find multiple drivers by custid"""
    drivers = {}
    
    for custid in custids:
        driver = df[df['custid'] == int(custid)]
        
        if not driver.empty:
            drivers[int(custid)] = driver.iloc[0].to_dict()
    
    return drivers


def compare_drivers(you, rivals_data):
    """Compare your stats against rivals"""
    comparisons = []
    
    for rival_custid, rival in rivals_data.items():
        if rival_custid == you['custid']:
            continue
        
        # Calculate gaps
        comparison = {
            'rival': {
                'name': rival['name'],
                'custid': rival_custid,
                'country': rival['countrycode']
            },
            'gaps': {
                'position': {
                    'you': int(you['position']),
                    'rival': int(rival['position']),
                    'gap': int(you['position']) - int(rival['position']),  # Negative = you're behind
                    'rival_ahead': int(rival['position']) < int(you['position'])
                },
                'irating': {
                    'you': int(you['irating']),
                    'rival': int(rival['irating']),
                    'gap': int(you['irating']) - int(rival['irating']),
                    'percent_gap': round((int(you['irating']) - int(rival['irating'])) / int(rival['irating']) * 100, 2)
                },
                'points': {
                    'you': float(you['points']),
                    'rival': float(rival['points']),
                    'gap': float(you['points']) - float(rival['points'])
                },
                'division': {
                    'you': int(you['division']),
                    'rival': int(rival['division']),
                    'divisions_apart': int(you['division']) - int(rival['division'])  # Positive = rival in higher div
                },
                'wins': {
                    'you': int(you['wins']),
                    'rival': int(rival['wins']),
                    'gap': int(you['wins']) - int(rival['wins'])
                },
                'incidents_per_race': {
                    'you': round(float(you['incidents']) / float(you['starts']), 2) if you['starts'] > 0 else 0,
                    'rival': round(float(rival['incidents']) / float(rival['starts']), 2) if rival['starts'] > 0 else 0,
                    'gap': round((float(you['incidents']) / float(you['starts'])) - (float(rival['incidents']) / float(rival['starts'])), 2) if you['starts'] > 0 and rival['starts'] > 0 else 0
                }
            },
            'insights': []
        }
        
        # Generate insights
        if comparison['gaps']['position']['rival_ahead']:
            pos_gap = abs(comparison['gaps']['position']['gap'])
            comparison['insights'].append(f"{rival['name']} is {pos_gap} positions ahead")
        else:
            pos_gap = comparison['gaps']['position']['gap']
            comparison['insights'].append(f"You're {pos_gap} positions ahead of {rival['name']}")
        
        if comparison['gaps']['irating']['gap'] < 0:
            comparison['insights'].append(f"iRating gap: {abs(comparison['gaps']['irating']['gap'])} points ({abs(comparison['gaps']['irating']['percent_gap']):.1f}% behind)")
        else:
            comparison['insights'].append(f"iRating: {comparison['gaps']['irating']['gap']} points ahead")
        
        if comparison['gaps']['divisions_apart'] > 0:
            comparison['insights'].append(f"{rival['name']} is {comparison['gaps']['divisions_apart']} divisions higher")
        elif comparison['gaps']['divisions_apart'] < 0:
            comparison['insights'].append(f"You're {abs(comparison['gaps']['divisions_apart'])} divisions higher")
        else:
            comparison['insights'].append("Same division")
        
        # Racecraft comparison
        if comparison['gaps']['incidents_per_race']['gap'] < 0:
            comparison['insights'].append(f"You're cleaner: {abs(comparison['gaps']['incidents_per_race']['gap']):.2f} fewer incidents/race")
        elif comparison['gaps']['incidents_per_race']['gap'] > 0:
            comparison['insights'].append(f"{rival['name']} is cleaner: {comparison['gaps']['incidents_per_race']['gap']:.2f} fewer incidents/race")
        
        comparisons.append(comparison)
    
    return comparisons


def main():
    if len(sys.argv) < 4:
        print("Usage: track_rivals.py <standings_csv> <your_custid> <rival_custid1> [rival_custid2] ...")
        print("\nExample:")
        print("  python tools/coach/track_rivals.py data/standings/week01/season-driver_*.csv 981717 209147")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    your_custid = int(sys.argv[2])
    rival_custids = [int(c) for c in sys.argv[3:]]
    
    print(f"👥 Tracking {len(rival_custids)} rival(s)...")
    
    # Load standings
    df = load_standings(csv_path)
    
    # Find drivers
    all_custids = [your_custid] + rival_custids
    drivers = find_drivers(df, all_custids)
    
    if your_custid not in drivers:
        print(f"❌ Could not find your custid ({your_custid}) in standings")
        sys.exit(1)
    
    you = drivers[your_custid]
    
    # Remove you from rivals
    rivals_data = {k: v for k, v in drivers.items() if k != your_custid}
    
    if not rivals_data:
        print("❌ No rivals found in standings")
        sys.exit(1)
    
    # Compare
    comparisons = compare_drivers(you, rivals_data)
    
    # Output
    output = {
        'you': {
            'name': you['name'],
            'custid': your_custid,
            'position': int(you['position']),
            'irating': int(you['irating']),
            'division': int(you['division']),
            'points': float(you['points']),
            'wins': int(you['wins'])
        },
        'rivals': comparisons
    }
    
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()

