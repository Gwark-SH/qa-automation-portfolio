from pydantic import BaseModel, Field

class RestaurantCreate(BaseModel):
    name: str = Field(..., min_length=1, description="식당 이름")
    category: str = Field(..., pattern="^(한식|일식|양식|중식)$")
    rating: float = Field(..., ge=0.0, le=5.0)
    ai_tag: str = Field(..., min_length=1)

class RestaurantResponse(RestaurantCreate):
    id: int