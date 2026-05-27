from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def get_data():
    return {"message": "Hello, World!"}

# Path parameter example
@app.get("/users/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id}

@app.get("/products/{category}/{product_id}")
def get_product(category: str, product_id: int):
    return {
            "category": category,
            "product_id": product_id
            }

# Query parameter example

items = [
    {"id": 1, "name": "Laptop"},
    {"id": 2, "name": "Mouse"},    
    {"id": 3, "name": "Keyboard"},
    {"id": 4, "name": "Monitor"},
    {"id": 5, "name": "Headphones"},
    {"id": 6, "name": "Smartphone"},
    {"id": 7, "name": "Tablet"},
    {"id": 8, "name": "Printer"},
    {"id": 9, "name": "Camera"},
    {"id": 10, "name": "Speaker"}            
]

@app.get("/items/search")
def search_items(q: str = ""):
    return [item for item in items if q.lower() in item["name"].lower()]
