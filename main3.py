from fastapi import (
    FastAPI, 
    HTTPException,
    Depends,
    BackgroundTasks,
    Header,
    Request,
    )

from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI()

# CORS Configuration

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
    allow_credentials=True,
)

# Middleware

@app.middleware("http")
async def log_requests(request, call_next):
    start_time = time.time()
    print(f"Request Started: {request.method} {request.url}")
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Request Completed in {process_time}")

    return response

# Temporary in-memory storage
items_db = {} # dictionary to store items with id as key

# Request Body Schema
class Item(BaseModel):
    name : str
    description: Optional[str] = None
    price: float
    quantity: int
    in_stock: bool
    tags: List[str] = []

# Dependency Injections

def verify_token(x_token: str = Header(None)):
    if x_token != "admin123":
        raise HTTPException(
            status_code=401, 
            detail="Invalid X-Token"
        )
    
    return {"username": "admin"}

# Custom Exception
class ItemNotFoundException(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id

# Custom Exception Handler
@app.exception_handler(ItemNotFoundException)
def item_not_found_exception_handler(
    request: Request, 
    exc: ItemNotFoundException):
    return JSONResponse(
        status_code=404,
        content={"message": f"Item with id {exc.item_id} not found"}
    )

# Background Task

def send_notification(item_name: str):
    time.sleep(5)  # Simulate delay
    print(f"Notification sent for item: {item_name}")


# Root API

@app.get("/")
def home():
    return {"message": "Welcome to the FastAPI application!"}


# create  items API
@app.post("/items/", status_code=201)
def create_item(
        item: Item,
        background_tasks: BackgroundTasks,
        user=Depends(verify_token)):
    item_id = len(items_db) + 1 # simple id generation
    items_db[item_id] = item
    
    background_tasks.add_task(send_notification, item.name)
    return {
        "id": item_id, 
        "data": items_db[item_id].dict(),
        "created_by": user
        }

# GET all the items API
@app.get("/items/")
def get_all_items(user=Depends(verify_token)):
    return {
        "total_items": len(items_db),
        "items": items_db,
        "requested_by": user
    }



# GET Single item by id API
@app.get("/items/{item_id}")
def get_single_item(item_id: int, user=Depends(verify_token)):
    if item_id in items_db:
        return {"id": item_id, "data": items_db[item_id].dict(), "requested_by": user}
    raise HTTPException(status_code=404, detail="Item not found")


# Update Item API
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item, user=Depends(verify_token)):
    if item_id in items_db:
        items_db[item_id] = item
        return {"message": "Item updated successfully", 
                "id": item_id, 
                "data": items_db[item_id].dict(),
                "updated_by": user
            }
    raise HTTPException(status_code=404, detail="Item not found")

# Delete Item API
@app.delete("/items/{item_id}")
def delete_item(item_id: int, user=Depends(verify_token)):
    if item_id in items_db:
        del items_db[item_id]
        return {"message": "Item deleted successfully", "deleted_by": user}
    raise HTTPException(status_code=404, detail="Item not found")

# Low Stocks API
@app.get("/items/low-stock/")
def low_stock_items(threshold: int = 5, user=Depends(verify_token)):
    low_stock = {item_id: item for item_id, item in items_db.items() if item.quantity < threshold}
    return {
        "total_low_stock_items": len(low_stock),
        "low_stock_items": low_stock,
        "requested_by": user
    }

# Clear all the records in the database
@app.delete("/items/clear/")
def clear_items(user=Depends(verify_token)):  
    items_db.clear()
    return {"message": "All items cleared successfully", "requested_by": user}