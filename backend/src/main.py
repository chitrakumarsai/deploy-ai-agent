from fastapi import FastAPI
import os

app = FastAPI()
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise NotImplementedError(" API_KEY environment variable is not set. Please set it before running the application.")
@app.get("/")
def read_index():
    return {"message": "Welcome to the FastAPI application! This is the index page."}   