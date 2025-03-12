import tensorflow as tf
import numpy as np
import os
import google.generativeai as genai
from data import training_data
from config import GEMINI_API_KEY

# Initialize Gemini API
genai.configure(api_key=GEMINI_API_KEY)

MODEL_PATH = "backend/career_model.keras"

# Convert data to tensors
xs = tf.constant([d["input"] for d in training_data], dtype=tf.float32)
ys = tf.constant([d["output"] for d in training_data], dtype=tf.float32)

# Function to build model
def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(10, activation="relu", input_shape=(7,)),  # Input shape fixed to 7
        tf.keras.layers.Dense(3, activation="softmax")  # 3 output classes
    ])
    model.compile(optimizer="adam", loss="categorical_crossentropy")
    return model

# Load existing model or train a new one
if os.path.exists(MODEL_PATH):
    model = tf.keras.models.load_model(MODEL_PATH)
    print("✅ Loaded existing AI model.")
else:
    model = create_model()
    model.fit(xs, ys, epochs=500, verbose=0)
    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    model.save(MODEL_PATH)
    print("✅ AI Model Trained & Saved Successfully!")

# Career labels matching the model's 3-class output
career_labels = ["Web Development", "Data Science", "Cybersecurity"]

# Function to Predict Career using Gemini (fallback)
def predict_career_gemini(user_input):
    prompt = (
        f"Based on the following skill levels (0-1 scale): {user_input}, "
        "which career is the best fit among Web Development, Data Science, and Cybersecurity?"
    )
    response = genai.generate_text(prompt)
    return response.text.strip() if response.text else "Unknown"

# Function to Predict Career (TensorFlow first, fallback to Gemini)
def predict_career(user_input):
    try:
        skill_matrix = np.array(user_input).reshape(1, 7)  # Ensure input shape is (1,7)
        prediction = model.predict(skill_matrix, verbose=0)
        career_index = np.argmax(prediction)
        return career_labels[career_index]
    except Exception as e:
        print(f"⚠️ TensorFlow model error: {e}, using Gemini instead.")
        return predict_career_gemini(user_input)
