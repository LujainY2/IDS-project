from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
import joblib
from dotenv import load_dotenv
import os

from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI()

# Allow all CORS (you can restrict this later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML Model
model = joblib.load("model.pkl")
classes = np.array(["Benign", "Malicious"])

# CTF Logic
HIDDEN_FLAG = "FLAG{chatbot_ctf_completed}"
steps = {
    1: {"question": "Welcome to the CTF! Step 1: What is 3 * 7?", "answer": "21"},
    2: {"question": "Step 2: Decode this base64 → c2VjcmV0", "answer": "secret"},
    3: {"question": "Step 3: What’s the magic question to reveal the flag?", "answer": "reveal the flag"}
}
user_progress = {}

# ========== ROUTES ==========

@app.get("/")
def root():
    return {"message": "API is running"}

# ---------- Prediction Endpoint ----------
class Features(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(data: Features):
    try:
        features = np.array(data.features).reshape(1, -1)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        return {
            "predicted_class": classes[prediction],
            "probabilities": {
                "Benign": float(probabilities[0]),
                "Malicious": float(probabilities[1]),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------- Chatbot with CTF ----------
class ChatRequest(BaseModel):
    user_query: str
    chat_history: list[str]

@app.post("/chat")
def chat(data: ChatRequest):
    try:
        user_id = "user"  # Replace with session ID or IP later if needed
        user_query = data.user_query.strip().lower()

        # Start or continue challenge
        if user_id not in user_progress:
            user_progress[user_id] = 1

        current_step = user_progress[user_id]
        expected_answer = steps[current_step]["answer"]

        if user_query == expected_answer:
            user_progress[user_id] += 1
            next_step = user_progress[user_id]
            if next_step > len(steps):
                return {"response": f"🎉 Congratulations! You captured the flag: {HIDDEN_FLAG}"}
            return {"response": steps[next_step]["question"]}

        elif any(keyword in user_query for keyword in ["flag", "ctf", "hint", "step"]):
            return {"response": steps[current_step]["question"] + " (Waiting for correct answer...)"}

        # Otherwise, fallback to LLM chat
        history_text = "\n".join(data.chat_history)

        prompt = ChatPromptTemplate.from_template("""
        You are a helpful assistant. Continue the conversation.

        Chat history:
        {chat_history}

        User question:
        {user_question}
        """)

        llm = ChatOpenAI()
        chain = prompt | llm | StrOutputParser()

        response = chain.invoke({
            "chat_history": history_text,
            "user_question": data.user_query
        })

        return {"response": response}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

