from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore
from fastapi.middleware.trustedhost import TrustedHostMiddleware # type: ignore
import os

from routers import products, brands, category, p_specification, specifications
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
app.include_router(p_specification.router)
app.include_router(specifications.router)