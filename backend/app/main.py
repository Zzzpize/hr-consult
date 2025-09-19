from fastapi import FastAPI
from .api import users, auth, career_plan, matching, gamification

app = FastAPI(
    title="HR Navigator AI API",
    description="API для управления карьерной платформой.",
    version="0.1.0"
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(career_plan.router)
app.include_router(matching.router)
app.include_router(gamification.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to HR Navigator AI API!"}