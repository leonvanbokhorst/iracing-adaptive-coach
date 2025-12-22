#!/usr/bin/env python3
"""
Visualize iRating Distribution

Creates a beautiful histogram showing the iRating distribution across all drivers,
with the user's position highlighted.

Usage:
    python tools/coach/visualize_irating_distribution.py <standings_csv> <custid> <output_dir>

Example:
    python tools/coach/visualize_irating_distribution.py \\
        data/standings/week01/*.csv \\
        981717 \\
        weeks/week01
"""

import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path

# Set style for beautiful plots
sns.set_theme(style="whitegrid", context="notebook", palette="muted")
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = '#f8f9fa'


def load_standings(csv_path: str, custid: int) -> tuple[pd.DataFrame, dict]:
    """Load standings data and get user's stats"""
    df = pd.read_csv(csv_path)
    
    # Get user's data
    user_data = df[df['custid'] == custid].iloc[0].to_dict()
    
    return df, user_data


def create_irating_distribution(df: pd.DataFrame, user_data: dict, output_path: str):
    """Create beautiful iRating distribution histogram"""
    
    # Define bins with variable sizes: 
    # - Fine detail (200 iR) in competitive range (1000-2000) where 80% of drivers are
    # - Coarser buckets at extremes where fewer drivers exist
    bins = [0, 700, 1000, 1200, 1400, 1600, 2000, 3500, 5000, 15000]
    bin_labels = [
        '0-700\n(Whut?)',
        '700-1000\n(Struggling)',
        '1000-1200\n(Trying)',
        '1200-1400\n(Learning)',
        '1400-1600\n(Progressing)',
        '1600-2000\n(Rising)',
        '2000-3500\n(Solid)',
        '3500-5000\n(Pro)',
        '5000+\n(Alien)'
    ]
    
    # Count drivers in each range
    df['irating_range'] = pd.cut(df['irating'], bins=bins, labels=bin_labels, include_lowest=True)
    range_counts = df['irating_range'].value_counts().sort_index()
    
    # User's iRating
    user_irating = user_data['irating']
    user_range_idx = np.digitize(user_irating, bins) - 1
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create bar colors (highlight user's range)
    colors = ['#3498db'] * len(range_counts)
    colors[user_range_idx] = '#e74c3c'  # Red for user's range
    
    # Create the bar chart
    bars = ax.bar(range(len(range_counts)), range_counts.values, 
                   color=colors, alpha=0.85, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, range_counts.values)):
        height = bar.get_height()
        percentage = (count / len(df)) * 100
        
        # Label text
        label = f'{count:,} drivers\n({percentage:.1f}%)'
        
        # Add star to user's range
        if i == user_range_idx:
            label = f'⭐ YOU ⭐\n{count:,} drivers\n({percentage:.1f}%)'
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   label,
                   ha='center', va='bottom',
                   fontsize=11, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.5', facecolor='#e74c3c', 
                            edgecolor='black', linewidth=2, alpha=0.9),
                   color='white')
        else:
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   label,
                   ha='center', va='bottom',
                   fontsize=10,
                   bbox=dict(boxstyle='round,pad=0.4', facecolor='white', 
                            edgecolor='gray', linewidth=1, alpha=0.8))
    
    # Customize axes
    ax.set_xlabel('iRating Range', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Drivers', fontsize=14, fontweight='bold')
    ax.set_title(f'iRating Distribution - Season Standings\nYour iRating: {user_irating:,}', 
                 fontsize=16, fontweight='bold', pad=20)
    
    # Set x-axis labels
    ax.set_xticks(range(len(range_counts)))
    ax.set_xticklabels(bin_labels, fontsize=11)
    
    # Add grid for readability
    ax.yaxis.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Format y-axis
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Add total drivers annotation
    total_drivers = len(df)
    ax.text(0.98, 0.98, f'Total Drivers: {total_drivers:,}',
           transform=ax.transAxes,
           ha='right', va='top',
           fontsize=12,
           bbox=dict(boxstyle='round,pad=0.5', facecolor='white', 
                    edgecolor='black', linewidth=1.5, alpha=0.9))
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Saved: {output_path}")


def create_detailed_histogram(df: pd.DataFrame, user_data: dict, output_path: str):
    """Create detailed iRating histogram with smooth distribution"""
    
    user_irating = user_data['irating']
    
    # Filter to focus on competitive range (0-5000) where 99.7% of drivers are
    # Only 22 drivers (0.3%) are above 5000, not worth stretching the chart
    df_filtered = df[df['irating'] <= 5000].copy()
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Create histogram with KDE overlay
    sns.histplot(data=df_filtered, x='irating', bins=50, kde=True, 
                color='#3498db', alpha=0.6, edgecolor='black', linewidth=0.5,
                stat='count', ax=ax)
    
    # Add vertical line for user's iRating
    ax.axvline(user_irating, color='#e74c3c', linestyle='--', linewidth=3,
              label=f'Your iRating: {user_irating:,}')
    
    # Add shaded area for user's position
    ax.axvspan(user_irating - 50, user_irating + 50, 
              color='#e74c3c', alpha=0.2)
    
    # Calculate percentile
    percentile = (df['irating'] < user_irating).sum() / len(df) * 100
    
    # Add annotation for user
    y_max = ax.get_ylim()[1]
    ax.annotate(f'YOU\n{user_irating:,} iR\n({percentile:.1f}th percentile)',
               xy=(user_irating, y_max * 0.7),
               xytext=(user_irating + 500, y_max * 0.85),
               fontsize=12, fontweight='bold',
               bbox=dict(boxstyle='round,pad=0.7', facecolor='#e74c3c', 
                        edgecolor='black', linewidth=2, alpha=0.9),
               color='white',
               arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0.3',
                             color='#e74c3c', linewidth=2))
    
    # Add percentile markers
    percentiles = [25, 50, 75, 90, 95]
    for p in percentiles:
        val = df['irating'].quantile(p/100)
        if abs(val - user_irating) > 200:  # Don't overlap with user marker
            ax.axvline(val, color='gray', linestyle=':', alpha=0.5, linewidth=1)
            ax.text(val, y_max * 0.95, f'{p}th\n{val:.0f}',
                   ha='center', fontsize=8, alpha=0.7)
    
    # Add note about cutoff
    total_drivers = len(df)
    drivers_shown = len(df_filtered)
    drivers_above_5k = total_drivers - drivers_shown
    
    # Customize
    ax.set_xlabel('iRating', fontsize=14, fontweight='bold')
    ax.set_ylabel('Number of Drivers', fontsize=14, fontweight='bold')
    ax.set_title(f'Detailed iRating Distribution (0-5000 iR)\nShowing {drivers_shown:,} of {total_drivers:,} drivers ({drivers_above_5k} above 5000)', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Format axes
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))
    
    # Add legend
    ax.legend(loc='upper right', fontsize=12, framealpha=0.9)
    
    # Grid
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.set_axisbelow(True)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✅ Saved: {output_path}")


def main():
    if len(sys.argv) < 4:
        print("Usage: python visualize_irating_distribution.py <standings_csv> <custid> <output_dir>")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    custid = int(sys.argv[2])
    week_dir = Path(sys.argv[3])
    
    # Create assets subdirectory for cleaner organization
    output_dir = week_dir / "assets"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📊 Creating iRating distribution visualizations...")
    print(f"   CSV: {csv_path}")
    print(f"   User: {custid}")
    
    # Load data
    df, user_data = load_standings(csv_path, custid)
    
    print(f"   Total drivers: {len(df):,}")
    print(f"   Your iRating: {user_data['irating']:,}")
    
    # Create visualizations
    print("\n📈 Generating charts...")
    
    # 1. Range-based bar chart
    bar_output = output_dir / "irating_distribution_ranges.png"
    create_irating_distribution(df, user_data, str(bar_output))
    
    # 2. Detailed histogram with KDE
    hist_output = output_dir / "irating_distribution_histogram.png"
    create_detailed_histogram(df, user_data, str(hist_output))
    
    print(f"\n✅ All visualizations created in: {output_dir}")
    print("\nGenerated files:")
    print(f"  - irating_distribution_ranges.png (bar chart)")
    print(f"  - irating_distribution_histogram.png (detailed histogram)")


if __name__ == "__main__":
    main()

