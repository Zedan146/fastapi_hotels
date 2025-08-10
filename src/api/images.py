import shutil

from fastapi import APIRouter, UploadFile, BackgroundTasks

from src.tasks.tasks import resize_image

router = APIRouter(prefix="/images", tags=["Изображения"])


@router.post("", summary="Добавить фотографию")
def upload_image(file: UploadFile, backgrounds_tasks: BackgroundTasks):
    image_path = f"src/static/images/{file.filename}"
    with open(image_path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

        # resize_image.delay(image_path)
        backgrounds_tasks.add_task(resize_image, image_path)
