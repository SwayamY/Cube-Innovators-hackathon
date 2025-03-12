import google.generativeai as genai
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

models = genai.list_models()

for model in models:
    print(model.name)
