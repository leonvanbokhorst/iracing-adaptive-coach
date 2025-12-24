#!/usr/bin/env python3
"""
Report Condenser

Post-processing utility to retroactively fix reports:
- Remove redundant "Translation" sections
- Condense lap lists to outliers only
- Reduce emphasis overuse
- Merge redundant sections

Usage:
    python tools/core/condense_report.py weeks/week02/session.md
    # Creates weeks/week02/session.md.condensed
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

from tools.core.format_lap_summary import format_lap_summary


def remove_redundant_translations(text: str) -> str:
    """Remove redundant 'Translation' sections after tables"""
    # Pattern: table followed by "Translation:" or "What This Means:"
    # Only remove if the translation just repeats table data
    
    # Match table + translation pattern
    pattern = r'(\|[^\n]+\|\n(?:\|[^\n]+\|\n)*)\n\n\*\*Translation\*\*:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|$)'
    
    def should_remove_translation(match):
        table = match.group(1)
        translation = match.group(2)
        
        # Extract numbers from table
        table_numbers = re.findall(r'[\d.]+', table)
        translation_numbers = re.findall(r'[\d.]+', translation)
        
        # If translation just repeats table numbers, remove it
        if translation_numbers and all(num in table_numbers for num in translation_numbers[:3]):
            return True
        return False
    
    def replacer(match):
        if should_remove_translation(match):
            return match.group(1)  # Keep table, remove translation
        return match.group(0)  # Keep both
    
    text = re.sub(pattern, replacer, text, flags=re.MULTILINE)
    
    # Also remove standalone "What This Means:" that just repeat table data
    pattern2 = r'\*\*What This Means\*\*:\s*([^\n]+(?:\n[^\n]+)*?)(?=\n\n|$)'
    # This is more complex - would need semantic analysis
    # For now, just remove obvious repeats
    
    return text


def condense_lap_lists(text: str) -> str:
    """Condense lap-by-lap lists to outliers only"""
    
    # Pattern: "All Clean Lap Times:" or similar followed by numbered list
    pattern = r'\*\*All Clean Lap Times\*\*:\s*\n((?:\d+\.\s*[\d:.]+\s*(?:←.*)?\n)+)'
    
    def replace_lap_list(match):
        lap_list_text = match.group(1)
        
        # Extract lap times
        lap_times = []
        for line in lap_list_text.strip().split('\n'):
            # Extract time from "1. 1:28.572" or "1. 88.572"
            time_match = re.search(r'[\d:]+\.?\d+', line)
            if time_match:
                time_str = time_match.group(0)
                # Convert to seconds
                if ':' in time_str:
                    parts = time_str.split(':')
                    seconds = int(parts[0]) * 60 + float(parts[1])
                else:
                    seconds = float(time_str)
                lap_times.append(seconds)
        
        if len(lap_times) > 3:  # Only condense if more than 3 laps
            summary = format_lap_summary(lap_times, show_full_list=False, include_lap_numbers=True)
            return summary['markdown']
        else:
            return match.group(0)  # Keep original if 3 or fewer
    
    text = re.sub(pattern, replace_lap_list, text)
    
    return text


def reduce_emphasis(text: str) -> str:
    """Reduce emphasis overuse"""
    
    # Split into paragraphs
    paragraphs = re.split(r'\n\n+', text)
    result = []
    
    for para in paragraphs:
        # Skip tables
        if para.strip().startswith('|'):
            result.append(para)
            continue
        
        # Count bold in paragraph
        bold_matches = list(re.finditer(r'\*\*([^*]+)\*\*', para))
        
        if len(bold_matches) > 2:
            # Keep first 2 bold, remove rest
            kept = set()
            for i, match in enumerate(bold_matches[:2]):
                kept.add(match.group(0))
            
            # Remove bold from matches not kept
            for match in bold_matches[2:]:
                para = para.replace(match.group(0), match.group(1), 1)
        
        # Reduce CAPS words (keep first one, lowercase rest)
        caps_words = re.finditer(r'\b([A-Z]{3,})\b', para)
        caps_list = list(caps_words)
        if len(caps_list) > 1:
            for match in caps_list[1:]:
                para = para.replace(match.group(0), match.group(1).capitalize(), 1)
        
        result.append(para)
    
    return '\n\n'.join(result)


def condense_report(file_path: str, output_path: str = None) -> str:
    """
    Condense a report file.
    
    Args:
        file_path: Path to input report
        output_path: Path to output report (default: input_path.condensed)
    
    Returns:
        Path to condensed report
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    text = path.read_text()
    
    # Apply condensations
    text = remove_redundant_translations(text)
    text = condense_lap_lists(text)
    text = reduce_emphasis(text)
    
    # Write output
    if output_path is None:
        output_path = str(path) + '.condensed'
    
    output = Path(output_path)
    output.write_text(text)
    
    return str(output)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: condense_report.py <report_file.md> [output_file.md]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        result = condense_report(input_file, output_file)
        print(f"✓ Condensed report saved to: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

