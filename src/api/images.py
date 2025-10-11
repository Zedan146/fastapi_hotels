from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.exceptions import UnavailableFileFormatException, UnavailableFileFormatHTTPException
from src.services.images import ImagesService

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("", summary="Добавить фотографию")
def upload_image(file: UploadFile, backgrounds_tasks: BackgroundTasks):
    try:
        ImagesService().upload_image(file, backgrounds_tasks)
    except UnavailableFileFormatException as ex:
        print(ex)
        raise UnavailableFileFormatHTTPException(detail=f"{ex}") from ex

    return {"status": "OK"}
