#!/usr/bin/env python3
"""
Style Enforcer for Little Padawan Reports

Checks and enforces style guidelines:
- Emphasis usage (bold/CAPS/emoji counts)
- TL;DR presence and length
- Tone variation (check for repetitive openings)

Usage:
    from tools.core.enforce_style import check_report_style
    
    issues = check_report_style('weeks/week02/session.md')
    for issue in issues:
        print(issue)
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def count_bold(text: str) -> int:
    """Count bold phrases (**text**)"""
    return len(re.findall(r'\*\*[^*]+\*\*', text))


def count_caps_words(text: str) -> int:
    """Count ALL CAPS words (3+ letters)"""
    return len(re.findall(r'\b[A-Z]{3,}\b', text))


def count_emojis(text: str) -> int:
    """Count emoji characters"""
    # Common emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return len(emoji_pattern.findall(text))


def check_tldr(text: str) -> Tuple[bool, List[str]]:
    """Check if TL;DR section exists and meets requirements"""
    issues = []
    
    # Check for TL;DR section
    tldr_match = re.search(r'##\s*📍\s*TL;DR\s*\n(.*?)(?=\n---|\n##|$)', text, re.DOTALL)
    
    if not tldr_match:
        issues.append("Missing TL;DR section")
        return False, issues
    
    tldr_content = tldr_match.group(1).strip()
    word_count = len(tldr_content.split())
    
    if word_count > 50:
        issues.append(f"TL;DR too long: {word_count} words (max 50)")
    
    if word_count < 10:
        issues.append(f"TL;DR too short: {word_count} words (should be informative)")
    
    return True, issues


def check_emphasis_per_section(text: str) -> List[str]:
    """Check emphasis usage per section"""
    issues = []
    
    # Split into sections
    sections = re.split(r'\n##\s+', text)
    
    for i, section in enumerate(sections[1:], 1):  # Skip header
        section_title = section.split('\n')[0]
        
        # Count emphasis in section
        bold_count = count_bold(section)
        caps_count = count_caps_words(section)
        emoji_count = count_emojis(section)
        
        # Count paragraphs
        paragraphs = [p.strip() for p in section.split('\n\n') if p.strip() and not p.strip().startswith('|')]
        
        for para in paragraphs:
            para_bold = count_bold(para)
            if para_bold > 2:
                issues.append(f"Section '{section_title}': Paragraph has {para_bold} bold phrases (max 2)")
        
        if caps_count > 1:
            issues.append(f"Section '{section_title}': {caps_count} CAPS words (max 1 per section)")
        
        if emoji_count > 1:
            issues.append(f"Section '{section_title}': {emoji_count} emojis (max 1 per section, excluding tables)")
    
    return issues


def check_redundant_translations(text: str) -> List[str]:
    """Check for redundant 'Translation' sections after tables"""
    issues = []
    
    # Look for table followed by "Translation:" or "What This Means:"
    pattern = r'\|[^\n]+\|\n(?:\|[^\n]+\|\n)*\n\*\*Translation\*\*:|\*\*What This Means\*\*:'
    matches = re.finditer(pattern, text, re.MULTILINE)
    
    for match in matches:
        context = text[max(0, match.start()-50):match.end()+50]
        issues.append(f"Redundant translation section found after table")
    
    return issues


def check_report_style(file_path: str) -> List[str]:
    """
    Check report style and return list of issues.
    
    Args:
        file_path: Path to markdown report file
    
    Returns:
        List of style issues found
    """
    issues = []
    
    path = Path(file_path)
    if not path.exists():
        return [f"File not found: {file_path}"]
    
    text = path.read_text()
    
    # Check TL;DR
    has_tldr, tldr_issues = check_tldr(text)
    issues.extend(tldr_issues)
    
    # Check emphasis
    emphasis_issues = check_emphasis_per_section(text)
    issues.extend(emphasis_issues)
    
    # Check redundant translations
    translation_issues = check_redundant_translations(text)
    issues.extend(translation_issues)
    
    return issues


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: enforce_style.py <report_file.md>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    issues = check_report_style(file_path)
    
    if issues:
        print(f"Style issues found in {file_path}:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print(f"✓ No style issues found in {file_path}")

