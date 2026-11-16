from fastapi import FastAPI, Query, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from contextlib import asynccontextmanager

from backend.database import init_db, reset_seed_data, get_db_connection
from backend.schemas import RestaurantCreate, RestaurantResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    reset_seed_data()
    yield

app = FastAPI(title="Matjip 3-Tier API Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 로그인 요청 스키마
class LoginRequest(BaseModel):
    username: str
    password: str

# [신규] 1. 로그인 API (성공 시 가짜 액세스 토큰 발급)
@app.post("/api/login")
def login(req: LoginRequest):
    if req.username == "qa_admin" and req.password == "pass1234":
        return {"access_token": "secret-qa-token-2026", "username": req.username}
    raise HTTPException(status_code=401, detail="아이디 또는 비밀번호가 올바르지 않습니다.")

@app.get("/api/restaurants", response_model=List[RestaurantResponse])
def get_restaurants(category: Optional[str] = Query(None), keyword: Optional[str] = Query(None)):
    conn = get_db_connection()
    query = "SELECT * FROM restaurants WHERE 1=1"
    params = []

    if category and category != "전체":
        query += " AND category = ?"
        params.append(category)
    if keyword:
        query += " AND (LOWER(name) LIKE ? OR LOWER(ai_tag) LIKE ?)"
        kw = f"%{keyword.lower()}%"
        params.extend([kw, kw])

    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# [업그레이드] 2. 맛집 등록 API (Authorization 토큰 검증 추가)
@app.post("/api/restaurants", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(item: RestaurantCreate, authorization: Optional[str] = Header(None)):
    if authorization != "Bearer secret-qa-token-2026":
        raise HTTPException(status_code=401, detail="로그인이 필요한 기능입니다.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO restaurants (name, category, rating, ai_tag) VALUES (?, ?, ?, ?)",
        (item.name, item.category, item.rating, item.ai_tag)
    )
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {**item.model_dump(), "id": new_id}

# [신규] 3. 맛집 삭제 API (Authorization 토큰 검증 포함)
@app.delete("/api/restaurants/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(restaurant_id: int, authorization: Optional[str] = Header(None)):
    if authorization != "Bearer secret-qa-token-2026":
        raise HTTPException(status_code=401, detail="삭제 권한이 없습니다.")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM restaurants WHERE id = ?", (restaurant_id,))
    conn.commit()
    conn.close()
    return

@app.post("/api/test/reset", status_code=status.HTTP_200_OK)
def reset_db_for_test():
    reset_seed_data()
    return {"message": "Database reset to initial seed state."}