from pydantic import BaseModel, EmailStr
from typing import List, Optional

# ====================================================================
# Pydantic Schemas for API Data Contracts (DTOs)
# ====================================================================

# These schemas define the shape of the data for API requests and responses.
# The `Config` class with `from_attributes = True` allows the schemas to
# be created directly from SQLAlchemy ORM objects.

class ArtistSchema(BaseModel):
    """
    Schema for representing an Artist/Performer.
    """
    id: int
    name: str

    class Config:
        from_attributes = True

class ArtistCreate(BaseModel):
    """
    Schema for creating a new Artist/Performer.
    """
    name: str

class CategorySchema(BaseModel):
    """
    Schema for representing a Category/Genre.
    """
    id: int
    name: str

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    """
    Schema for creating a new Category/Genre.
    """
    name: str

class VinylRecordSchema(BaseModel):
    """
    Main schema for a VinylRecord, including nested artist and category data.
    """
    id: int
    title: str
    description: Optional[str] = None
    price: float
    cover_image_url: Optional[str] = None
    
    # Nested schema for the artist/performer relationship
    artist: ArtistSchema
    
    # Nested list of schemas for the categories relationship
    categories: List[CategorySchema] = []

    class Config:
        from_attributes = True

class VinylRecordCreate(BaseModel):
    """
    Schema for creating a new VinylRecord.
    """
    title: str
    description: Optional[str] = None
    price: float
    artist_id: int
    category_ids: List[int] = []

class VinylRecordUpdate(BaseModel):
    """
    Schema for updating an existing VinylRecord.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    artist_id: Optional[int] = None
    category_ids: Optional[List[int]] = None

# --- Schemas for Analytics & Statistics ---

class CatalogStats(BaseModel):
    """
    Schema for overall catalog statistics.
    """
    total_vinyl_records: int
    total_artists: int
    total_authors: int  # Для обратной совместимости
    total_categories: int

class AuthorSummary(BaseModel):
    """
    Schema for an artist's summary.
    """
    record_count: int
    average_price: Optional[float] = None

class CategoryAnalysis(BaseModel):
    """
    Schema for category analysis.
    """
    record_count: int
    artists_in_category: List[str]

# --- Schemas for Comprehensive Operations ---

class ComprehensiveVinylRecordCreate(BaseModel):
    """
    Schema for creating a vinyl record, artist, and categories in one go.
    """
    title: str
    description: Optional[str] = None
    price: float
    artist_name: str
    category_names: List[str] = []

# --- Schemas for Authentication ---

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    """
    Schema for returning user information without the password.
    """
    email: EmailStr
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
