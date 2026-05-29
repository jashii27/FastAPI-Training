from fastapi import (
FastAPI,
HTTPException,
Depends,
BackgroundTasks,
Query
)

from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import (
OAuth2PasswordBearer,
OAuth2PasswordRequestForm
)

from sqlalchemy import (
create_engine,
Column,
Integer,
String,
Float,
Boolean
)

from sqlalchemy.orm import (
sessionmaker,
declarative_base,
Session
)

from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timedelta
import time

# APP INITIALIZATION

app = FastAPI(
title="Inventory API",
version="1.0.0"
)

# =========================

# CORS MIDDLEWARE

# =========================

app.add_middleware(
CORSMiddleware,
allow_origins=["*"],
allow_credentials=True,
allow_methods=["*"],
allow_headers=["*"],
)

# =========================

# CUSTOM MIDDLEWARE

# =========================

@app.middleware("http")
async def log_requests(request, call_next):

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time

    response.headers["X-Process-Time"] = str(process_time)

    print(f"{request.method} {request.url} Completed")

    return response

# DATABASE CONFIGURATION

DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()

# DATABASE MODEL

class ItemDB(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)
    in_stock = Column(Boolean, default=True)
    tags = Column(String)

Base.metadata.create_all(bind=engine)

# PYDANTIC SCHEMA

class Item(BaseModel):
    name: str = Field(..., min_length=2)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    quantity: int = Field(..., ge=0)
    in_stock: bool = True
    tags: List[str] = []

class ItemResponse(Item):
    id: int
    class Config:
        from_attributes = True

# DATABASE DEPENDENCY

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# JWT AUTHENTICATION

SECRET_KEY = "5eae0113b5b0cc4ef769056cb87c91fc476271246879378d1b482db3f2e464c4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/login"
)

fake_user = {
    "username": "admin",
    "password": "admin123"
}


def authenticate_user(username, password):
    if username != fake_user["username"]:
        return False
    return fake_user

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def get_current_user(
    token: str = Depends(oauth2_scheme)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid Token"
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        return username

    except JWTError:
        raise credentials_exception

# BACKGROUND TASK

def send_notification(item_name: str):
    print(f"Notification Sent For {item_name}")

# LOGIN API

@app.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):

    user = authenticate_user(
        form_data.username,
        form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username or Password"
        )
    access_token = create_access_token(
        data={"sub": user["username"]}
    )
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ROOT API
@app.get("/")
async def home():
    return {
        "message": "Welcome to FastAPI Inventory App"
    }

# HEALTH CHECK API

@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }

 # Helper function to convert DB model to response model
def convert_item_response(item):

    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "quantity": item.quantity,
        "in_stock": item.in_stock,
        "tags": item.tags.split(",") if item.tags else []
    }

# CREATE ITEM API

@app.post("/items/", response_model=ItemResponse, status_code=201)
async def create_item(
    item: Item,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_item = ItemDB(
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
        in_stock=item.in_stock,
        tags=",".join(item.tags)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    background_tasks.add_task(
        send_notification,
        item.name
    )
    return convert_item_response(db_item)

# GET ALL ITEMS API

@app.get("/items/", response_model=List[ItemResponse])
async def get_all_items(
    skip: int = 0,
    limit: int = Query(default=10, le=100),
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    items = db.query(ItemDB)\
        .offset(skip)\
        .limit(limit)\
        .all()

    return [convert_item_response(item) for item in items]

# GET SINGLE ITEM API

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_single_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    item = db.query(ItemDB)\
        .filter(ItemDB.id == item_id)\
        .first()

    if not item:
        raise HTTPException(
            status_code=404,
            detail="Item Not Found"
        )
    return convert_item_response(item)

# UPDATE ITEM API

@app.put("/items/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item: Item,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_item = db.query(ItemDB)\
        .filter(ItemDB.id == item_id)\
        .first()

    if not db_item:
        raise HTTPException(
            status_code=404,
            detail="Item Not Found"
        )

    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.quantity = item.quantity
    db_item.in_stock = item.in_stock
    db_item.tags = ",".join(item.tags)

    db.commit()
    db.refresh(db_item)
    return convert_item_response(db_item)

# DELETE ITEM API

@app.delete("/items/{item_id}")
async def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    db_item = db.query(ItemDB)\
        .filter(ItemDB.id == item_id)\
        .first()

    if not db_item:
        raise HTTPException(
            status_code=404,
            detail="Item Not Found"
        )

    db.delete(db_item)
    db.commit()
    return {
        "message": "Item Deleted Successfully"
    }

# LOW STOCK ITEMS API

@app.get("/items/low-stock/")
async def low_stock_items(
    threshold: int = 5,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    items = db.query(ItemDB)\
        .filter(ItemDB.quantity < threshold)\
        .all()

    return {
        "total_low_stock_items": len(items),
        "items": [convert_item_response(item) for item in items]
    }
