from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import numpy as np
from models import predict_career
from config import GEMINI_API_KEY

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro")

# Store user session data (temporary memory)
user_sessions = {}

# Predefined 10 skill-related questions
skill_questions = [
    "Do you enjoy solving complex mathematical problems? (yes/no)",
    "Do you have experience in programming or coding? (yes/no)",
    "Are you interested in working with data and statistics? (yes/no)",
    "Do you prefer creative fields like design and animation? (yes/no)",
    "Do you enjoy working with hardware and electronic circuits? (yes/no)",
    "Are you comfortable explaining complex ideas to others? (yes/no)",
    "Do you like researching and analyzing large sets of information? (yes/no)",
    "Are you skilled in using tools like Excel, SQL, or Tableau? (yes/no)",
    "Do you enjoy writing and content creation? (yes/no)",
    "Are you more interested in building software applications? (yes/no)"
]

class ChatInput(BaseModel):
    user_id: str  # A unique user identifier
    user_message: str  # User response

# Start the conversation or continue tracking responses
@app.post("/chat")
async def chat_with_gemini(chat_input: ChatInput):
    user_id = chat_input.user_id
    user_message = chat_input.user_message.lower().strip()

    # Start a new session if user is new
    if user_id not in user_sessions:
        user_sessions[user_id] = {"responses": [], "current_question": 0}

    session = user_sessions[user_id]

    # If user has not answered all questions, ask the next one
    if session["current_question"] < len(skill_questions):
        session["responses"].append(user_message)
        session["current_question"] += 1

        # If all 10 questions are answered, process the responses
        if session["current_question"] == len(skill_questions):
            # Convert responses to a binary skill matrix
            skill_matrix = np.array([[1 if response in ["yes", "y"] else 0 for response in session["responses"]]])
            
            # Ensure only the first 7 responses are passed to match model input shape
            skill_matrix = skill_matrix[:, :7]

            # Predict career
            career = predict_career(skill_matrix)

            # Use Gemini API to provide a natural explanation
            prompt = f"Based on the user's responses, they are best suited for {career}. Provide a brief and motivational explanation."
            gemini_response = model.generate_content(prompt)
            gemini_text = gemini_response.text if gemini_response else "I couldn't generate an explanation."

            # Clear session after prediction
            del user_sessions[user_id]

            return {
                "reply": f"Based on your responses, the best career match is: {career}\n\n{gemini_text}",
                "career": career
            }
        else:
            return {"reply": skill_questions[session["current_question"]]}  # Ask the next question

    return {"reply": "Error: Unexpected conversation flow. Try again."}
