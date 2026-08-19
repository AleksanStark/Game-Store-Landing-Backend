import aiofiles
from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = Path("uploads/products")
ALLOWED_TYPES = {"image/jpeg", "image/jpg", "image/png", "image/webp"}
MAX_SIZE = 5 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)



async def save_image_file(file: UploadFile) -> str:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Разрешены только JPEG, JPG, PNG, WEBP")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="Файл болььше 5 МБ")

    ext = Path(file.filename).suffix.lower()
    filename = f"{uuid4()}{ext}"
    disk_path = UPLOAD_DIR / filename

    async with aiofiles.open(disk_path, "wb") as f:
        await f.write(contents)
    return f"/uploads/products/{filename}"


def delete_image_file(relative_path: str) -> None:
    disk_path = Path(relative_path.lstrip("/"))
    if disk_path.exists():
        disk_path.unlink()