from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.services.images import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("", summary="Добавить фотографию")
def upload_image(file: UploadFile, backgrounds_tasks: BackgroundTasks):
    ImagesService().upload_image(file, backgrounds_tasks)
