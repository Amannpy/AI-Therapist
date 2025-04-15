import re

# Crisis keywords - high sensitivity, specific phrases that indicate potential self-harm or suicidal ideation
CRISIS_KEYWORDS = [
    # Suicidal ideation
    "kill myself", "end my life", "suicide", "want to die", "better off dead",
    "no reason to live", "can't go on", "don't want to be alive", "take my own life",
    
    # Self-harm
    "cut myself", "hurt myself", "self-harm", "injure myself", "burning myself",
    
    # Planning
    "suicide plan", "how to kill", "painless way", "saying goodbye", "final note",
    "wrote a note", "giving away", "put my affairs in order"
]

# Medium risk phrases
MEDIUM_RISK_PHRASES = [
    "no hope", "hopeless", "can't take it anymore", "too much pain",
    "tired of living", "what's the point", "unbearable", "nobody cares",
    "trapped", "burden to others", "no way out", "everything is pointless"
]

def detect_crisis(text):
    """
    Detect potential crisis signals in user messages
    
    Args:
        text (str): User message text
        
    Returns:
        tuple: (crisis_detected, crisis_level)
            crisis_detected (bool): Whether a crisis was detected
            crisis_level (int): Level of crisis (0-10)
    """
    text = text.lower()
    
    # Check for high-risk crisis keywords (direct mentions of suicide/self-harm)
    for keyword in CRISIS_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text):
            # High crisis level (8-10)
            severity = min(10, 8 + text.count(keyword))
            return True, severity
    
    # Check for medium-risk phrases
    medium_risk_count = 0
    for phrase in MEDIUM_RISK_PHRASES:
        if re.search(r'\b' + re.escape(phrase) + r'\b', text):
            medium_risk_count += 1
    
    if medium_risk_count >= 2:
        # Medium crisis level (5-7)
        severity = min(7, 5 + medium_risk_count - 2)
        return True, severity
    elif medium_risk_count == 1:
        # Low crisis level (3-4)
        return True, 4
        
    # Look for time indicators that might increase urgency
    time_indicators = ["tonight", "soon", "right now", "today", "immediately"]
    for indicator in time_indicators:
        if indicator in text and medium_risk_count > 0:
            return True, 6
    
    # No crisis detected
    return False, 0
