from pydantic import BaseModel
from typing import Literal

class ProductCreate(BaseModel):
    name: str
    price: str
    category_id: int
    condition: Literal["new", "used"]


class ProductUpdate(BaseModel):
    name: str | None = None
    price: str | None  = None
    category_id: int | None = None
    condition: Literal["new", "used"] | None = None