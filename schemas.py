from pydantic import BaseModel, EmailStr
from typing import Optional, List, Literal
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
    icon_image_link: Optional[str] = None

    class Config:
        orm_mode = True


# Brand Schemas
class BrandBase(BaseModel):
    name: str


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
    is_active: bool = True  # Default to True, but keep as required in base

    class Config:
        orm_mode = True

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    date_created: datetime
    updated_at: datetime
    is_active: Optional[bool] = True  # Make optional with a default value

    class Config:
        orm_mode = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None 
    price: Optional[int] = None  
    num_product: Optional[int] = None
    image_link: Optional[str] = None
    brend_id: Optional[int] = None 
    model_name: Optional[str] = None
    discount: Optional[int] = None  
    search_string: Optional[str] = None
    author_id: Optional[int] = None  
    is_super: Optional[bool] = None
    is_new: Optional[bool] = None
    is_active: Optional[bool] = None  # Already optional here

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


class ProductSpecificationUpdate(BaseModel):
    product_id: int
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



# ---- Order Base Schemas ---- #
class OrderBase(BaseModel):
    name: str
    surname: str
    phone_number: str
    total_price: float
    status: Optional[str] = "pending"
    status: Optional[Literal["pending", "processing", "shipped", "delivered", "canceled"]] = "pending"
    payment_status: Optional[str] = "unpaid"
    payment_method: Optional[str] = None


class OrderCreate(OrderBase):
    pass


# ---- OrderItem Schemas ---- #
class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: float


class OrderItemCreate(OrderItemBase):
    pass


class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        orm_mode = True


# ---- Order Response Schemas ---- #
class Order(OrderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class OrderWithItems(Order):
    order_items: List[OrderItem]

    class Config:
        orm_mode = True


class OrderItemResponse(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price_at_purchase: float

    class Config:
        orm_mode = True


class OrderResponse(BaseModel):
    id: int
    user_id: int
    name: str
    surname: str
    phone_number: str
    total_price: float
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    order_items: List[OrderItemResponse]

    class Config:
        orm_mode = True

class OrderPaymentUpdate(BaseModel):
    payment_status: str

class OrderStatusUpdate(BaseModel):
    status: str