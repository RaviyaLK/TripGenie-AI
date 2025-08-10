from fastapi import APIRouter, HTTPException
from schemas import ChatRequest, ChatResponse, ChatPart
from llm.gemini_client import get_user_intent, generate_response
from services.amadeus_client import amadeus_client

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_handler(request: ChatRequest):
    user_message = request.message
    
    # Reformat history for the Gemini API
    gemini_history = [
        {"role": msg.role, "parts": [part.text for part in msg.parts]}
        for msg in request.history
    ]

    # 1. Get user intent from question including history
    extracted_info = await get_user_intent(user_message, gemini_history)
    intent = extracted_info.intent
    city = extracted_info.city
    
    print(f"Detected Intent: {intent}, City: {city}")

    data_payload = None
    
    # 2. If intent requires an API call, execute it
    if city:
        city_code = await amadeus_client.get_city_code(city)
        if not city_code:
            data_payload = f"I couldn't find a major city named '{city}'. Could you be more specific?"
        else:
            if intent == "search_hotels":
                data_payload = await amadeus_client.find_hotels(city_code)
            elif intent == "find_attractions":
                lat,lon = await amadeus_client.get_city_coordinates(city)
                data_payload = await amadeus_client.find_points_of_interest(lat,lon)

    # 3. Construct final prompt for response generation
    final_prompt = user_message
    if data_payload:
        final_prompt = f"DATA_PAYLOAD:\n---\n{data_payload}\n---\n\nUser Question: {user_message}"
        print(f"--- Sending prompt with data to LLM ---\n{final_prompt}\n---------------------------------------")

    # 4. Generate the final conversational response
    try:
        response_text = await generate_response(final_prompt, gemini_history)
        return ChatResponse(role="model", parts=[ChatPart(text=response_text)])
    except Exception as e:
        print(f"Error in chat handler: {e}")
        raise HTTPException(status_code=500, detail="Failed to get a response from the AI model.")