from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import ItemModel
import models

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    description: str = None

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    return item

@app.post("/items/")
def create_item(item: Item, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/all-items/")
def get_all_items(db: Session = Depends(get_db)):
    items = db.query(ItemModel).all()
    return {"items": items}