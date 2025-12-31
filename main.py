from fastapi import FastAPI
from app.db.session import engine
from app.db.base import Base
app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the terraform backend API"}

Base.metadata.create_all(bind=engine)