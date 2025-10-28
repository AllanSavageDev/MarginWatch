from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import List
from services.auth import get_current_user  # your JWT validator

router = APIRouter()

# ---- Demo Models ----
class Item(BaseModel):
    id: int
    name: str
    description: str

fake_db = []

# ---- CRUD Routes ----
@router.get("/items", response_model=List[Item])
def list_items(user=Depends(get_current_user)):
    return fake_db

@router.post("/items", response_model=Item)
def create_item(item: Item, user=Depends(get_current_user)):
    fake_db.append(item)
    return item

@router.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated: Item, user=Depends(get_current_user)):
    for idx, item in enumerate(fake_db):
        if item.id == item_id:
            fake_db[idx] = updated
            return updated
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/items/{item_id}")
def delete_item(item_id: int, user=Depends(get_current_user)):
    global fake_db
    fake_db = [item for item in fake_db if item.id != item_id]
    return {"message": "Deleted"}

# ---- Auth Clone ----
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/auth")
def login(request: LoginRequest):
    if request.email == "demo@demo.com" and request.password == "password":
        return {"access_token": "demo_token", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")
