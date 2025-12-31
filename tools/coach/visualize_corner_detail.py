#!/usr/bin/env python3
"""
Coach Tool: Corner Detail Visualization

Zooms in on a specific corner to show:
1. Racing line comparison (zoomed GPS view)
2. Speed trace through the corner
3. Throttle/Brake comparison
4. Line deviation vs speed delta

Usage:
    python tools/coach/visualize_corner_detail.py <your_lap.csv> <reference_lap.csv> <corner_name> [output.png] [track_id] [--dark]

Examples:
    python tools/coach/visualize_corner_detail.py lap.csv ref.csv "Diving Turn" output.png limerock-2019-gp
"""

import sys
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap
from pathlib import Path
from scipy.interpolate import interp1d

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from tools.core.track_data_loader import load_track_data
except ImportError:
    def load_track_data(track_id):
        return None


def load_telemetry(filepath):
    """Load telemetry CSV file."""
    try:
        df = pd.read_csv(filepath)
        return df
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return None


def interpolate_to_common_distance(df, num_points=2000):
    """Interpolate telemetry to common distance points."""
    if df is None or len(df) == 0:
        return None
    
    df = df.copy()
    
    # Remove wrap-around points
    if 'LapDistPct' in df.columns and len(df) > 1:
        if df['LapDistPct'].iloc[-1] < df['LapDistPct'].iloc[-2]:
            df = df.iloc[:-1]
        df = df.sort_values('LapDistPct').reset_index(drop=True)
    
    df = df.drop_duplicates(subset=['LapDistPct'], keep='first')
    
    dist_new = np.linspace(df['LapDistPct'].min(), df['LapDistPct'].max(), num_points)
    
    result = {'LapDistPct': dist_new}
    
    for col in ['Lat', 'Lon', 'Speed', 'Throttle', 'Brake', 'SteeringWheelAngle']:
        if col in df.columns:
            try:
                f = interp1d(df['LapDistPct'].values, df[col].values, 
                           kind='linear', fill_value='extrapolate')
                result[col] = f(dist_new)
            except:
                pass
    
    return pd.DataFrame(result)


def find_corner_by_name(track_data, corner_name):
    """Find a corner in track data by name (case-insensitive partial match)."""
    if not track_data:
        return None
    
    corner_name_lower = corner_name.lower()
    
    # Search turns
    for turn in track_data.get('turn', []):
        if corner_name_lower in turn['name'].lower():
            return {**turn, 'type': 'turn'}
    
    # Search straights
    for straight in track_data.get('straight', []):
        if corner_name_lower in straight['name'].lower():
            return {**straight, 'type': 'straight'}
    
    return None


def create_corner_detail_visualization(current_df, reference_df, corner_name, output_path,
                                       track_id=None, current_name="Your Lap",
                                       reference_name="Reference", dark_mode=False,
                                       margin_pct=0.05):
    """
    Create detailed corner comparison visualization.
    
    Args:
        margin_pct: How much extra track to show before/after corner (default 5%)
    """
    # Load track data
    track_data = None
    corner_info = None
    if track_id:
        try:
            track_data = load_track_data(track_id)
            corner_info = find_corner_by_name(track_data, corner_name)
        except:
            pass
    
    if corner_info is None:
        print(f"Corner '{corner_name}' not found in track data")
        # Try to guess based on the corner name - assume it's 10% of lap
        corner_info = {'start': 0.75, 'end': 0.90, 'name': corner_name, 'type': 'turn'}
    
    # Interpolate data
    current_interp = interpolate_to_common_distance(current_df, num_points=3000)
    reference_interp = interpolate_to_common_distance(reference_df, num_points=3000)
    
    if current_interp is None or reference_interp is None:
        print("Error: Could not interpolate data")
        return None
    
    # Define corner boundaries with margin
    corner_start = max(0, corner_info['start'] - margin_pct)
    corner_end = min(1, corner_info['end'] + margin_pct)
    
    # Filter to corner region
    mask_current = (current_interp['LapDistPct'] >= corner_start) & \
                   (current_interp['LapDistPct'] <= corner_end)
    mask_ref = (reference_interp['LapDistPct'] >= corner_start) & \
               (reference_interp['LapDistPct'] <= corner_end)
    
    current_corner = current_interp[mask_current].copy()
    reference_corner = reference_interp[mask_ref].copy()
    
    if len(current_corner) == 0 or len(reference_corner) == 0:
        print("Error: No data in corner region")
        return None
    
    # Color scheme
    if dark_mode:
        bg_color = '#1a1a2e'
        panel_color = '#16213e'
        text_color = 'white'
        current_color = '#ff6b6b'
        ref_color = '#4cc9f0'
        grid_color = 'white'
        throttle_color = '#00ff88'
        brake_color = '#ff4757'
    else:
        bg_color = '#fafafa'
        panel_color = '#ffffff'
        text_color = '#1a1a2e'
        current_color = '#e63946'
        ref_color = '#0077b6'
        grid_color = '#cccccc'
        throttle_color = '#2a9d8f'
        brake_color = '#e63946'
    
    # Create figure
    fig = plt.figure(figsize=(16, 10))
    fig.patch.set_facecolor(bg_color)
    
    # ==========================================
    # Subplot 1: Zoomed racing line
    # ==========================================
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.set_facecolor(panel_color)
    
    if 'Lat' in current_corner.columns and 'Lon' in current_corner.columns:
        # Plot both lines
        ax1.plot(reference_corner['Lon'], reference_corner['Lat'],
                 color=ref_color, linewidth=4, alpha=0.6, label=reference_name)
        ax1.plot(current_corner['Lon'], current_corner['Lat'],
                 color=current_color, linewidth=3, alpha=0.9, label=current_name)
        
        # Mark entry and exit
        ax1.scatter(current_corner['Lon'].iloc[0], current_corner['Lat'].iloc[0],
                    color='green', s=100, marker='^', zorder=5, label='Entry')
        ax1.scatter(current_corner['Lon'].iloc[-1], current_corner['Lat'].iloc[-1],
                    color='orange', s=100, marker='v', zorder=5, label='Exit')
        
        # Arrow showing direction
        mid_idx = len(current_corner) // 2
        if mid_idx > 0 and mid_idx < len(current_corner) - 1:
            dx = current_corner['Lon'].iloc[mid_idx+1] - current_corner['Lon'].iloc[mid_idx-1]
            dy = current_corner['Lat'].iloc[mid_idx+1] - current_corner['Lat'].iloc[mid_idx-1]
            ax1.annotate('', xy=(current_corner['Lon'].iloc[mid_idx] + dx*0.3,
                                  current_corner['Lat'].iloc[mid_idx] + dy*0.3),
                        xytext=(current_corner['Lon'].iloc[mid_idx],
                                current_corner['Lat'].iloc[mid_idx]),
                        arrowprops=dict(arrowstyle='->', color=text_color, lw=2))
    
    ax1.set_xlabel('Longitude', color=text_color)
    ax1.set_ylabel('Latitude', color=text_color)
    ax1.set_title(f'{corner_info["name"]} - Racing Line Comparison',
                  fontsize=12, fontweight='bold', color=text_color)
    ax1.tick_params(colors=text_color)
    ax1.legend(loc='best', facecolor=panel_color, edgecolor=grid_color,
               labelcolor=text_color, fontsize=8)
    ax1.set_aspect('equal')
    ax1.grid(True, alpha=0.3, color=grid_color)
    for spine in ax1.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 2: Speed trace
    # ==========================================
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_facecolor(panel_color)
    
    dist_pct = current_corner['LapDistPct'].values * 100
    dist_pct_ref = reference_corner['LapDistPct'].values * 100
    
    if 'Speed' in current_corner.columns and 'Speed' in reference_corner.columns:
        ax2.plot(dist_pct_ref, reference_corner['Speed'], 
                 color=ref_color, linewidth=2.5, alpha=0.7, label=reference_name)
        ax2.plot(dist_pct, current_corner['Speed'], 
                 color=current_color, linewidth=2, alpha=0.9, label=current_name)
        
        # Fill the delta
        # Need to align the data points
        common_dist = np.linspace(corner_start*100, corner_end*100, 200)
        current_speed_interp = np.interp(common_dist, dist_pct, current_corner['Speed'])
        ref_speed_interp = np.interp(common_dist, dist_pct_ref, reference_corner['Speed'])
        
        ax2.fill_between(common_dist, current_speed_interp, ref_speed_interp,
                        where=(current_speed_interp >= ref_speed_interp),
                        color=throttle_color, alpha=0.3, label='You faster')
        ax2.fill_between(common_dist, current_speed_interp, ref_speed_interp,
                        where=(current_speed_interp < ref_speed_interp),
                        color=brake_color, alpha=0.3, label='You slower')
        
        # Mark min speed points
        current_min_idx = current_corner['Speed'].idxmin()
        ref_min_idx = reference_corner['Speed'].idxmin()
        
        if current_min_idx in current_corner.index:
            ax2.scatter(current_corner.loc[current_min_idx, 'LapDistPct'] * 100,
                       current_corner.loc[current_min_idx, 'Speed'],
                       color=current_color, s=80, marker='o', zorder=5, edgecolor='white')
            ax2.annotate(f'{current_corner.loc[current_min_idx, "Speed"]:.1f}',
                        xy=(current_corner.loc[current_min_idx, 'LapDistPct'] * 100,
                            current_corner.loc[current_min_idx, 'Speed']),
                        fontsize=9, color=current_color, fontweight='bold',
                        xytext=(5, -15), textcoords='offset points')
        
        if ref_min_idx in reference_corner.index:
            ax2.scatter(reference_corner.loc[ref_min_idx, 'LapDistPct'] * 100,
                       reference_corner.loc[ref_min_idx, 'Speed'],
                       color=ref_color, s=80, marker='o', zorder=5, edgecolor='white')
            ax2.annotate(f'{reference_corner.loc[ref_min_idx, "Speed"]:.1f}',
                        xy=(reference_corner.loc[ref_min_idx, 'LapDistPct'] * 100,
                            reference_corner.loc[ref_min_idx, 'Speed']),
                        fontsize=9, color=ref_color, fontweight='bold',
                        xytext=(5, 10), textcoords='offset points')
    
    ax2.set_xlabel('Lap Distance (%)', color=text_color)
    ax2.set_ylabel('Speed (km/h)', color=text_color)
    ax2.set_title(f'{corner_info["name"]} - Speed Comparison',
                  fontsize=12, fontweight='bold', color=text_color)
    ax2.tick_params(colors=text_color)
    ax2.legend(loc='best', facecolor=panel_color, edgecolor=grid_color,
               labelcolor=text_color, fontsize=8)
    ax2.grid(True, alpha=0.3, color=grid_color)
    for spine in ax2.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 3: Throttle & Brake
    # ==========================================
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.set_facecolor(panel_color)
    
    if 'Throttle' in current_corner.columns:
        ax3.plot(dist_pct, current_corner['Throttle'] * 100,
                 color=throttle_color, linewidth=2, alpha=0.9, 
                 label=f'{current_name} Throttle', linestyle='-')
        ax3.plot(dist_pct_ref, reference_corner['Throttle'] * 100,
                 color=throttle_color, linewidth=2, alpha=0.4,
                 label=f'{reference_name} Throttle', linestyle='--')
    
    if 'Brake' in current_corner.columns:
        ax3.plot(dist_pct, current_corner['Brake'] * 100,
                 color=brake_color, linewidth=2, alpha=0.9,
                 label=f'{current_name} Brake', linestyle='-')
        ax3.plot(dist_pct_ref, reference_corner['Brake'] * 100,
                 color=brake_color, linewidth=2, alpha=0.4,
                 label=f'{reference_name} Brake', linestyle='--')
    
    ax3.set_xlabel('Lap Distance (%)', color=text_color)
    ax3.set_ylabel('Pedal Input (%)', color=text_color)
    ax3.set_title(f'{corner_info["name"]} - Pedal Inputs',
                  fontsize=12, fontweight='bold', color=text_color)
    ax3.tick_params(colors=text_color)
    ax3.legend(loc='best', facecolor=panel_color, edgecolor=grid_color,
               labelcolor=text_color, fontsize=8)
    ax3.grid(True, alpha=0.3, color=grid_color)
    ax3.set_ylim(-5, 105)
    for spine in ax3.spines.values():
        spine.set_color(grid_color)
    
    # ==========================================
    # Subplot 4: Analysis summary
    # ==========================================
    ax4 = fig.add_subplot(2, 2, 4)
    ax4.set_facecolor(panel_color)
    ax4.axis('off')
    
    # Calculate stats
    stats = {}
    if 'Speed' in current_corner.columns and 'Speed' in reference_corner.columns:
        stats['current_min_speed'] = current_corner['Speed'].min()
        stats['ref_min_speed'] = reference_corner['Speed'].min()
        stats['min_speed_diff'] = stats['current_min_speed'] - stats['ref_min_speed']
        
        stats['current_exit_speed'] = current_corner['Speed'].iloc[-10:].mean()
        stats['ref_exit_speed'] = reference_corner['Speed'].iloc[-10:].mean()
        stats['exit_speed_diff'] = stats['current_exit_speed'] - stats['ref_exit_speed']
        
        stats['current_entry_speed'] = current_corner['Speed'].iloc[:10].mean()
        stats['ref_entry_speed'] = reference_corner['Speed'].iloc[:10].mean()
        stats['entry_speed_diff'] = stats['current_entry_speed'] - stats['ref_entry_speed']
    
    # Estimate time difference through corner
    if 'Speed' in current_corner.columns and track_data:
        track_length = track_data.get('length', 2340)  # Lime Rock default
        corner_length_m = track_length * (corner_end - corner_start)
        
        current_avg_speed_ms = current_corner['Speed'].mean() / 3.6
        ref_avg_speed_ms = reference_corner['Speed'].mean() / 3.6
        
        current_time = corner_length_m / current_avg_speed_ms
        ref_time = corner_length_m / ref_avg_speed_ms
        time_diff = current_time - ref_time
        stats['time_diff'] = time_diff
    else:
        stats['time_diff'] = 0
    
    analysis_text = f"""
╔═══════════════════════════════════════════════╗
║     {corner_info['name'].upper():^37}     ║
║              CORNER ANALYSIS                  ║
╠═══════════════════════════════════════════════╣

  ENTRY SPEED:
    You:       {stats.get('current_entry_speed', 0):6.1f} km/h
    Reference: {stats.get('ref_entry_speed', 0):6.1f} km/h
    Delta:     {stats.get('entry_speed_diff', 0):+6.1f} km/h

  MINIMUM SPEED (Apex):
    You:       {stats.get('current_min_speed', 0):6.1f} km/h
    Reference: {stats.get('ref_min_speed', 0):6.1f} km/h
    Delta:     {stats.get('min_speed_diff', 0):+6.1f} km/h

  EXIT SPEED:
    You:       {stats.get('current_exit_speed', 0):6.1f} km/h
    Reference: {stats.get('ref_exit_speed', 0):6.1f} km/h
    Delta:     {stats.get('exit_speed_diff', 0):+6.1f} km/h

  ESTIMATED TIME LOSS:
    {stats.get('time_diff', 0):+.3f} seconds

╚═══════════════════════════════════════════════╝

KEY OBSERVATIONS:
"""
    
    # Add observations based on data
    observations = []
    if stats.get('exit_speed_diff', 0) < -2:
        observations.append("• Exit speed is LOW - use more track on exit!")
    if stats.get('min_speed_diff', 0) < -3:
        observations.append("• Apex speed is LOW - tighter line or over-slowing")
    if stats.get('entry_speed_diff', 0) < -2:
        observations.append("• Entry speed is LOW - brake later?")
    if stats.get('exit_speed_diff', 0) > 2:
        observations.append("• EXIT speed is GOOD!")
    if stats.get('time_diff', 0) > 0.1:
        observations.append(f"• Losing ~{stats.get('time_diff', 0):.2f}s in this corner alone!")
    
    if not observations:
        observations.append("• Performance is close to reference")
    
    analysis_text += "\n".join(observations)
    
    ax4.text(0.05, 0.95, analysis_text, transform=ax4.transAxes,
             fontsize=10, color=text_color, family='monospace',
             verticalalignment='top')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, facecolor=fig.get_facecolor(),
                edgecolor='none', bbox_inches='tight')
    plt.close()
    
    print(f"Corner detail saved to: {output_path}")
    
    return stats


def main():
    if len(sys.argv) < 4:
        print(json.dumps({
            "error": 'Usage: python visualize_corner_detail.py <your_lap.csv> <reference_lap.csv> <corner_name> [output.png] [track_id] [--dark]'
        }))
        sys.exit(1)
    
    dark_mode = '--dark' in sys.argv
    args = [a for a in sys.argv if a != '--dark']
    
    current_file = Path(args[1])
    reference_file = Path(args[2])
    corner_name = args[3]
    output_path = args[4] if len(args) > 4 else f"corner_{corner_name.replace(' ', '_')}.png"
    track_id = args[5] if len(args) > 5 else None
    
    if not current_file.exists():
        print(json.dumps({"error": f"Current lap file not found: {current_file}"}))
        sys.exit(1)
    
    if not reference_file.exists():
        print(json.dumps({"error": f"Reference lap file not found: {reference_file}"}))
        sys.exit(1)
    
    # Extract names from filenames
    current_name = "Your Lap"
    reference_name = "Reference"
    
    ref_filename = reference_file.stem
    if " - " in ref_filename:
        parts = ref_filename.split(" - ")
        if len(parts) >= 2:
            reference_name = parts[1]
    
    curr_filename = current_file.stem
    if " - " in curr_filename:
        parts = curr_filename.split(" - ")
        if len(parts) >= 2:
            current_name = parts[1]
    
    # Load telemetry
    current_df = load_telemetry(current_file)
    reference_df = load_telemetry(reference_file)
    
    if current_df is None or reference_df is None:
        print(json.dumps({"error": "Could not load telemetry files"}))
        sys.exit(1)
    
    # Create visualization
    stats = create_corner_detail_visualization(
        current_df, reference_df, corner_name, output_path,
        track_id=track_id,
        current_name=current_name,
        reference_name=reference_name,
        dark_mode=dark_mode
    )
    
    if stats:
        print(json.dumps(stats, indent=2, default=float))


if __name__ == "__main__":
    main()

