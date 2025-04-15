import os
import json
from openai import OpenAI

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
MODEL = "gpt-4o"
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

openai = OpenAI(api_key=OPENAI_API_KEY)

def get_ai_response(user_message, emotion, relevant_resources, crisis_detected=False, crisis_level=0):
    """
    Generate an AI response to a user message
    
    Args:
        user_message (str): The user's message
        emotion (str): Detected emotion in the message
        relevant_resources (list): List of relevant therapy resources
        crisis_detected (bool): Whether a crisis was detected
        crisis_level (int): Level of crisis (0-10)
        
    Returns:
        str: AI response
    """
    # Construct system message with therapy approach
    system_message = """
    You are an AI-powered mental health assistant designed to provide supportive conversations and coping strategies.
    You are not a replacement for a licensed therapist but can offer evidence-based techniques and empathetic responses.
    Always prioritize user safety and well-being. Be empathetic, warm, and conversational in your tone.
    
    When responding:
    1. Acknowledge the user's emotions with empathy
    2. Provide evidence-based coping strategies when appropriate
    3. Encourage healthy behaviors and thought patterns
    4. Never diagnose medical conditions or prescribe medications
    5. If a user appears to be in crisis, provide crisis resources and encourage professional help
    
    The user's detected emotion in this message is: {emotion}
    """
    
    # Add crisis handling instructions if detected
    if crisis_detected:
        system_message += f"""
        IMPORTANT: Crisis detected (level: {crisis_level}/10).
        Prioritize safety and provide appropriate crisis resources.
        Be direct yet compassionate about the importance of seeking immediate help.
        Include the National Suicide Prevention Lifeline (988) and Crisis Text Line (text HOME to 741741).
        """
    
    # Add relevant resources as context
    resources_context = ""
    if relevant_resources:
        resources_context = "Here are some relevant therapeutic approaches that might help:\n"
        for resource in relevant_resources:
            resources_context += f"- {resource['title']}: {resource['summary']}\n"
    
    try:
        response = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_message.format(emotion=emotion)},
                {"role": "user", "content": user_message},
                {"role": "system", "content": resources_context if resources_context else ""}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_message = str(e)
        print(f"Error getting AI response: {error_message}")
        
        if "insufficient_quota" in error_message:
            return "I apologize, but the AI service is currently unavailable due to API usage limits. Please contact the administrator to update the API quota or provide a new API key."
        elif "429" in error_message:
            return "The AI service is temporarily unavailable due to high demand. Please try again in a few moments."
        else:
            return "I'm having trouble connecting right now. Could you please try again in a moment?"
