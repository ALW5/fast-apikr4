import os
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from dotenv import load_dotenv

from database import engine, Base, get_db, Product as DBProduct
from models import User, ErrorResponse
from exceptions import CustomExceptionA, CustomExceptionB, ProductNotFoundException

load_dotenv()

# Создание таблиц
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Контрольная работа №4")

# =====================================================
# ЗАДАНИЕ 10.1: Пользовательская обработка ошибок
# =====================================================

@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": exc.error_code}
    )

@app.get("/trigger-a")
def trigger_exception_a(raise_error: bool = True):
    if raise_error:
        raise CustomExceptionA("Custom Exception A triggered")
    return {"message": "OK"}

@app.get("/trigger-b/{item_id}")
def trigger_exception_b(item_id: int):
    if item_id > 100:
        raise CustomExceptionB(f"Item {item_id} not found")
    return {"message": f"Item {item_id} found"}

# =====================================================
# ЗАДАНИЕ 10.2: Валидация данных запроса
# =====================================================

@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error_code": "VALIDATION_ERROR"}
    )

@app.post("/users/validate")
def validate_user(user: User):
    return {"message": f"User {user.username} is valid", "user": user.model_dump()}

# =====================================================
# ЗАДАНИЕ 9.1: CRUD для Product (с SQLAlchemy)
# =====================================================

# Pydantic модели для Product
from pydantic import BaseModel as PydanticBaseModel

class ProductCreate(PydanticBaseModel):
    title: str
    price: float
    count: int

class ProductResponse(PydanticBaseModel):
    id: int
    title: str
    price: float
    count: int
    description: str = ""  # Добавлено после миграции

class ProductUpdate(PydanticBaseModel):
    title: str | None = None
    price: float | None = None
    count: int | None = None
    description: str | None = None

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    db_product = DBProduct(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    return product

@app.get("/products", response_model=List[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return db.query(DBProduct).all()

@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_update: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    
    for key, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    
    db.commit()
    db.refresh(product)
    return product

@app.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(DBProduct).filter(DBProduct.id == product_id).first()
    if not product:
        raise ProductNotFoundException(product_id)
    db.delete(product)
    db.commit()
    return None

# =====================================================
# ЗАДАНИЕ 11.1: Простое приложение с тремя эндпоинтами
# =====================================================

from itertools import count
from threading import Lock
from pydantic import BaseModel

db_users: dict[int, dict] = {}
_user_id_seq = count(start=1)
_user_id_lock = Lock()

def next_user_id() -> int:
    with _user_id_lock:
        return next(_user_id_seq)

class UserIn(BaseModel):
    username: str
    age: int

class UserOut(BaseModel):
    id: int
    username: str
    age: int

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(user: UserIn):
    user_id = next_user_id()
    db_users[user_id] = user.model_dump()
    return {"id": user_id, **db_users[user_id]}

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    if user_id not in db_users:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user_id, **db_users[user_id]}

@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int):
    if db_users.pop(user_id, None) is None:
        raise HTTPException(status_code=404, detail="User not found")
    return None

# =====================================================
# Запуск
# =====================================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)