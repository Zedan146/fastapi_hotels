import shutil

from fastapi import UploadFile, BackgroundTasks

from src.exceptions import UnavailableFileFormatException
from src.services.base import BaseService
from src.tasks.tasks import resize_image


class ImagesService(BaseService):
    ALLOWED_IMAGE_TYPES = {"jpeg", "jpg", "png", "webp"}

    def upload_image(self, file: UploadFile, backgrounds_tasks: BackgroundTasks):
        file_extension = file.filename.split(".")[-1].lower()
        if file_extension not in self.ALLOWED_IMAGE_TYPES:
            raise UnavailableFileFormatException(
                detail=f".{file_extension} недопустимый формат файла. Разрешены: {', '.join(self.ALLOWED_IMAGE_TYPES)}"
            )

        image_path = f"src/static/images/{file.filename}"
        with open(image_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)

            # resize_image.delay(image_path)
            backgrounds_tasks.add_task(resize_image, image_path)
