from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_index():
    return {"message": "Welcome to the FastAPI application!"}   