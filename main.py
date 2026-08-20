from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import db
from app.core.migrations import run_migrations
from app.routes import products, categories, auth, images , chat

origins = ["http://localhost:3000", "https://tim-game-store-landing.vercel.app"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    await run_migrations(db.pool)
    yield
    await db.disconnect()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=("POST", "GET", "PATCH" , "PUT", "DELETE"),
    allow_headers=["*"]
    )


app.include_router(products.router)
app.include_router(categories.router)
app.include_router(auth.router)
app.include_router(images.router)
app.include_router(chat.router)