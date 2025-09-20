from fastapi import FastAPI
from contextlib import asynccontextmanager
from .api import users, auth, chat, matching, gamification, offers, profile, assets
from .initial_data import create_initial_admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup...")
    create_initial_admin()
    yield
    print("Application shutdown...")

app = FastAPI(title="Talent Navigator AI API", version="0.1.0", lifespan=lifespan)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(matching.router)
app.include_router(gamification.router)
app.include_router(offers.router)
app.include_router(profile.router)
app.include_router(assets.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"status": "ok", "message": "Welcome to Talent Navigator AI API!"}