# backend/check_type.py 라는 파일로 잠시 저장해서 실행해 보세요.
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.app.db.session import engine, SessionLocal
print(f"DEBUG: engine type is {type(engine)}")
print(f"DEBUG: SessionLocal type is {type(SessionLocal)}")