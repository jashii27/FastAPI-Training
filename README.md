# FastAPI CRUD Application

## Project Overview

This project is a complete FastAPI CRUD application that demonstrates:

* FastAPI basics
* CRUD Operations
* Middleware
* Dependency Injection
* Header Authentication
* Background Tasks
* Query Parameters
* Custom Exception Handling
* Pydantic Validation
* CORS Configuration
* REST API Development

The project uses an in-memory dictionary as a temporary database.

---

# Project Structure

```bash
project_folder/
│
├── main.py
├── requirements.txt
└── README.md
```

---

# Step 1 — Install Python

Make sure Python 3.9+ is installed.

Check Python version:

```bash
python --version
```

OR

```bash
python3 --version
```

---

# Step 2 — Create Virtual Environment

## Windows

```bash
python -m venv venv
```

Activate Virtual Environment:

```bash
venv\Scripts\activate
```

---

## Mac/Linux

```bash
python3 -m venv venv
```

Activate Virtual Environment:

```bash
source venv/bin/activate
```

---

# Step 3 — Install Dependencies

Install required packages:

```bash
pip install fastapi uvicorn
```

OR using requirements file:

Create `requirements.txt`

```txt
fastapi
uvicorn
```

Install:

```bash
pip install -r requirements.txt
```

---

# Step 4 — Create main.py File

Create a file named:

```bash
main.py
```

Paste the complete FastAPI code inside it.

---

# Step 5 — Run FastAPI Server

Run the application using Uvicorn:

```bash
uvicorn main:app --reload
```

Explanation:

```bash
main     -> filename
app      -> FastAPI instance name
--reload -> auto restart server after code changes
```

---

# Step 6 — Open Browser

After running the server:

```bash
http://127.0.0.1:8000
```

You will see:

```json
{
  "message": "FastAPI CRUD Application Running"
}
```

---

# Step 7 — Swagger UI Documentation

FastAPI automatically generates API documentation.

Open:

```bash
http://127.0.0.1:8000/docs
```

Alternative ReDoc:

```bash
http://127.0.0.1:8000/redoc
```

---

# Authentication

All protected APIs require a custom header.

Header Name:

```bash
x-token
```

Header Value:

```bash
admin123
```

Without this header:

```json
{
  "detail": "Invalid Token"
}
```

---

# API Endpoints

---

# 1. Home API

## Endpoint

```http
GET /
```

## Response

```json
{
  "message": "FastAPI CRUD Application Running"
}
```

---

# 2. Create Item API

## Endpoint

```http
POST /items/
```

## Headers

```http
x-token: admin123
```

## Request Body

```json
{
  "name": "Laptop",
  "description": "Gaming Laptop",
  "price": 75000,
  "quantity": 10,
  "in_stock": true,
  "tags": ["electronics", "gaming"]
}
```

## Response

```json
{
  "message": "Item Created Successfully",
  "id": 1,
  "data": {
    "name": "Laptop",
    "description": "Gaming Laptop",
    "price": 75000,
    "quantity": 10,
    "in_stock": true,
    "tags": [
      "electronics",
      "gaming"
    ]
  },
  "created_by": {
    "username": "Admin"
  }
}
```

---

# 3. Get All Items API

## Endpoint

```http
GET /items/
```

## Headers

```http
x-token: admin123
```

---

# 4. Get Single Item API

## Endpoint

```http
GET /items/{item_id}
```

Example:

```http
GET /items/1
```

---

# 5. Update Item API

## Endpoint

```http
PUT /items/{item_id}
```

Example:

```http
PUT /items/1
```

## Headers

```http
x-token: admin123
```

## Request Body

```json
{
  "name": "Updated Laptop",
  "description": "Updated Gaming Laptop",
  "price": 85000,
  "quantity": 5,
  "in_stock": true,
  "tags": ["electronics"]
}
```

---

# 6. Delete Item API

## Endpoint

```http
DELETE /items/{item_id}
```

Example:

```http
DELETE /items/1
```

---

# 7. Search Item API

## Endpoint

```http
GET /search/?keyword=laptop&min_price=50000
```

## Query Parameters

| Parameter | Type   | Description    |
| --------- | ------ | -------------- |
| keyword   | string | Search keyword |
| min_price | float  | Minimum price  |

---

# 8. Low Stock API

## Endpoint

```http
GET /low-stock/?threshold=5
```

## Query Parameter

| Parameter | Type | Description |
| --------- | ---- | ----------- |
| threshold | int  | Stock limit |

---
# 9. Clear Database API

## Endpoint

```http
DELETE /clear-db/
```

---

# Middleware Working

This project contains custom middleware.

Middleware performs:

* Logs incoming request
* Measures API execution time
* Adds custom response header

Example Header:

```http
X-Process-Time: 0.0021
```

---

# Background Tasks

When an item is created:

```python
background_tasks.add_task(send_notification, item.name)
```

FastAPI runs the notification task in the background.

Main response returns immediately.

---

# Pydantic Validation

The `Item` model validates incoming data.

Example:

```python
name: str = Field(..., min_length=3)
price: float = Field(..., gt=0)
quantity: int = Field(..., ge=1)
```

Validation Rules:

| Field    | Rule                       |
| -------- | -------------------------- |
| name     | Minimum 3 characters       |
| price    | Greater than 0             |
| quantity | Greater than or equal to 1 |

---

# Custom Exception Handling

If item is not found:

```python
raise ItemNotFoundException(item_id)
```

Custom handler returns:

```json
{
  "error": "Item with ID 1 not found"
}
```

---

# CORS Configuration

```python
allow_origins=["*"]
```

This allows requests from all domains.

Useful for frontend-backend communication.

---

# Testing APIs Using Swagger UI

1. Open:

```bash
http://127.0.0.1:8000/docs
```

2. Select API
3. Click "Try it out"
4. Enter request data
5. Add header:

```http
x-token: admin123
```

6. Click Execute

---

# Common Errors

# 1. Uvicorn Not Found

Install uvicorn:

```bash
pip install uvicorn
```

---

# 2. Port Already In Use

Run on another port:

```bash
uvicorn main:app --reload --port 8001
```

---

# 3. Invalid Token Error

Make sure header is:

```http
x-token: admin123
```

---

# 4. Module Not Found Error

Install dependencies again:

```bash
pip install -r requirements.txt
```

---

# Recommended Commands

## Freeze Dependencies

```bash
pip freeze > requirements.txt
```

---

## Stop Server

Press:

```bash
CTRL + C
```

---

# Technologies Used

* Python
* FastAPI
* Uvicorn
* Pydantic
* Swagger UI



# Final Run Command

```bash
uvicorn main:app --reload
```

---

# Project Successfully Ready

Your FastAPI CRUD Application is now ready for:

* Learning FastAPI
* Interview Practice
* Backend Development
* API Development
* Production-Level Concept Understanding
