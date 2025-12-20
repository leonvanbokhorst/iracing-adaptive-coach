"""Formatted analysis output for Little Padawan"""
from tools.core.time_formatter import format_laptime, format_laptime_short, format_delta_short


def print_session_analysis(analysis, sectors=None):
    """Print formatted session analysis with proper lap time formatting"""
    
    print("\n📊 Session Analysis:")
    print(f"   Best lap: {format_laptime(analysis['best_lap'])}")
    print(f"   Average: {format_laptime(analysis['avg_lap'])} ({format_delta_short(analysis['avg_lap'] - analysis['best_lap'])})")
    print(f"   Consistency (σ): {analysis['sigma']:.3f}s")
    print(f"   Clean laps: {analysis['clean_laps']}/{analysis['total_laps']}")
    
    if sectors:
        print("\n🎯 Sector Breakdown:")
        
        # Find sector with most loss
        max_loss_sector = max(sectors.items(), key=lambda x: x[1]['loss_per_lap'])
        
        for sector_name, data in sectors.items():
            is_problem = sector_name == max_loss_sector[0]
            marker = " ← Focus here!" if is_problem else ""
            
            print(f"   {sector_name}:")
            print(f"      Best: {data['best']:.3f}s")
            print(f"      Average: {data['avg']:.3f}s ({format_delta_short(data['loss_per_lap'])} per lap){marker}")
            print(f"      Total loss: {data['total_loss']:.2f}s")
    
    print()


def print_coaching_summary(analysis, sectors=None):
    """Print coaching-focused summary"""
    
    print(f"\n💬 Little Padawan says:")
    print(f"   Master Lonn, I see {analysis['clean_laps']} clean laps.")
    print(f"   Your best: {format_laptime(analysis['best_lap'])}")
    print(f"   Consistency: σ = {analysis['sigma']:.2f}s", end="")
    
    # Consistency assessment
    if analysis['sigma'] < 0.5:
        print(" (excellent!)")
    elif analysis['sigma'] < 1.0:
        print(" (good)")
    elif analysis['sigma'] < 1.5:
        print(" (moderate)")
    else:
        print(" (needs work)")
    
    if sectors:
        # Find problem sector
        max_loss_sector = max(sectors.items(), key=lambda x: x[1]['loss_per_lap'])
        sector_name, sector_data = max_loss_sector
        
        # Calculate relative loss
        other_sectors_avg_loss = sum(s['loss_per_lap'] for n, s in sectors.items() if n != sector_name) / (len(sectors) - 1)
        multiplier = sector_data['loss_per_lap'] / other_sectors_avg_loss if other_sectors_avg_loss > 0 else 1
        
        print(f"\n   {sector_name} is your focus area:")
        print(f"   - Loss per lap: {sector_data['loss_per_lap']:.2f}s")
        print(f"   - That's {multiplier:.1f}x more than other sectors!")
        print(f"   - Best: {sector_data['best']:.2f}s, Average: {sector_data['avg']:.2f}s")
    
    print()


def format_comparison(current, previous):
    """Format comparison between two sessions"""
    
    delta = current - previous
    
    if abs(delta) < 0.01:
        return "no change"
    elif delta < 0:
        return f"improved by {abs(delta):.2f}s ✓"
    else:
        return f"slower by {delta:.2f}s"
