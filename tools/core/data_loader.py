"""Core data loading utilities for the adaptive coaching system"""
import pandas as pd
import json
from pathlib import Path
from tools.core.time_formatter import format_laptime, format_laptime_short


def load_learning_memory():
    """Load learning memory or create if doesn't exist"""
    memory_path = Path('learning_memory.json')
    
    if not memory_path.exists():
        memory = {
            "driver": {"name": "Master Lonn", "started": str(pd.Timestamp.now().date())},
            "current_focus": None,
            "mastered_skills": [],
            "learning_patterns": {"responds_well_to": [], "struggles_with": []},
            "tool_usage_history": {},
            "session_history": []
        }
        save_learning_memory(memory)
    else:
        with open(memory_path, 'r') as f:
            memory = json.load(f)
    
    return memory


def save_learning_memory(memory):
    """Save learning memory"""
    with open('learning_memory.json', 'w') as f:
        json.dump(memory, f, indent=2)


def load_session_data(csv_path):
    """Load session CSV with smart cleaning for outliers and partial laps"""
    df = pd.read_csv(csv_path)
    
    # Normalize column names (Garage 61 uses spaces, we use no spaces)
    df.columns = df.columns.str.strip()
    column_map = {
        'Lap time': 'LapTime',
        'Started at': 'StartedAt',
        'Pit in': 'PitIn',
        'Pit out': 'PitOut',
        'Track temp': 'TrackTemp',
        'Track usage': 'TrackUsage',
        'Air temperature': 'AirTemp',
        'Cloud cover': 'CloudCover',
        'Air density': 'AirDensity',
        'Air pressure': 'AirPressure',
        'Wind velocity': 'WindVelocity',
        'Wind direction': 'WindDirection',
        'Relative humidity': 'RelativeHumidity',
        'Fog level': 'FogLevel',
        'Track Wetness': 'TrackWetness',
        'Fuel level': 'FuelLevel',
        'Fuel used': 'FuelUsed',
        'Fuel added': 'FuelAdded'
    }
    df = df.rename(columns=column_map)
    
    # Remove invalid laps (zeros, negatives, NaN)
    df = df[df['LapTime'] > 0]
    df = df.dropna(subset=['LapTime'])
    
    if len(df) == 0:
        return df
    
    # Remove extreme outliers (pit stops, partial laps)
    # Use median-based method: flag laps that are WAY off (2x median or more)
    # This catches pit stops but keeps crashes (which are just slow laps)
    median_time = df['LapTime'].median()
    
    # Upper bound: 2x median (catches pit stops, not crashes)
    # Lower bound: 0.5x median (catches partial laps)
    upper_bound = median_time * 2.0
    lower_bound = median_time * 0.5
    
    # Mark outliers but keep them in dataframe for reference
    df['is_outlier'] = (df['LapTime'] < lower_bound) | (df['LapTime'] > upper_bound)
    
    # Mark dirty laps (incidents or outliers)
    # Garage 61 provides 'Clean' column (1=clean, 0=incident)
    if 'Clean' in df.columns:
        df['clean'] = (df['Clean'] == 1) & (~df['is_outlier'])
    elif 'Inc' in df.columns:
        df['clean'] = (df['Inc'] == 0) & (~df['is_outlier'])
    else:
        df['clean'] = ~df['is_outlier']
    
    # Additional sector cleaning if sectors exist
    sectors = ['Sector 1', 'Sector 2', 'Sector 3', 'Sector 4']
    for sector in sectors:
        if sector in df.columns:
            # Remove sector times that are clearly invalid
            df.loc[df[sector] <= 0, sector] = pd.NA
            
            # Mark laps with invalid sector times as not clean
            df.loc[df[sector].isna(), 'clean'] = False
    
    return df


def analyze_session_basic(df):
    """Basic session analysis"""
    clean_df = df[df['clean']]
    
    if len(clean_df) == 0:
        return None
    
    return {
        'total_laps': len(df),
        'clean_laps': len(clean_df),
        'best_lap': float(clean_df['LapTime'].min()),
        'avg_lap': float(clean_df['LapTime'].mean()),
        'sigma': float(clean_df['LapTime'].std()),
        'median_lap': float(clean_df['LapTime'].median())
    }


def analyze_sectors(df):
    """Sector analysis if available"""
    sectors = ['Sector 1', 'Sector 2', 'Sector 3', 'Sector 4']
    sector_analysis = {}
    
    clean_df = df[df['clean']]
    if len(clean_df) == 0:
        return sector_analysis
    
    for sector in sectors:
        if sector in df.columns:
            sector_times = clean_df[sector]
            
            sector_analysis[sector] = {
                'best': float(sector_times.min()),
                'avg': float(sector_times.mean()),
                'worst': float(sector_times.max()),
                'sigma': float(sector_times.std()),
                'loss_per_lap': float(sector_times.mean() - sector_times.min()),
                'total_loss': float((sector_times.mean() - sector_times.min()) * len(sector_times))
            }
    
    return sector_analysis


def update_session_history(analysis):
    """Add session to history"""
    memory = load_learning_memory()
    
    session_entry = {
        'date': str(pd.Timestamp.now().date()),
        'timestamp': str(pd.Timestamp.now()),
        'best_lap': analysis['best_lap'],
        'sigma': analysis['sigma'],
        'total_laps': analysis['total_laps'],
        'clean_laps': analysis['clean_laps'],
        'current_focus': memory.get('current_focus', {}).get('skill') if memory.get('current_focus') else None
    }
    
    memory['session_history'].append(session_entry)
    save_learning_memory(memory)
    
    return session_entry
