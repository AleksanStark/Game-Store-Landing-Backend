from pydantic import BaseModel
from datetime import datetime

class ImageOut(BaseModel):
    id: int
    product_id: int
    path: str
    position: int
    created_at: datetime


class ImageReorderRequest(BaseModel):
    ordered_ids: list[int]  # порядок сверху вниз, ПОСЛЕДНИЙ id в списке = обложка
 
 