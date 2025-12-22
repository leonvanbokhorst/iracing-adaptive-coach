#!/usr/bin/env python3
"""
Standings Analysis Tool - SCIENCE EDITION 🧪

Analyzes season standings with statistical depth:
- Find driver position and stats
- Division analysis
- iRating distribution
- Incident analysis
- Country/club comparisons
- Statistical trends and significance
- Percentile rankings

Usage:
    python tools/coach/analyze_standings.py <standings_csv> <custid>
    
Output: JSON with comprehensive statistical analysis
"""

import sys
import json
import pandas as pd
import numpy as np
from pathlib import Path
from scipy import stats


def load_standings(csv_path):
    """Load standings CSV"""
    df = pd.read_csv(csv_path)
    
    # Clean up column names
    df.columns = df.columns.str.strip()
    
    # Convert numeric columns
    numeric_cols = ['position', 'points', 'irating', 'avgfinish', 'topfive', 
                    'starts', 'lapslead', 'wins', 'incidents', 'division', 
                    'weekscounted', 'laps', 'poles', 'avgstart']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df


def find_driver(df, custid):
    """Find specific driver by custid"""
    driver = df[df['custid'] == int(custid)]
    
    if driver.empty:
        return None
    
    return driver.iloc[0].to_dict()


def calculate_driver_percentiles(df, driver):
    """Calculate percentile rankings for driver's stats"""
    custid = driver['custid']
    driver_row = df[df['custid'] == custid].iloc[0]
    
    # Only include drivers with at least 1 start
    active_df = df[df['starts'] > 0].copy()
    
    percentiles = {}
    
    # Lower is better for these metrics
    reverse_metrics = ['avgfinish', 'incidents', 'avgstart']
    
    metrics = {
        'position': 'Overall Position',
        'points': 'Points',
        'irating': 'iRating',
        'avgfinish': 'Avg Finish',
        'incidents': 'Incidents',
        'wins': 'Wins',
        'poles': 'Poles',
        'topfive': 'Top 5s',
        'avgstart': 'Avg Start Position'
    }
    
    for metric, label in metrics.items():
        if metric in active_df.columns and not pd.isna(driver_row[metric]):
            value = driver_row[metric]
            
            if metric in reverse_metrics:
                # For these, lower is better, so reverse percentile
                percentile = (active_df[metric] > value).sum() / len(active_df) * 100
            else:
                # For these, higher is better
                percentile = (active_df[metric] <= value).sum() / len(active_df) * 100
            
            percentiles[metric] = {
                'value': float(value),
                'percentile': round(percentile, 1),
                'label': label,
                'better_than_percent': round(percentile, 1) if metric not in reverse_metrics else round(100 - percentile, 1)
            }
    
    return percentiles


def analyze_divisions(df):
    """Analyze division breakdown"""
    # Only active drivers
    active_df = df[df['starts'] > 0].copy()
    
    division_stats = {}
    
    for div in sorted(active_df['division'].dropna().unique()):
        div_data = active_df[active_df['division'] == div]
        
        division_stats[int(div)] = {
            'drivers': len(div_data),
            'avg_irating': round(div_data['irating'].mean(), 0),
            'irating_std': round(div_data['irating'].std(), 0),
            'irating_range': {
                'min': int(div_data['irating'].min()),
                'max': int(div_data['irating'].max())
            },
            'avg_incidents': round(div_data['incidents'].mean(), 2),
            'incidents_std': round(div_data['incidents'].std(), 2),
            'avg_starts': round(div_data['starts'].mean(), 1),
            'total_races': int(div_data['starts'].sum())
        }
    
    return division_stats


def analyze_irating_distribution(df):
    """Analyze iRating distribution with statistical measures"""
    active_df = df[df['starts'] > 0].copy()
    iratings = active_df['irating'].dropna()
    
    # Calculate percentiles
    percentiles = [10, 25, 50, 75, 90, 95, 99]
    percentile_values = {}
    
    for p in percentiles:
        percentile_values[f'p{p}'] = int(np.percentile(iratings, p))
    
    # Calculate statistical measures
    distribution = {
        'total_drivers': len(iratings),
        'mean': round(iratings.mean(), 0),
        'median': int(iratings.median()),
        'std': round(iratings.std(), 0),
        'min': int(iratings.min()),
        'max': int(iratings.max()),
        'percentiles': percentile_values,
        'quartiles': {
            'q1': int(iratings.quantile(0.25)),
            'q2': int(iratings.quantile(0.50)),
            'q3': int(iratings.quantile(0.75)),
            'iqr': int(iratings.quantile(0.75) - iratings.quantile(0.25))
        }
    }
    
    # Classify into ranges
    ranges = [
        (0, 1000),
        (1000, 1500),
        (1500, 2000),
        (2000, 3000),
        (3000, 4000),
        (4000, 5000),
        (5000, 10000)
    ]
    
    range_counts = {}
    for low, high in ranges:
        count = len(iratings[(iratings >= low) & (iratings < high)])
        if count > 0:
            range_counts[f'{low}-{high}'] = {
                'count': count,
                'percentage': round(count / len(iratings) * 100, 1)
            }
    
    distribution['ranges'] = range_counts
    
    return distribution


def analyze_incidents(df):
    """Analyze incident patterns"""
    active_df = df[df['starts'] > 0].copy()
    
    # Calculate incidents per race
    active_df['inc_per_race'] = active_df['incidents'] / active_df['starts']
    
    inc_stats = {
        'total_drivers': len(active_df),
        'total_incidents': int(active_df['incidents'].sum()),
        'avg_incidents_total': round(active_df['incidents'].mean(), 2),
        'avg_incidents_per_race': round(active_df['inc_per_race'].mean(), 2),
        'std_incidents_per_race': round(active_df['inc_per_race'].std(), 2),
        'median_incidents_per_race': round(active_df['inc_per_race'].median(), 2),
        'percentiles': {
            'p25': round(active_df['inc_per_race'].quantile(0.25), 2),
            'p50': round(active_df['inc_per_race'].quantile(0.50), 2),
            'p75': round(active_df['inc_per_race'].quantile(0.75), 2),
            'p90': round(active_df['inc_per_race'].quantile(0.90), 2)
        }
    }
    
    # Clean drivers (0 incidents)
    clean_drivers = len(active_df[active_df['incidents'] == 0])
    inc_stats['clean_drivers'] = clean_drivers
    inc_stats['clean_percentage'] = round(clean_drivers / len(active_df) * 100, 1)
    
    return inc_stats


def analyze_country(df, country_code):
    """Analyze specific country's drivers"""
    country_df = df[(df['countrycode'] == country_code) & (df['starts'] > 0)].copy()
    
    if country_df.empty:
        return None
    
    # Calculate incidents per race for ranking
    country_df['inc_per_race'] = country_df['incidents'] / country_df['starts']
    
    # Get all active drivers for comparison
    all_active = df[df['starts'] > 0].copy()
    all_active['inc_per_race'] = all_active['incidents'] / all_active['starts']
    
    stats = {
        'country_code': country_code,
        'total_drivers': len(country_df),
        'avg_irating': round(country_df['irating'].mean(), 0),
        'avg_irating_all': round(all_active['irating'].mean(), 0),
        'median_irating': int(country_df['irating'].median()),
        'avg_position': round(country_df['position'].mean(), 1),
        'best_position': int(country_df['position'].min()),
        'avg_incidents_per_race': round(country_df['inc_per_race'].mean(), 2),
        'avg_incidents_per_race_all': round(all_active['inc_per_race'].mean(), 2),
        'total_wins': int(country_df['wins'].sum()),
        'total_poles': int(country_df['poles'].sum()),
        'drivers_with_wins': int((country_df['wins'] > 0).sum()),
        'top_drivers': []
    }
    
    # Top 5 drivers from this country
    top_country = country_df.nsmallest(5, 'position')
    
    for _, driver in top_country.iterrows():
        stats['top_drivers'].append({
            'name': driver['name'],
            'position': int(driver['position']),
            'irating': int(driver['irating']),
            'points': float(driver['points']),
            'wins': int(driver['wins']),
            'division': int(driver['division'])
        })
    
    return stats


def analyze_performance_correlation(df):
    """Analyze correlations between metrics"""
    active_df = df[df['starts'] > 0].copy()
    active_df['inc_per_race'] = active_df['incidents'] / active_df['starts']
    
    # Select relevant columns for correlation
    correlation_metrics = ['irating', 'avgfinish', 'inc_per_race', 'points', 'wins', 'topfive']
    
    corr_df = active_df[correlation_metrics].dropna()
    
    correlations = {}
    
    # Key correlations to examine
    pairs = [
        ('irating', 'avgfinish', 'iRating vs Avg Finish'),
        ('irating', 'points', 'iRating vs Points'),
        ('inc_per_race', 'avgfinish', 'Incidents/Race vs Avg Finish'),
        ('inc_per_race', 'points', 'Incidents/Race vs Points'),
        ('irating', 'inc_per_race', 'iRating vs Incidents/Race')
    ]
    
    for metric1, metric2, label in pairs:
        if metric1 in corr_df.columns and metric2 in corr_df.columns:
            correlation, p_value = stats.pearsonr(corr_df[metric1], corr_df[metric2])
            
            # Determine significance
            if p_value < 0.001:
                significance = '***'
            elif p_value < 0.01:
                significance = '**'
            elif p_value < 0.05:
                significance = '*'
            else:
                significance = 'ns'
            
            correlations[label] = {
                'correlation': round(correlation, 3),
                'p_value': round(p_value, 6),
                'significance': significance,
                'interpretation': interpret_correlation(correlation)
            }
    
    return correlations


def interpret_correlation(r):
    """Interpret correlation strength"""
    abs_r = abs(r)
    
    if abs_r < 0.1:
        strength = 'negligible'
    elif abs_r < 0.3:
        strength = 'weak'
    elif abs_r < 0.5:
        strength = 'moderate'
    elif abs_r < 0.7:
        strength = 'strong'
    else:
        strength = 'very strong'
    
    direction = 'positive' if r > 0 else 'negative'
    
    return f'{strength} {direction}'


def analyze_division_comparison(df, driver_division):
    """Compare driver's division to others"""
    active_df = df[df['starts'] > 0].copy()
    active_df['inc_per_race'] = active_df['incidents'] / active_df['starts']
    
    div_data = active_df[active_df['division'] == driver_division]
    
    comparison = {
        'your_division': int(driver_division),
        'your_division_stats': {
            'drivers': len(div_data),
            'avg_irating': round(div_data['irating'].mean(), 0),
            'avg_incidents_per_race': round(div_data['inc_per_race'].mean(), 2),
            'avg_points': round(div_data['points'].mean(), 1)
        },
        'all_divisions': {}
    }
    
    # Compare to each division
    for div in sorted(active_df['division'].dropna().unique()):
        div_comparison = active_df[active_df['division'] == div]
        
        comparison['all_divisions'][int(div)] = {
            'drivers': len(div_comparison),
            'avg_irating': round(div_comparison['irating'].mean(), 0),
            'avg_incidents_per_race': round(div_comparison['inc_per_race'].mean(), 2),
            'avg_points': round(div_comparison['points'].mean(), 1)
        }
    
    return comparison


def main():
    if len(sys.argv) < 3:
        print(json.dumps({'error': 'Usage: analyze_standings.py <standings_csv> <custid>'}))
        sys.exit(1)
    
    csv_path = sys.argv[1]
    custid = sys.argv[2]
    
    # Load data
    df = load_standings(csv_path)
    
    # Find driver
    driver = find_driver(df, custid)
    
    if driver is None:
        print(json.dumps({'error': f'Driver with custid {custid} not found'}))
        sys.exit(1)
    
    # Build comprehensive analysis
    analysis = {
        'driver': {
            'name': driver['name'],
            'custid': int(driver['custid']),
            'position': int(driver['position']),
            'total_drivers': len(df),
            'points': float(driver['points']),
            'irating': int(driver['irating']),
            'division': int(driver['division']),
            'country': driver['countrycode'],
            'wins': int(driver['wins']),
            'poles': int(driver['poles']),
            'topfive': int(driver['topfive']),
            'starts': int(driver['starts']),
            'incidents': int(driver['incidents']),
            'avgfinish': float(driver['avgfinish']),
            'avgstart': float(driver['avgstart'])
        },
        'percentiles': calculate_driver_percentiles(df, driver),
        'divisions': analyze_divisions(df),
        'irating_distribution': analyze_irating_distribution(df),
        'incident_analysis': analyze_incidents(df),
        'country_analysis': analyze_country(df, driver['countrycode']),
        'correlations': analyze_performance_correlation(df),
        'division_comparison': analyze_division_comparison(df, driver['division'])
    }
    
    # Calculate derived stats
    if driver['starts'] > 0:
        analysis['driver']['incidents_per_race'] = round(driver['incidents'] / driver['starts'], 2)
        analysis['driver']['points_per_race'] = round(driver['points'] / driver['starts'], 1)
    
    # Print JSON output
    print(json.dumps(analysis, indent=2))


if __name__ == '__main__':
    main()

