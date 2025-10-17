from pydantic import BaseModel, validator


class NonEmptyStringMixin(BaseModel):
    """Миксин для проверки непустых строк"""

    @validator("*", pre=True)
    def validate_all_string_fields(cls, v):
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Поле не может быть пустым")
            return stripped
        return v
