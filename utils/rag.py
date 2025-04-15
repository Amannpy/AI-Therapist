import os
import json
from pathlib import Path

def get_therapy_resources(text, emotion, top_k=3):
    """
    Get relevant therapy resources based on emotion
    
    Args:
        text (str): User query text
        emotion (str): Detected emotion
        top_k (int): Number of resources to return
        
    Returns:
        list: List of relevant therapy resources
    """
    return fallback_resources(emotion)

def fallback_resources(emotion):
    """Return resources based on emotion"""
    # First try to load from therapy_documents.json if it exists
    try:
        therapy_docs_path = Path(__file__).parent.parent / "data" / "therapy_documents.json"
        
        if therapy_docs_path.exists():
            with open(therapy_docs_path, 'r') as f:
                all_docs = json.load(f)
                
            # Simple keyword matching for demo
            if emotion:
                emotion_docs = []
                for doc in all_docs:
                    if emotion.lower() in doc.get("title", "").lower() or emotion.lower() in doc.get("content", "").lower():
                        emotion_docs.append({
                            "title": doc.get("title", ""),
                            "summary": doc.get("summary", "")
                        })
                        if len(emotion_docs) >= 3:
                            break
                
                if emotion_docs:
                    return emotion_docs
    except Exception as e:
        print(f"Error loading therapy documents: {e}")
    
    # Fallback resources by emotion
    resources_by_emotion = {
        "anxious": [
            {
                "title": "Deep Breathing Exercise",
                "summary": "Breathe in slowly for 4 counts, hold for 2, exhale for 6. Repeat 5-10 times to activate the parasympathetic nervous system."
            },
            {
                "title": "Grounding Technique",
                "summary": "Use the 5-4-3-2-1 technique: identify 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, and 1 thing you taste."
            }
        ],
        "sad": [
            {
                "title": "Behavioral Activation",
                "summary": "Schedule small, achievable positive activities throughout your day, even when you don't feel motivated."
            },
            {
                "title": "Self-Compassion Practice",
                "summary": "Speak to yourself as you would to a good friend who is going through a difficult time."
            }
        ],
        "angry": [
            {
                "title": "Time-Out Strategy",
                "summary": "When feeling overwhelmed with anger, take a break for 10-20 minutes before responding."
            },
            {
                "title": "Cognitive Reframing",
                "summary": "Challenge thoughts like 'they always' or 'they never' with more balanced perspectives."
            }
        ],
        "depressed": [
            {
                "title": "Small Goals Approach",
                "summary": "Break tasks into the smallest possible steps and celebrate completing each one."
            },
            {
                "title": "Thought Record",
                "summary": "Write down negative thoughts, identify the cognitive distortion, and create a more balanced thought."
            }
        ],
        "stressed": [
            {
                "title": "Progressive Muscle Relaxation",
                "summary": "Tense and then release each muscle group from toes to head to reduce physical tension."
            },
            {
                "title": "Mindful Focus Exercise",
                "summary": "Focus completely on one simple task like washing dishes, bringing attention back whenever your mind wanders."
            }
        ],
        "fearful": [
            {
                "title": "Exposure Hierarchy",
                "summary": "Create a ladder of feared situations from least to most anxiety-provoking, and gradually expose yourself to each level."
            },
            {
                "title": "Worry Time",
                "summary": "Schedule 15-30 minutes daily to focus on worries, postponing worry thoughts outside of this time."
            }
        ]
    }
    
    # Return emotion-specific resources or general ones
    if emotion in resources_by_emotion:
        return resources_by_emotion[emotion]
    else:
        # Default resources for other emotions
        return [
            {
                "title": "Mindfulness Meditation",
                "summary": "Focus on your breath for 5 minutes, gently returning attention whenever your mind wanders."
            },
            {
                "title": "Gratitude Practice",
                "summary": "Write down three things you're grateful for each day to shift focus toward positive aspects of life."
            }
        ]
