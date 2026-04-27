from pydantic import BaseModel, EmailStr, conint, constr, Field
from typing import Optional

# Задание 10.2 - модель User с валидацией
class User(BaseModel):
    username: str
    age: conint(gt=18)  # age must be greater than 18
    email: EmailStr
    password: constr(min_length=8, max_length=16)
    phone: Optional[str] = 'Unknown'

# Модели для ответов с ошибками (задание 10.1)
class ErrorResponse(BaseModel):
    detail: str
    error_code: str
    status_code: int