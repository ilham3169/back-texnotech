from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: str
    is_admin: Optional[bool] = False
    is_seller: Optional[bool] = False
    is_active: Optional[bool] = True

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    mail_verified: bool
    phone_verified: bool
    date_created: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    num_category: Optional[int] = 0
    is_active: Optional[bool] = False

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    date_created: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Brand Schemas
class BrandBase(BaseModel):
    name: str
    num_brend: Optional[int] = 0
    is_active: Optional[bool] = False
    image_link: str

class BrandCreate(BrandBase):
    pass

class BrandResponse(BrandBase):
    id: int
    date_created: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Product Schemas
class ProductBase(BaseModel):
    name: str
    category_id: int
    price: int
    num_product: Optional[int] = 0
    image_link: str
    brend_id: int
    model_name: str
    discount: int
    search_string: str
    author_id: int

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    date_created: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Specification Schemas
class SpecificationBase(BaseModel):
    name: str
    category: str

class SpecificationCreate(SpecificationBase):
    pass

class SpecificationResponse(SpecificationBase):
    id: int

    class Config:
        orm_mode = True


# Product Specification Schemas
class ProductSpecificationBase(BaseModel):
    product_id: int
    specification_id: int
    value: str

class ProductSpecificationCreate(ProductSpecificationBase):
    pass

class ProductSpecificationResponse(ProductSpecificationBase):
    id: int

    class Config:
        orm_mode = True
