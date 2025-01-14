from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

from routers import products, brands, category, p_specifications
from routers.auth import auth


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


app.include_router(auth.router)
app.include_router(products.router)
app.include_router(brands.router)
app.include_router(category.router)
