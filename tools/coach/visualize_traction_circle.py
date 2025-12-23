#!/usr/bin/env python3
"""
Visualize the Traction Circle (Friction Circle)

Demonstrates how braking and cornering forces combine on a tire.
Shows the limit of grip and example points from the weight transfer guide.

Usage:
    python tools/coach/visualize_traction_circle.py [--output path/to/save.png]
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import argparse
from pathlib import Path


def create_traction_circle_basic(output_path=None):
    """Create basic traction circle with example points"""
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw the circle (grip limit)
    circle = plt.Circle((0, 0), 1.0, color='#2ecc71', fill=False, linewidth=3, label='Grip Limit (100%)')
    ax.add_patch(circle)
    
    # Fill inside (safe zone)
    circle_fill = plt.Circle((0, 0), 1.0, color='#2ecc71', alpha=0.1)
    ax.add_patch(circle_fill)
    
    # Example points from the guide (CLEAN, NON-OVERLAPPING)
    # X-axis: LEFT turn = positive (right), RIGHT turn = negative (left)
    # Y-axis: ACCELERATION = positive (up), BRAKING = negative (down)
    examples = [
        # (lateral, longitudinal, label, color, offset_x, offset_y, ha)
        (0.0, -1.0, "Straight\nBraking", '#e74c3c', 0.3, 0.0, 'left'),
        (0.707, -0.707, "Trail Braking\n(70.7% + 70.7%)", '#3498db', -0.35, 0.0, 'right'),
        (0.866, -0.5, "Light Trail", '#9b59b6', 0.15, -0.1, 'left'),
        (1.0, 0.0, "Pure\nCornering", '#f39c12', 0.15, 0.0, 'left'),
        (0.0, 1.0, "Full\nThrottle", '#2ecc71', -0.15, 0.1, 'right'),
        (1.05, -1.05, "OVER LIMIT\nSliding!", '#ff0000', -0.15, 0.1, 'right'),
    ]
    
    # Plot points
    for lateral, longitudinal, label, color, offset_x, offset_y, ha in examples:
        # Check if over limit
        over_limit = (lateral**2 + longitudinal**2) > 1.0
        marker = 'x' if over_limit else 'o'
        size = 300 if over_limit else 250
        alpha = 0.9
        
        ax.scatter(lateral, longitudinal, s=size, c=color, marker=marker, 
                  edgecolors='black', linewidths=2, alpha=alpha, zorder=3)
        
        ax.annotate(label, (lateral, longitudinal), 
                   xytext=(lateral + offset_x, longitudinal + offset_y),
                   fontsize=9, ha=ha, va='center', fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.4', facecolor=color, alpha=0.3, edgecolor='black', linewidth=1.5),
                   zorder=2)
    
    # Draw axes
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add quadrant labels (HUMAN-ORIENTED!)
    ax.text(0.05, 0.5, 'ACCELERATION', ha='left', va='center', fontsize=12, fontweight='bold')
    ax.text(0.05, -0.5, 'BRAKING', ha='left', va='center', fontsize=12, fontweight='bold')
    ax.text(0.5, 0.05, 'LEFT TURN', ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.text(-0.5, 0.05, 'RIGHT TURN', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Styling
    ax.set_xlim(-1.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xlabel('Lateral Force (← Right Turn | Left Turn →)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Longitudinal Force (↓ Braking | Acceleration ↑)', fontsize=12, fontweight='bold')
    ax.set_title('The Traction Circle: How Forces Combine on a Tire\n(As YOU Feel It in the Car)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend
    legend_text = (
        "The circle represents 100% of available grip.\n"
        "Points inside the circle are safe.\n"
        "Points outside the circle = tire slides!"
    )
    ax.text(0, -1.15, legend_text, ha='center', fontsize=10, 
           style='italic', bbox=dict(boxstyle='round,pad=0.7', 
           facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved basic traction circle to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def create_trail_braking_path(output_path=None):
    """Create traction circle showing typical trail braking path"""
    
    fig, ax = plt.subplots(figsize=(10, 10))
    
    # Draw the circle (grip limit)
    circle = plt.Circle((0, 0), 1.0, color='#2ecc71', fill=False, linewidth=3, label='Grip Limit')
    ax.add_patch(circle)
    
    # Fill inside (safe zone)
    circle_fill = plt.Circle((0, 0), 1.0, color='#2ecc71', alpha=0.1)
    ax.add_patch(circle_fill)
    
    # Create trail braking path (LEFT turn)
    # Typical path: brake hard → trail brake into corner → apex → power out
    # X-axis: lateral (left turn = positive right)
    # Y-axis: longitudinal (acceleration = up, braking = down)
    
    phases = [
        # Phase 1: Heavy braking (straight line)
        {'lateral': np.zeros(20), 'longitudinal': np.linspace(-0.3, -1.0, 20),
         'label': '1. Heavy Braking', 'color': '#e74c3c'},
        
        # Phase 2: Trail braking (reducing brake, adding left turn)
        {'lateral': np.sqrt(1.0 - np.linspace(1.0, 0.4, 30)**2),
         'longitudinal': -np.linspace(1.0, 0.4, 30),
         'label': '2. Trail Braking', 'color': '#3498db'},
        
        # Phase 3: Apex (minimal brake, max left turn)
        {'lateral': np.sqrt(1.0 - np.linspace(0.4, 0.0, 15)**2),
         'longitudinal': -np.linspace(0.4, 0.0, 15),
         'label': '3. Apex', 'color': '#f39c12'},
        
        # Phase 4: Exit (adding throttle, reducing left turn)
        {'lateral': np.sqrt(1.0 - np.linspace(0.0, 0.7, 25)**2),
         'longitudinal': np.linspace(0.0, 0.7, 25),
         'label': '4. Power Out', 'color': '#9b59b6'},
        
        # Phase 5: Full throttle (straightening)
        {'lateral': np.sqrt(1.0 - np.linspace(0.7, 1.0, 15)**2) * np.linspace(1, 0.3, 15),
         'longitudinal': np.linspace(0.7, 1.0, 15),
         'label': '5. Full Throttle', 'color': '#2ecc71'},
    ]
    
    # Plot path
    for i, phase in enumerate(phases):
        ax.plot(phase['lateral'], phase['longitudinal'], 
               color=phase['color'], linewidth=3, 
               label=phase['label'], zorder=2)
        
        # Add direction arrows
        if i < len(phases) - 1:
            next_phase = phases[i + 1]
            dx = next_phase['lateral'][0] - phase['lateral'][-1]
            dy = next_phase['longitudinal'][0] - phase['longitudinal'][-1]
            ax.arrow(phase['lateral'][-1], phase['longitudinal'][-1], 
                    dx * 0.3, dy * 0.3,
                    head_width=0.06, head_length=0.04, 
                    fc=phase['color'], ec=phase['color'], 
                    linewidth=2, zorder=3)
    
    # Add start and finish markers
    ax.scatter(0, -0.3, s=300, c='green', marker='v', 
              edgecolors='black', linewidths=2, zorder=4, label='Start (Brake)')
    ax.scatter(phases[-1]['lateral'][-1], 1.0, s=300, c='red', marker='^',
              edgecolors='black', linewidths=2, zorder=4, label='Finish (Accel)')
    
    # Draw axes
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    
    # Add quadrant labels (HUMAN-ORIENTED!)
    ax.text(0.05, 0.65, 'ACCELERATION', ha='left', va='center', fontsize=12, fontweight='bold')
    ax.text(0.05, -0.65, 'BRAKING', ha='left', va='center', fontsize=12, fontweight='bold')
    ax.text(0.65, 0.05, 'LEFT\nTURN', ha='center', va='bottom', fontsize=12, fontweight='bold')
    
    # Styling
    ax.set_xlim(-0.3, 1.3)
    ax.set_ylim(-1.3, 1.3)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3, linestyle=':', linewidth=0.5)
    ax.set_xlabel('Lateral Force (← Right Turn | Left Turn →)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Longitudinal Force (↓ Braking | Acceleration ↑)', fontsize=12, fontweight='bold')
    ax.set_title('Trail Braking Path Through a Left Turn\n(As YOU Feel It: Brake Down → Turn Right → Accel Up)', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add legend
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    
    # Add description
    desc_text = (
        "Perfect trail braking keeps the tire at the grip limit (on the circle)\n"
        "throughout the corner, maximizing speed and control."
    )
    ax.text(0, -0.2, desc_text, ha='center', fontsize=10, 
           style='italic', bbox=dict(boxstyle='round,pad=0.7', 
           facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved trail braking path to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def create_comparison_good_vs_bad(output_path=None):
    """Compare good (smooth) vs bad (abrupt) weight transfer paths"""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    # Good path (smooth)
    # X-axis: lateral (left turn = positive right)
    # Y-axis: longitudinal (acceleration = up, braking = down)
    ax = ax1
    circle = plt.Circle((0, 0), 1.0, color='#2ecc71', fill=False, linewidth=3)
    ax.add_patch(circle)
    circle_fill = plt.Circle((0, 0), 1.0, color='#2ecc71', alpha=0.1)
    ax.add_patch(circle_fill)
    
    # Smooth path around circle (LEFT TURN)
    lateral_smooth = np.concatenate([
        np.zeros(15),  # Straight
        np.sqrt(np.maximum(0, 1.0 - np.linspace(1.0, 0.0, 30)**2)),  # Adding left turn
        np.sqrt(np.maximum(0, 1.0 - np.linspace(0.0, 0.8, 25)**2)) * np.linspace(1, 0.5, 25),  # Exit
    ])
    longitudinal_smooth = np.concatenate([
        -np.linspace(0.2, 1.0, 15),  # Brake
        -np.linspace(1.0, 0.0, 30),  # Trail brake
        np.linspace(0.0, 0.8, 25),   # Throttle
    ])
    
    ax.plot(lateral_smooth, longitudinal_smooth, color='#2ecc71', linewidth=4, 
           label='Smooth Trail Braking', zorder=2)
    ax.scatter(lateral_smooth[0], longitudinal_smooth[0], s=200, c='green', marker='v', 
              edgecolors='black', linewidths=2, zorder=3)
    
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Lateral Force (Left Turn →)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Longitudinal Force (↓ Brake | Accel ↑)', fontsize=11, fontweight='bold')
    ax.set_title('✅ GOOD: Smooth Weight Transfer\n(Stays on the circle)', 
                fontsize=13, fontweight='bold', color='#2ecc71', pad=15)
    ax.legend(loc='upper right', fontsize=10)
    
    # Bad path (abrupt)
    ax = ax2
    circle = plt.Circle((0, 0), 1.0, color='#2ecc71', fill=False, linewidth=3)
    ax.add_patch(circle)
    circle_fill = plt.Circle((0, 0), 1.0, color='#2ecc71', alpha=0.1)
    ax.add_patch(circle_fill)
    
    # Abrupt path with overshoot (LEFT TURN)
    lateral_bad = np.array([0.0, 0.0, 0.0, 0.4, 0.9, 0.9, 1.0, 1.0, 0.8, 0.8, 0.4])
    longitudinal_bad = np.array([-0.2, -1.0, -1.0, -0.6, -0.6, 0.0, 0.0, 0.3, 0.3, 0.8, 0.8])
    
    ax.plot(lateral_bad, longitudinal_bad, color='#e74c3c', linewidth=4, 
           linestyle='--', label='Abrupt Transitions', zorder=2)
    ax.scatter(lateral_bad[0], longitudinal_bad[0], s=200, c='green', marker='v', 
              edgecolors='black', linewidths=2, zorder=3)
    
    # Mark overshoot points
    overshoot_indices = [4, 6]
    ax.scatter(lateral_bad[overshoot_indices], longitudinal_bad[overshoot_indices], 
              s=300, c='red', marker='x', linewidths=4, zorder=4, 
              label='⚠️ Over Limit (Sliding!)')
    
    ax.axhline(y=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.axvline(x=0, color='gray', linestyle='--', linewidth=1, alpha=0.5)
    ax.set_xlim(-0.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    ax.set_xlabel('Lateral Force (Left Turn →)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Longitudinal Force (↓ Brake | Accel ↑)', fontsize=11, fontweight='bold')
    ax.set_title('❌ BAD: Abrupt Weight Transfer\n(Exceeds the circle)', 
                fontsize=13, fontweight='bold', color='#e74c3c', pad=15)
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"✅ Saved comparison to: {output_path}")
    else:
        plt.show()
    
    plt.close()


def main():
    parser = argparse.ArgumentParser(
        description='Visualize the traction circle with synthetic data'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default='docs/assets',
        help='Directory to save visualizations (default: docs/assets)'
    )
    parser.add_argument(
        '--show',
        action='store_true',
        help='Display plots instead of saving'
    )
    
    args = parser.parse_args()
    
    if args.show:
        print("🎨 Generating visualizations (display mode)...")
        create_traction_circle_basic()
        create_trail_braking_path()
        create_comparison_good_vs_bad()
    else:
        # Create output directory
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print("🎨 Generating traction circle visualizations...")
        
        # Generate all three visualizations
        create_traction_circle_basic(
            output_dir / 'traction-circle-basic.png'
        )
        create_trail_braking_path(
            output_dir / 'traction-circle-trail-braking.png'
        )
        create_comparison_good_vs_bad(
            output_dir / 'traction-circle-comparison.png'
        )
        
        print("\n✨ All visualizations created!")
        print(f"📁 Location: {output_dir}/")
        print("\nGenerated files:")
        print("  1. traction-circle-basic.png - Basic concepts with example points")
        print("  2. traction-circle-trail-braking.png - Path through a corner")
        print("  3. traction-circle-comparison.png - Good vs Bad technique")


if __name__ == "__main__":
    main()

