import os

# Emotion categories
EMOTIONS = [
    "angry", "anxious", "depressed", "fearful", "happy", 
    "sad", "stressed", "calm", "hopeful", "neutral"
]

# Using simple keyword-based emotion detection
def detect_emotion(text):
    """
    Simple keyword-based emotion detection
    
    Args:
        text (str): The text to analyze
        
    Returns:
        str: Detected emotion
    """
    text = text.lower()
    
    emotion_keywords = {
        "angry": ["angry", "anger", "mad", "furious", "rage", "hate", "frustrated"],
        "anxious": ["anxious", "anxiety", "worry", "worried", "nervous", "uneasy", "panic"],
        "depressed": ["depressed", "depression", "hopeless", "worthless", "empty", "numb"],
        "fearful": ["afraid", "scared", "terrified", "fear", "frightened", "terror"],
        "happy": ["happy", "joy", "glad", "pleased", "delighted", "excited", "grateful"],
        "sad": ["sad", "unhappy", "miserable", "down", "blue", "upset", "heartbroken"],
        "stressed": ["stressed", "overwhelmed", "pressure", "burden", "overloaded"],
        "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "composed"],
        "hopeful": ["hopeful", "optimistic", "looking forward", "positive", "better"]
    }
    
    emotion_counts = {emotion: 0 for emotion in emotion_keywords}
    
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in text:
                emotion_counts[emotion] += 1
    
    # Find emotion with most keyword matches
    max_count = max(emotion_counts.values())
    if max_count > 0:
        max_emotions = [e for e, c in emotion_counts.items() if c == max_count]
        return max_emotions[0]  # Return first if multiple have same count
    
    # Default if no keywords found
    return "neutral"
