from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.core.database import get_connection
from app.api.deps import get_current_admin_id
from app.services.image_services import save_image_file, delete_image_file
from app.repositories import image_repo
from app.schemas.image import ImageOut, ImageReorderRequest
import asyncpg


router = APIRouter()



@router.post("/products/{product_id}/images", response_model=ImageOut)
async def upload_image(
    product_id: int,
    file: UploadFile = File(...),
    admin_id: int = Depends(get_current_admin_id),
    conn: asyncpg.Connection = Depends(get_connection)

):
    if admin_id:
        path = await save_image_file(file)
        existing = await image_repo.list_images(conn, product_id)
        image = await image_repo.add_image(conn, product_id, path, position=len(existing))
        return ImageOut(**image)


@router.get("/products/{product_id}/images", response_model=list[ImageOut])
async def get_product_images(product_id: int, conn: asyncpg.Connection = Depends(get_connection)):
    images = await image_repo.list_images(conn, product_id)
    return [ImageOut(**img) for img in images]


@router.put("/products/{product_id}/images/reorder")
async def reorder_product_images(
    product_id: int,
    payload: ImageReorderRequest,
    admin_id: int = Depends(get_current_admin_id),
    conn=Depends(get_connection),
):
    if admin_id:
        updated = await image_repo.reorder_images(conn, product_id, payload.ordered_ids)
        return updated



 
@router.put("/images/{image_id}/replace", response_model=ImageOut)
async def replace_product_image(
    image_id: int,
    file: UploadFile = File(...),
    admin_id: int = Depends(get_current_admin_id),
    conn=Depends(get_connection),

  
    ):
        if admin_id:
            existing = await image_repo.get_image_by_id(conn, image_id)
            if not existing:
                raise HTTPException(status_code=404, detail="Изображение не найдено")
        
            new_path = await save_image_file(file)          # сохраняем новый файл на диск
            updated = await image_repo.replace_image_file_path(conn, image_id, new_path)
        
            delete_image_file(existing["path"])              # удаляем старый файл С ДИСКА (после успешного обновления БД)
        
            return ImageOut(**updated)

@router.delete("/images/{image_id}")
async def remove_image(
    image_id: int,
    admin_id:int = Depends(get_current_admin_id),
    conn: asyncpg.Connection = Depends(get_connection)
):  
    if admin_id:
       
        image = await image_repo.get_image(conn, image_id)
        if not image:
            raise HTTPException(status_code=404, detail="Изображение не найдено")
      
        await image_repo.delete_image(conn, image["id"])
        delete_image_file(image["path"])

        return {"message": "Изображение удалено"}