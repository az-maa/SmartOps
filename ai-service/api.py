from fastapi import FastAPI

app = FastAPI(title="Smart OPS AI Service")

@app.get("/")
def root():
    return {"message": "AI Service is running"}
 
