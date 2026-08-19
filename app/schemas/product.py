from pydantic import BaseModel
from typing import Literal

class ProductCreate(BaseModel):
    name: str
    price: int
    category_id: int
    condition: Literal["new", "used"]


class ProductUpdate(BaseModel):
    name: str | None = None
    price: int | None  = None
    category_id: int | None = None
    condition: Literal["new", "used"] | None = None