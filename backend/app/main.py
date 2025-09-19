from fastapi import FastAPI

app = FastAPI(
    title="HR Navigator AI API",
    description="API для управления карьерной платформой.",
    version="0.1.0"
)

@app.get("/")
def read_root():
    """
    Корневой эндпоинт для проверки, что API работает.
    """
    return {"status": "ok", "message": "Welcome to Talent Navigator AI API!"}