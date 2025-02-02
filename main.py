from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.middleware.trustedhost import TrustedHostMiddleware # type: ignore
from fastapi.middleware.cors import CORSMiddleware

import os

from redis import Redis

from routers import products, brands, category, p_specification, specifications, images
from routers.auth import auth
from aws import s3


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow only your frontend domain
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
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