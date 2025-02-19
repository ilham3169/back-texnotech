from sqlalchemy import ( # type: ignore
    Boolean, Column, Integer, String, DateTime, Enum, ForeignKey, TIMESTAMP, text, Float
)
from sqlalchemy.orm import relationship # type: ignore
from database import Base
from datetime import datetime


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
    icon_image_link = Column(String(511), nullable=False)
    parent_category_id = Column(Integer, nullable = True, unique = True, default = None)


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
    brend_id = Column(Integer, ForeignKey("brends.id"), nullable=False)  # Ensure this is correct
    model_name = Column(String(127), nullable=False)
    discount = Column(Integer, nullable=False)
    date_created = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    search_string = Column(String(511), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_super = Column(Boolean, nullable=False, default=False)
    is_new = Column(Boolean, nullable=False, default=False)


    category = relationship("Category", back_populates="products")
    brend = relationship("Brand", back_populates="products")  # Ensure this is correct
    author = relationship("User", back_populates="products")
    specifications = relationship("ProductSpecification", back_populates="product")
    images = relationship("Image", back_populates="product", cascade="all, delete-orphan")

class Specification(Base):
    __tablename__ = "specifications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(127), nullable=False)
    category_id = Column(Integer, nullable=False)

    product_specifications = relationship("ProductSpecification", back_populates="specification")


class ProductSpecification(Base):
    __tablename__ = "product_specifications"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    specification_id = Column(Integer, ForeignKey("specifications.id"), nullable=False)
    value = Column(String(63), nullable=False)

    product = relationship("Product", back_populates="specifications", passive_deletes=True)
    specification = relationship("Specification", back_populates="product_specifications")


class Image(Base):
    __tablename__ = "images"

    id = Column(Integer, primary_key=True, index=True)
    image_link = Column(String(511), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=True)

    # Relationships
    product = relationship("Product", back_populates="images")


class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True, index=True)
<<<<<<< Updated upstream
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)  # Make user_id nullable
=======
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"), nullable=True)  
>>>>>>> Stashed changes
    name = Column(String(63), nullable=False)
    surname = Column(String(63), nullable=False)
    phone_number = Column(String(15), nullable=False)
    total_price = Column(Float, nullable=False)
    status = Column(Enum('pending', 'processing', 'shipped', 'delivered', 'canceled'), default='pending')
    payment_status = Column(Enum('paid', 'unpaid', 'failed', 'refunded'), default='unpaid')
    payment_method = Column(String(50), nullable=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with OrderItems
    order_items = relationship("OrderItem", back_populates="order")
<<<<<<< Updated upstream
    
=======



>>>>>>> Stashed changes
class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    # Relationship with Orders
<<<<<<< Updated upstream
    order = relationship("Order", back_populates="order_items")
=======
    order = relationship("Order", back_populates="order_items")

>>>>>>> Stashed changes
