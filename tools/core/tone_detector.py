#!/usr/bin/env python3
"""
Tone Detector for Little Padawan Reports

Analyzes session context and returns appropriate tone for report generation.
Prevents repetitive cheerleading by varying personality based on context.

Usage:
    from tools.core.tone_detector import detect_tone
    
    tone = detect_tone(
        has_pb=True,
        has_excuses=False,
        repeated_mistakes=False,
        following_advice=True,
        last_tone='excited'
    )
"""

import random
from typing import Optional, Literal

Tone = Literal['excited', 'sassy', 'grumpy', 'deadpan', 'proud', 'matter_of_fact']


def detect_tone(
    has_pb: bool = False,
    has_excuses: bool = False,
    repeated_mistakes: bool = False,
    following_advice: bool = False,
    obvious_result: bool = False,
    last_tone: Optional[Tone] = None,
    random_variance: bool = False
) -> Tone:
    """
    Detect appropriate tone based on session context.
    
    Args:
        has_pb: Did Master Lonn set a personal best?
        has_excuses: Did Master Lonn make excuses or downplay success?
        repeated_mistakes: Did Master Lonn repeat the same mistake?
        following_advice: Did Master Lonn follow previous advice?
        obvious_result: Is this an obvious/expected result?
        last_tone: Last tone used (to avoid repetition)
        random_variance: 10% chance of "bad hair day" (grumpy for no reason)
    
    Returns:
        Appropriate tone for the session
    """
    
    # 10% random variance - bad hair day
    if random_variance and random.random() < 0.1:
        return 'grumpy'
    
    # Context-based detection
    if has_excuses:
        return 'sassy'
    
    if repeated_mistakes:
        return 'grumpy'
    
    if following_advice:
        return 'proud'
    
    if obvious_result:
        return 'deadpan'
    
    if has_pb:
        # Rotate between excited and deadpan for PBs
        if last_tone == 'excited':
            return 'deadpan'
        elif last_tone == 'deadpan':
            return 'excited'
        else:
            # First PB or alternating - pick randomly
            return random.choice(['excited', 'deadpan'])
    
    # Default: matter-of-fact for neutral sessions
    return 'matter_of_fact'


def get_tone_characteristics(tone: Tone) -> dict:
    """
    Get characteristics for a given tone.
    
    Returns:
        Dictionary with tone characteristics:
        - opening: List of opening phrases
        - emphasis: Emphasis level ('moderate', 'minimal', 'none', 'subtle')
        - closing: List of closing phrases
    """
    
    tones = {
        'excited': {
            'opening': ['New PB!', "There it is.", "That's the stuff."],
            'emphasis': 'moderate',  # Some caps, one emoji
            'closing': ['Now do it again.', 'Keep going.']
        },
        'sassy': {
            'opening': ['Oh look,', 'Interesting.', 'Well well well.'],
            'emphasis': 'minimal',  # Italics, no caps
            'closing': ['Cool cool cool.', 'Totally normal.', 'Sure.']
        },
        'grumpy': {
            'opening': ['Fine.', 'Okay.', 'Right.'],
            'emphasis': 'minimal',  # Period-heavy, short sentences
            'closing': ["We've talked about this.", 'Please.', 'Try again.']
        },
        'deadpan': {
            'opening': ['1:28.572.', 'New PB.', 'Faster.'],
            'emphasis': 'none',  # No formatting, just facts
            'closing': ['Moving on.', 'Next.', "That'll do."]
        },
        'proud': {
            'opening': ['You listened.', 'There you go.', 'Good.'],
            'emphasis': 'subtle',  # Italics for warmth
            'closing': ['This is how you learn.', 'Keep it up.', 'Proud of you.']
        },
        'matter_of_fact': {
            'opening': ['Alright,', 'Let\'s see,', 'Session data:'],
            'emphasis': 'minimal',
            'closing': ['Work to do.', 'Next session.', 'Moving forward.']
        }
    }
    
    return tones.get(tone, tones['matter_of_fact'])


if __name__ == '__main__':
    # Test examples
    print("PB achieved, last tone was excited:")
    print(detect_tone(has_pb=True, last_tone='excited'))
    
    print("\nMaster Lonn makes excuses:")
    print(detect_tone(has_excuses=True))
    
    print("\nRepeated mistakes:")
    print(detect_tone(repeated_mistakes=True))
    
    print("\nFollowing advice:")
    print(detect_tone(following_advice=True))
    
    print("\nObvious result:")
    print(detect_tone(obvious_result=True))

