"""Time formatting utilities for lap times"""


def format_laptime(seconds):
    """
    Format lap time from seconds to M:SS.mmm format
    
    Examples:
        80.356 -> "1:20.356"
        90.290 -> "1:30.290"
        125.450 -> "2:05.450"
        45.123 -> "45.123"
    """
    if seconds < 0:
        return "Invalid"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes > 0:
        return f"{minutes}:{remaining_seconds:06.3f}"
    else:
        return f"{remaining_seconds:.3f}"


def format_laptime_short(seconds):
    """
    Format lap time with 2 decimal places for cleaner display
    
    Examples:
        80.356 -> "1:20.36"
        90.290 -> "1:30.29"
    """
    if seconds < 0:
        return "Invalid"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes > 0:
        return f"{minutes}:{remaining_seconds:05.2f}"
    else:
        return f"{remaining_seconds:.2f}"


def format_delta(seconds):
    """
    Format time delta with + or - sign
    
    Examples:
        0.356 -> "+0.356"
        -0.125 -> "-0.125"
        1.234 -> "+1.234"
    """
    if seconds >= 0:
        return f"+{seconds:.3f}"
    else:
        return f"{seconds:.3f}"


def format_delta_short(seconds):
    """
    Format time delta with 2 decimal places
    
    Examples:
        0.356 -> "+0.36"
        -0.125 -> "-0.13"
    """
    if seconds >= 0:
        return f"+{seconds:.2f}"
    else:
        return f"{seconds:.2f}"


def parse_laptime(time_str):
    """
    Parse lap time string back to seconds
    
    Examples:
        "1:20.356" -> 80.356
        "45.123" -> 45.123
    """
    if ':' in time_str:
        parts = time_str.split(':')
        minutes = int(parts[0])
        seconds = float(parts[1])
        return minutes * 60 + seconds
    else:
        return float(time_str)
