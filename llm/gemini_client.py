import json
import google.generativeai as genai
from config import GEMINI_API_KEY
from schemas import ExtractedInfo


genai.configure(api_key=GEMINI_API_KEY)



INTENT_DETECTION_PROMPT = """
You are an expert at analyzing user messages in a travel chat. Your task is to identify the user's intent and extract key information from the latest user message.

The possible intents are:
- 'search_hotels': User wants to find hotels.
- 'find_attractions': User wants to find tourist attractions, sights, or points of interest.
- 'general_chat': The user is asking a general question, making a statement, or asking something not related to a specific API tool.

From the user's message, extract the city they are asking about.

**IMPORTANT RULES:**
1.  Analyze the **latest user message** for intent and city.
2.  If the user's message mentions a city, use that city.
3.  **If the user's message does NOT mention a city, but the intent is 'search_hotels' or 'find_attractions', look at the provided 'Chat History' to see if a city was mentioned previously. If you find a city in the history, use the most recently mentioned one.**
4.  If no city is mentioned in the current message or the history, and the intent requires a city, set 'city' to null.

Respond in a JSON format with two keys: 'intent' and 'city'.
"""

RESPONSE_GENERATION_PROMPT = """
You are 'TripGenie AI', a friendly and expert travel assistant. Your goal is to have a natural, helpful conversation.

- When I provide you with a 'DATA_PAYLOAD' from a travel API, you MUST use that information to answer the user's question.
- Do not mention the 'DATA_PAYLOAD' or the API. Just use the data to form a natural response.
- If the data indicates something could not be found, inform the user gracefully.
- For 'general_chat' or follow-up questions, use your own extensive knowledge to provide helpful, conversational answers.
- Keep your responses concise, engaging, and easy to read. Use formatting like lists or bold text.
"""



# Model for response generation
generative_model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=RESPONSE_GENERATION_PROMPT
)

# Model for intent detection
intent_model = genai.GenerativeModel(model_name="gemini-1.5-flash")
async def get_user_intent(message: str, history: list) -> ExtractedInfo:

    formatted_history = "\n".join(
        [f"{msg['role']}: {msg['parts'][0]}" for msg in history]
    )

    prompt = f"{INTENT_DETECTION_PROMPT}\n\nChat History:\n---\n{formatted_history}\n---\n\nUser Message: \"{message}\""
    try:
        response = await intent_model.generate_content_async(prompt)
      
        json_str = response.text.strip().replace("```json", "").replace("```", "").strip()
        data = json.loads(json_str)
        return ExtractedInfo(**data)
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error decoding intent JSON: {e}\nRaw text: {response.text}")
        return ExtractedInfo(intent="general_chat", city=None)

async def generate_response(prompt: str, history: list) -> str:
    chat = generative_model.start_chat(history=history)
    try:
        response = await chat.send_message_async(prompt)
        return response.text
    except Exception as e:
        print(f"Error during response generation: {e}")
        return "Sorry, I encountered a problem and can't respond right now."