from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    fin: str
    first_name: str
    last_name: str
    email: Optional[EmailStr] = None
    phone: str
    is_admin: Optional[bool] = False
    is_seller: Optional[bool] = False


class UserCreate(UserBase):
    password: str
    confirm_password: str


class UserResponse(UserBase):
    id: int
    mail_verified: bool
    phone_verified: bool
    date_created: datetime
    updated_at: datetime
    is_active: Optional[bool] = True

    class Config:
        from_attributes = True


# Category Schemas
class CategoryBase(BaseModel):
    name: str
    num_category: Optional[int] = 0
    is_active: Optional[bool] = False


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    parent_category_id: Optional[int] = None
    date_created: datetime
    updated_at: datetime
    icon_image_link: str

    class Config:
        orm_mode = True


# Brand Schemas
class BrandBase(BaseModel):
    name: str
    num_brand: Optional[int] = 0
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
    num_product: int = 0  # Default value is set to 0, no need for Optional
    image_link: str
    brend_id: int  # Use brend_id here to match the SQLAlchemy model
    model_name: str
    discount: int
    search_string: str
    author_id: int
    is_super: bool
    is_new: bool

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
    category_id: int


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


# Image Schemas
class ImageBase(BaseModel):
    image_link: str
    product_id: Optional[int] = None


class ImageCreate(ImageBase):
    pass

class ImageResponse(BaseModel):
    id: int
    image_link: str
    product_id: Optional[int] = None

    class Config:
        orm_mode = True

# JWT Token Schemas
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


# Email Schemas
class EmailSchema(BaseModel):
    email: EmailStr


# Password Schemas
class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
