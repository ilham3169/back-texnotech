from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.middleware.trustedhost import TrustedHostMiddleware # type: ignore

import os

from redis import Redis

from routers import telegram, products, brands, category, p_specification, specifications, images, others, orders, order_items, google_api, analytics, banner
from routers.auth import auth
from aws import s3


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://texnotech.vercel.app",
        "https://admin-texnotech.vercel.app",
        "https://admin-texnotech-3nyw.vercel.app",
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://localhost:5174",
        "https://texnotech.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Connect to Redis on start up 
@app.on_event("startup")
async def startup_event():

    # Connect Redis database to FastAPI application
    redis_url = os.getenv("REDIS_URL")
    app.state.redis = Redis.from_url(redis_url)



# Disconnect from Redis on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    app.state.redis.close()


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
app.include_router(google_api.router)
app.include_router(analytics.router)
app.include_router(banner.router)
app.include_router(telegram.router)