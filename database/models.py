import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    ForeignKey,
    Table,
    DateTime
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Association Table for the many-to-many relationship between VinylRecord and Category
vinyl_record_category_association = Table(
    'vinyl_record_category',
    Base.metadata,
    Column('vinyl_record_id', Integer, ForeignKey('vinyl_records.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Artist(Base):
    """
    Entity representing an artist/performer.
    An artist can have multiple vinyl records.
    """
    __tablename__ = 'artists'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)

    # One-to-Many relationship with VinylRecord
    vinyl_records = relationship("VinylRecord", back_populates="artist")

class Category(Base):
    """
    Entity representing a category or genre for a vinyl record.
    """
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)

    # Many-to-Many relationship is defined in VinylRecord via the association table

class VinylRecord(Base):
    """
    Aggregate root for the VinylRecord.
    It holds information about the vinyl record and its relationships.
    """
    __tablename__ = 'vinyl_records'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    cover_image_url = Column(String(500), nullable=True)

    # Foreign key for the one-to-many relationship with Artist (artist/performer)
    artist_id = Column(Integer, ForeignKey('artists.id'), nullable=False)

    # Many-to-One relationship with Artist (artist/performer)
    artist = relationship("Artist", back_populates="vinyl_records")

    # Many-to-Many relationship with Category
    categories = relationship(
        "Category",
        secondary=vinyl_record_category_association,
        backref="vinyl_records"
    )

class Order(Base):
    """
    Represents a customer's order.
    """
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    total_price = Column(Float, nullable=False)

    # One-to-Many relationship with OrderItem
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    """
    Represents a single item within an order.
    """
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    vinyl_id = Column(Integer, nullable=False) # We don't use a FK here to keep services decoupled
    quantity = Column(Integer, nullable=False)
    price_at_purchase = Column(Float, nullable=False)

    # Many-to-One relationship with Order
    order = relationship("Order", back_populates="items")

class User(Base):
    """
    Entity representing a user.
    """
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)

class Prompt(Base):
    """
    Entity representing an AI prompt template.
    Used for centralized storage and versioning of AI instructions.
    """
    __tablename__ = 'prompts'

    id = Column(String(255), primary_key=True, index=True)  # Строковый ключ, не автоинкрементный (например, 'recommendation_prompt')
    name = Column(String(255), nullable=False)
    template = Column(Text, nullable=False)  # Сам текст промпта