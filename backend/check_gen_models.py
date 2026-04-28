import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv('backend/.env')
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ API 키가 없습니다.")
else:
    genai.configure(api_key=api_key.strip())
    print("--- [Jarvis V3] 가용 생성 모델 리스트 ---")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ 모델명: {m.name}")
