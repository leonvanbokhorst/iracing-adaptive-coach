#!/usr/bin/env python3
"""
Visualize Driver's Actual Path on the Traction Circle

This tool plots real telemetry data on the traction circle to show:
- Where the driver is using grip efficiently (inside circle)
- Where the driver is at the limit (on circle)
- Where the driver is overdriving (outside circle = sliding)

Usage:
    # Single lap
    python tools/coach/visualize_driver_traction_circle.py data/telemetry.csv
    
    # Compare two laps
    python tools/coach/visualize_driver_traction_circle.py data/slow_lap.csv data/fast_lap.csv
    
    # Save to file
    python tools/coach/visualize_driver_traction_circle.py data/lap.csv --output path/to/save.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import argparse
from pathlib import Path


def load_telemetry(file_path):
    """Load telemetry data from CSV"""
    df = pd.read_csv(file_path)
    
    # Check if we have the required columns
    required = ['LapDistPct', 'LongAccel', 'LatAccel']
    missing = [col for col in required if col not in df.columns]
    
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    return df


def calculate_traction_usage(df):
    """Calculate traction circle metrics"""
    # Remove wrap-around rows at the end (where LapDistPct jumps back to ~0)
    # Find where LapDistPct decreases significantly (wrap-around detection)
    lap_pct_diff = df['LapDistPct'].diff()
    wrap_idx = df[lap_pct_diff < -0.5].index  # Big negative jump = wrap
    if len(wrap_idx) > 0:
        # Keep only data before the first wrap
        df = df.loc[:wrap_idx[0]-1].copy()
        print(f"   Removed {len(df) - wrap_idx[0] + 1} wrap-around rows at end of lap")
    
    # Convert from m/s² to G's (1G = 9.8 m/s²)
    # STANDARD RACING CONVENTION: Braking = positive (up), Acceleration = negative (down)
    df['LongG_raw'] = -(df['LongAccel'] / 9.8)  # Positive = braking, negative = acceleration
    df['LatG_raw'] = df['LatAccel'] / 9.8       # Positive = left turn, negative = right turn
    
    # Apply smoothing to remove spikes/noise (rolling average, 10 samples ~= 0.1 seconds at 100Hz)
    window = 10
    df['LongG'] = df['LongG_raw'].rolling(window=window, center=True, min_periods=1).mean()
    df['LatG'] = df['LatG_raw'].rolling(window=window, center=True, min_periods=1).mean()
    
    # Total G-force (combined) - both raw and smoothed
    df['TotalG_raw'] = np.sqrt(df['LongG_raw']**2 + df['LatG_raw']**2)
    df['TotalG'] = np.sqrt(df['LongG']**2 + df['LatG']**2)
    
    # Traction usage - use smoothed for sustained cornering limit
    # Sustained cornering limit: ~1.4G (based on XRS data)
    df['TractionUsage'] = (df['TotalG'] / 1.4) * 100
    
    # Overdriving flag - sustained over 1.4G
    df['Overdriving'] = df['TotalG'] > 1.4
    
    return df


def plot_single_lap(df, lap_name, output_path=None):
    """Plot a single lap on the traction circle"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # --- LEFT PLOT: Traction circle with path ---
    ax = ax1
    
    # Draw the grip limit circle (1.2G for FF1600 on treaded tires)
    circle = plt.Circle((0, 0), 1.2, color='#2ecc71', fill=False, linewidth=3, 
                        label='Grip Limit (~1.2G)', linestyle='--')
    ax.add_patch(circle)
    
    # Fill inside (safe zone)
    circle_fill = plt.Circle((0, 0), 1.2, color='#2ecc71', alpha=0.05)
    ax.add_patch(circle_fill)
    
    # Plot the driving path, colored by speed
    scatter = ax.scatter(df['LatG'], df['LongG'], 
                        c=df['LapDistPct'], 
                        cmap='viridis', 
                        s=10, 
                        alpha=0.6,
                        label='Driving Path')
    
    # Highlight overdriving moments in red
    overdrive_df = df[df['Overdriving']]
    if len(overdrive_df) > 0:
        ax.scatter(overdrive_df['LatG'], overdrive_df['LongG'], 
                  c='red', s=30, marker='x', linewidths=2, 
                  alpha=0.8, label=f'Overdriving ({len(overdrive_df)} points)', zorder=5)
    
    # Add colorbar for lap progress
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Lap Progress (%)', fontsize=11)
    
    # Draw axes
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add quadrant labels (STANDARD RACING CONVENTION)
    ax.text(0.05, 0.8, 'BRAKE', ha='left', va='center', fontsize=10, fontweight='bold', alpha=0.5)
    ax.text(0.05, -0.8, 'ACCEL', ha='left', va='center', fontsize=10, fontweight='bold', alpha=0.5)
    ax.text(0.8, 0.05, 'LEFT', ha='center', va='bottom', fontsize=10, fontweight='bold', alpha=0.5)
    ax.text(-0.8, 0.05, 'RIGHT', ha='center', va='bottom', fontsize=10, fontweight='bold', alpha=0.5)
    
    # Styling
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xlabel('Lateral G (← Right | Left →)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Longitudinal G (↑ Brake | Accel ↓)', fontsize=12, fontweight='bold')
    ax.set_title(f'Your Path on the Traction Circle\n{lap_name}', 
                fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    # --- RIGHT PLOT: Grip usage over lap ---
    ax = ax2
    
    # Convert LapDistPct to percentage (0-100) for plotting
    lap_pct = df['LapDistPct'] * 100
    
    # Plot total G over lap distance
    ax.plot(lap_pct, df['TotalG'], color='#3498db', linewidth=2, label='Total G-Force')
    
    # Add grip limit line
    ax.axhline(y=1.4, color='#2ecc71', linestyle='--', linewidth=2, label='Grip Limit (~1.4G)')
    
    # Shade overdriving areas
    ax.fill_between(lap_pct, df['TotalG'], 1.4, 
                    where=(df['TotalG'] > 1.4), 
                    color='red', alpha=0.3, label='Overdriving')
    
    # Styling
    ax.set_xlim(0, 100)
    ax.set_ylim(0, max(df['TotalG'].max() * 1.1, 1.5))
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xlabel('Lap Progress (%)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Combined G-Force', fontsize=12, fontweight='bold')
    ax.set_title('Grip Usage Throughout the Lap', fontsize=13, fontweight='bold', pad=15)
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add statistics
    overdrive_pct = (df['Overdriving'].sum() / len(df)) * 100
    avg_g = df['TotalG'].mean()
    max_g = df['TotalG'].max()
    
    stats_text = (
        f"Avg G-Force: {avg_g:.2f}G\n"
        f"Max G-Force: {max_g:.2f}G\n"
        f"Overdriving: {overdrive_pct:.1f}% of lap"
    )
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes,
           fontsize=10, verticalalignment='top',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def plot_comparison(df1, df2, name1, name2, output_path=None):
    """Compare two laps on the traction circle - CLEAN & SIMPLE"""
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # --- ONE SIMPLE TRACTION CIRCLE ---
    
    # Draw grip limit circles (XRS-style: inner = sustained, outer = peaks)
    circle_sustained = plt.Circle((0, 0), 1.4, color='#2ecc71', fill=False, linewidth=2.5, 
                                   linestyle='-', alpha=0.7, label='Sustained Limit (~1.4G)')
    circle_peak = plt.Circle((0, 0), 2.0, color='gray', fill=False, linewidth=1.5, 
                             linestyle='--', alpha=0.4, label='Peak Limit (~2.0G)')
    ax.add_patch(circle_peak)
    ax.add_patch(circle_sustained)
    
    # Fill the safe zone
    circle_fill = plt.Circle((0, 0), 1.4, color='#2ecc71', alpha=0.05)
    ax.add_patch(circle_fill)
    
    # Plot both laps - SMOOTHED for clean visualization
    ax.plot(df1['LatG'], df1['LongG'], color='#e74c3c', linewidth=1.5, alpha=0.7, label='Slow Lap (smoothed)')
    ax.plot(df2['LatG'], df2['LongG'], color='#27ae60', linewidth=1.5, alpha=0.7, label='Fast Lap (smoothed)')
    
    # Add scatter for raw data (light, to show spikes)
    ax.scatter(df1['LatG_raw'], df1['LongG_raw'], c='#e74c3c', s=3, alpha=0.15, zorder=1)
    ax.scatter(df2['LatG_raw'], df2['LongG_raw'], c='#27ae60', s=3, alpha=0.15, zorder=1)
    
    # Axes
    ax.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    ax.axvline(x=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.3)
    
    # Styling - MINIMAL
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-2.5, 2.5)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle=':', linewidth=0.5)
    ax.set_xlabel('Lateral G (← Right | Left →)', fontsize=11)
    ax.set_ylabel('Longitudinal G (↑ Brake | Accel ↓)', fontsize=11)
    ax.set_title('Traction Circle Comparison (Smoothed)\n' + 
                'Bold Lines = Sustained Force | Light Dots = Raw Data',
                fontsize=13, fontweight='bold', pad=20)
    ax.legend(loc='upper left', fontsize=9, framealpha=0.9)
    
    plt.tight_layout()
    
    # Print detailed analysis to terminal
    print("\n" + "="*70)
    print("📊 TRACTION CIRCLE ANALYSIS (SMOOTHED DATA)")
    print("="*70)
    
    print(f"\n🔴 SLOW LAP:")
    print(f"   Sustained Avg:   {df1['TotalG'].mean():.3f}G")
    print(f"   Sustained Max:   {df1['TotalG'].max():.3f}G")
    print(f"   Raw Spikes:      {df1['TotalG_raw'].max():.3f}G")
    print(f"   Peak Lateral:    {df1['LatG'].abs().max():.3f}G (sustained) / {df1['LatG_raw'].abs().max():.3f}G (spike)")
    print(f"   Peak Braking:    {df1['LongG'].min():.3f}G (sustained) / {df1['LongG_raw'].min():.3f}G (spike)")
    print(f"   Peak Accel:      {df1['LongG'].max():.3f}G")
    print(f"   Over 1.4G:       {(df1['Overdriving'].sum()/len(df1)*100):.1f}% of lap")
    
    print(f"\n🟢 FAST LAP:")
    print(f"   Sustained Avg:   {df2['TotalG'].mean():.3f}G")
    print(f"   Sustained Max:   {df2['TotalG'].max():.3f}G")
    print(f"   Raw Spikes:      {df2['TotalG_raw'].max():.3f}G")
    print(f"   Peak Lateral:    {df2['LatG'].abs().max():.3f}G (sustained) / {df2['LatG_raw'].abs().max():.3f}G (spike)")
    print(f"   Peak Braking:    {df2['LongG'].min():.3f}G (sustained) / {df2['LongG_raw'].min():.3f}G (spike)")
    print(f"   Peak Accel:      {df2['LongG'].max():.3f}G")
    print(f"   Over 1.4G:       {(df2['Overdriving'].sum()/len(df2)*100):.1f}% of lap")
    
    print(f"\n📈 DELTA (Fast - Slow):")
    avg_delta = df2['TotalG'].mean() - df1['TotalG'].mean()
    max_delta = df2['TotalG'].max() - df1['TotalG'].max()
    spike_delta = df2['TotalG_raw'].max() - df1['TotalG_raw'].max()
    print(f"   Sustained Avg:   {avg_delta:+.3f}G")
    print(f"   Sustained Max:   {max_delta:+.3f}G  {'✅ Smoother!' if max_delta < 0 else '⚠️ More spiky'}")
    print(f"   Raw Spikes:      {spike_delta:+.3f}G  {'✅ Cleaner!' if spike_delta < 0 else '⚠️ More spiky'}")
    
    # Calculate smoothness metric (standard deviation of G-force changes)
    df1_smoothness = df1['TotalG'].diff().std()
    df2_smoothness = df2['TotalG'].diff().std()
    print(f"\n🎯 SMOOTHNESS (lower = smoother):")
    print(f"   Slow lap:        {df1_smoothness:.4f}")
    print(f"   Fast lap:        {df2_smoothness:.4f}  {'✅ Smoother!' if df2_smoothness < df1_smoothness else '⚠️ More erratic'}")
    
    # Find sections with biggest differences (compare by lap progress %)
    # Bin by lap progress for comparison
    bins = np.linspace(0, 100, 101)
    df1_binned = df1.groupby(pd.cut(df1['LapDistPct'], bins))['TotalG'].mean()
    df2_binned = df2.groupby(pd.cut(df2['LapDistPct'], bins))['TotalG'].mean()
    
    # Calculate difference where both have data
    valid_mask = ~(df1_binned.isna() | df2_binned.isna())
    if valid_mask.sum() > 0:
        diff = np.abs(df1_binned[valid_mask] - df2_binned[valid_mask])
        max_diff_idx = diff.idxmax()
        max_diff_pct = max_diff_idx.mid
        
        print(f"\n🔍 BIGGEST DIFFERENCE:")
        print(f"   Location:        {max_diff_pct:.1f}% through lap")
        print(f"   Slow lap:        {df1_binned[max_diff_idx]:.3f}G")
        print(f"   Fast lap:        {df2_binned[max_diff_idx]:.3f}G")
        print(f"   Difference:      {diff.max():.3f}G")
    
    print("\n" + "="*70)
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"\n💾 Saved visualization to: {output_path}\n")
    else:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Visualize driver traction circle usage from telemetry'
    )
    parser.add_argument(
        'telemetry1',
        type=str,
        help='Path to first telemetry CSV file'
    )
    parser.add_argument(
        'telemetry2',
        type=str,
        nargs='?',
        help='Path to second telemetry CSV file (for comparison)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path (PNG)'
    )
    
    args = parser.parse_args()
    
    # Load first lap
    print(f"📂 Loading: {args.telemetry1}")
    df1 = load_telemetry(args.telemetry1)
    df1 = calculate_traction_usage(df1)
    name1 = Path(args.telemetry1).stem
    
    if args.telemetry2:
        # Comparison mode
        print(f"📂 Loading: {args.telemetry2}")
        df2 = load_telemetry(args.telemetry2)
        df2 = calculate_traction_usage(df2)
        name2 = Path(args.telemetry2).stem
        
        output_path = args.output or 'docs/assets/traction-circle-driver-comparison.png'
        plot_comparison(df1, df2, name1, name2, output_path)
        
    else:
        # Single lap mode
        output_path = args.output or 'docs/assets/traction-circle-driver-single.png'
        plot_single_lap(df1, name1, output_path)


if __name__ == "__main__":
    main()

