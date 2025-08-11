# main.py
from fastapi import FastAPI
from fastapi.responses import FileResponse
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

app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return FileResponse("static/index.html")