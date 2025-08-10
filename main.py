# main.py
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from api.chat import router as chat_router

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)



# Include the chat router
app.include_router(chat_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "Travel Chatbot API is running. Go to /docs for the API explorer."}