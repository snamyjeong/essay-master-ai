import os
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv('backend/.env')
api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ 에러: API 키를 찾을 수 없습니다. .env 파일을 확인해주세요.")
else:
    genai.configure(api_key=api_key.strip())
    print(f"--- [Jarvis V3] 사용 가능한 임베딩 모델 리스트 ---")
    try:
        for m in genai.list_models():
            if 'embedContent' in m.supported_generation_methods:
                print(f"✅ 모델명: {m.name}")
    except Exception as e:
        print(f"❌ API 호출 중 오류 발생: {e}")
