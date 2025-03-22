from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from fastapi.middleware.trustedhost import TrustedHostMiddleware  # type: ignore
from contextlib import asynccontextmanager
import os
from redis import Redis
from routers import products, brands, category, p_specification, specifications, images, others, orders, order_items
from routers.auth import auth
from aws import s3

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    redis_url = os.getenv("REDIS_URL")
    app.state.redis = Redis.from_url(redis_url)
    yield
    # Shutdown code
    app.state.redis.close()

app = FastAPI(lifespan=lifespan)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://texnotech.vercel.app",
        "https://admin-texnotech.vercel.app",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://texnotech.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(brands.router)
app.include_router(category.router)
app.include_router(p_specification.router)
app.include_router(specifications.router)
app.include_router(images.router)
app.include_router(s3.router)
app.include_router(others.router)
app.include_router(orders.router)
app.include_router(order_items.router)