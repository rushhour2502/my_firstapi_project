from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
from models import ItemModel
import models

# This line tells SQLAlchemy to create all the database tables defined by our models.
# OOP Concept: We tell the 'metadata' object to perform an action ('create_all') 
# using the database connection object ('engine').
models.Base.metadata.create_all(bind=engine)

# We create an instance (a specific copy) of the FastAPI class. 
# OOP Concept: 'app' is an object that represents our entire web application.
app = FastAPI()


# Here, we define a class called 'Item' that inherits from (is a blueprint based on) 'BaseModel'.
# OOP Concept: Inheritance. By writing 'class Item(BaseModel):', we get all the data-validating
# features of Pydantic's BaseModel inside our custom Item class without rewriting them.
class Item(BaseModel):
    name: str              # The item's name (string of text)
    price: float           # The item's price (a number with a decimal/float)
    description: str = None # An optional description (defaults to nothing/None)


# This function creates and manages our connection to the database.
def get_db():
    # 'db' here represents a database "Session" object.
    db = SessionLocal()
    try:
        yield db  # Give this database connection object to whatever function needs it
    finally:
        db.close()  # Object cleanup: Always close the connection when we're done!

# @app.get is a decorator. It tells the 'app' object that if someone visits the root URL ("/")
# using a GET request (like a normal web browser visit), it should run this function.
@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# This endpoint expects a variable in the URL path, like /items/5 (where 5 is the item_id)
@app.get("/items/{item_id}")
def read_item(item_id: int, db: Session = Depends(get_db)):
    # We ask the 'db' object to search (query) the 'ItemModel', filter down to the 
    # matching ID, and give us the first result.
    # OOP Concept: Method chaining. .query() returns an object, we call .filter() on it, 
    # which returns another object, and we finally call .first() on that.
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    return item

# @app.post means this endpoint is meant for receiving new data.
@app.post("/items/")
def create_item(item: Item, db: Session = Depends(get_db)):
    # Create a new instance (object) of ItemModel based on the incoming data.
    # **item.dict() takes the data from our Item object and unwraps it into arguments.
    db_item = ItemModel(**item.dict())
    
    # OOP Concept: State changes and actions on objects.
    db.add(db_item)      # Tell the database session object to stage this new object
    db.commit()          # Tell the session to save (commit) it to the actual database
    db.refresh(db_item)  # Re-sync our local object with the DB (e.g., to fetch the new auto-generated ID)
    
    return db_item

@app.get("/all-items/")
def get_all_items(db: Session = Depends(get_db)):
    # Ask the database session object to give us .all() the records for ItemModel.
    items = db.query(ItemModel).all()
    return {"items": items}