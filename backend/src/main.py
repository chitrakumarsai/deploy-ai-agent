from fastapi import FastAPI
import os

app = FastAPI()
@app.get("/")
def read_index():
    return {"message": "Welcome to the FastAPI application! This is the index page."}   