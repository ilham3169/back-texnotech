from sqlalchemy import (
    Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, TIMESTAMP, text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(63), nullable=False)
    last_name = Column(String(63), nullable=False)
    hashed_pass = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, default=None)
    phone = Column(String(15), unique=True, nullable=False)
    social_id = Column(String(255), unique=True, default=None)
    provider = Column(Enum("google", "facebook", "email", "phone"))
    mail_verified = Column(Boolean, nullable=False, default=False)
    phone_verified = Column(Boolean, nullable=False, default=False)
    is_admin = Column(Boolean, nullable=False, default=False)
    is_seller = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    fin = Column(String, unique=True)

    products = relationship("Product", back_populates="author")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), nullable=False, unique=True)
    num_category = Column(Integer, nullable=False, default=0)
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    products = relationship("Product", back_populates="category")


class Brand(Base):
    __tablename__ = "brends"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(63), nullable=False, unique=True)
    num_brend = Column(Integer, nullable=False, default=0)
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    is_active = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    image_link = Column(String(255), nullable=False)

    products = relationship("Product", back_populates="brend")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(127), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    price = Column(Integer, nullable=False)
    num_product = Column(Integer, nullable=False, default=0)
    image_link = Column(String(255), nullable=False)
    brend_id = Column(Integer, ForeignKey("brends.id"), nullable=False)
    model_name = Column(String(127), nullable=False)
    discount = Column(Integer, nullable=False)
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    search_string = Column(String(511), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    category = relationship("Category", back_populates="products")
    brend = relationship("Brand", back_populates="products")
    author = relationship("User", back_populates="products")
    specifications = relationship("ProductSpecification", back_populates="product")


class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(127), nullable=False)
    category = Column(String(63), nullable=False)

    product_specifications = relationship("ProductSpecification", back_populates="specification")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    specification_id = Column(Integer, ForeignKey("specifications.id"), nullable=False)
    value = Column(String(63), nullable=False)

    product = relationship("Product", back_populates="specifications")
    specification = relationship("Specification", back_populates="product_specifications")
