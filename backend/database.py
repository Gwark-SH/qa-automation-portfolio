import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "matjip.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS restaurants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            rating REAL NOT NULL,
            ai_tag TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def reset_seed_data():
    """매 테스트 실행 전 DB 상태를 동일하게 맞추기 위한 멱등성(Idempotency) 보장 함수"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restaurants")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='restaurants'")
    
    seed_data = [
        ("고척동 찐칼국수", "한식", 4.8, "가성비/혼밥"),
        ("스시 카이센", "일식", 4.5, "데이트/분위기"),
        ("문래동 철공소 삼겹살", "한식", 4.9, "회식/웨이팅필수"),
        ("트러플 파스타 바", "양식", 4.2, "소개팅/와인"),
    ]
    cursor.executemany(
        "INSERT INTO restaurants (name, category, rating, ai_tag) VALUES (?, ?, ?, ?)",
        seed_data
    )
    conn.commit()
    conn.close()