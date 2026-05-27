from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

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


# create  items API
@app.post("/items/", status_code=201)
def create_item(item: Item):
    item_id = len(items_db) + 1 # simple id generation
    items_db[item_id] = item
    return {"id": item_id, **items_db[item_id].dict()}

# GET all the items API
@app.get("/items/")
def get_all_items():
    return items_db

# GET Single item by id API
@app.get("/items/{item_id}")
def get_single_item(item_id: int):
    if item_id in items_db:
        return {"id": item_id, **items_db[item_id].dict()}
    raise HTTPException(status_code=404, detail="Item not found")

# Update Item API
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id in items_db:
        items_db[item_id] = item
        return {"message": "Item updated successfully", 
                "id": item_id, 
                "data": items_db[item_id].dict()
                }
    raise HTTPException(status_code=404, detail="Item not found")

# Delete Item API
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id in items_db:
        del items_db[item_id]
        return {"message": "Item deleted successfully"}
    raise HTTPException(status_code=404, detail="Item not found")
