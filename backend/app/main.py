from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api import users, auth, career_plan, matching, gamification, offers
from .initial_data import create_initial_admin

# --- Lifespan Event ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    create_initial_admin()
    yield
    print("Application shutdown...")


app = FastAPI(
    title="Talent Navigator AI API",
    description="API для управления карьерной платформой.",
    version="0.1.0",
    lifespan=lifespan 
)

# Подключаем роутеры
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(career_plan.router)
app.include_router(matching.router)
app.include_router(gamification.router)
app.include_router(offers.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to Talent Navigator AI API!"}