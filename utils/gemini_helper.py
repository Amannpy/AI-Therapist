import os
import google.generativeai as genai

# Set up the Gemini API
GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
MODEL = "gemini-1.5-pro"

# Configure the Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def get_ai_response(user_message, emotion, relevant_resources, crisis_detected=False, crisis_level=0):
    """
    Generate an AI response to a user message using Gemini
    
    Args:
        user_message (str): The user's message
        emotion (str): Detected emotion in the message
        relevant_resources (list): List of relevant therapy resources
        crisis_detected (bool): Whether a crisis was detected
        crisis_level (int): Level of crisis (0-10)
        
    Returns:
        str: AI response
    """
    # Construct system prompt with therapy approach
    system_prompt = """
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
        system_prompt += f"""
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
    
    # Combine all context
    full_prompt = system_prompt.format(emotion=emotion) + "\n\n" + resources_context + "\n\nUser message: " + user_message
    
    try:
        if not GEMINI_API_KEY:
            raise ValueError("Missing Gemini API key")
            
        # Create a generative model instance
        model = genai.GenerativeModel(MODEL)
        
        # Generate response
        response = model.generate_content(full_prompt)
        
        return response.text.strip()
    except Exception as e:
        error_message = str(e)
        print(f"Error getting AI response from Gemini: {error_message}")
        
        if "API key not available" in error_message or "Missing Gemini API key" in error_message:
            return "I apologize, but I need a Google AI API key to function properly. Please ask the administrator to provide a valid Gemini API key."
        elif "quota" in error_message.lower():
            return "I apologize, but the AI service is currently unavailable due to API usage limits. Please contact the administrator to update the API quota."
        elif "429" in error_message:
            return "The AI service is temporarily unavailable due to high demand. Please try again in a few moments."
        else:
            # Provide a meaningful fallback response based on the detected emotion
            if emotion in ["sad", "depressed", "down"]:
                return "I notice you might be feeling down. While we're experiencing some technical difficulties, remember that it's okay to reach out to friends, family, or professional support when needed. Deep breathing exercises and gentle physical activity can sometimes help lift your mood."
            elif emotion in ["anxious", "worried", "stressed"]:
                return "I sense you might be feeling anxious. While our systems are currently experiencing technical issues, a quick grounding exercise might help: try naming 5 things you can see, 4 things you can touch, 3 things you can hear, 2 things you can smell, and 1 thing you can taste."
            elif emotion in ["angry", "frustrated", "upset"]:
                return "I can understand feeling frustrated, especially when technology isn't working as expected. Taking a short break, some deep breaths, or a brief walk might help provide some perspective."
            else:
                return "I apologize for the technical difficulties we're experiencing. While I work to resolve this issue, is there something specific you'd like to discuss or any particular coping strategies you've found helpful in the past?"