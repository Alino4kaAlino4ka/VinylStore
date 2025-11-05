import pytest
import httpx
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the project root to the Python path
sys.path.append('../../')

from database.models import Base, Artist, Category, VinylRecord
from database.connection import get_db
from services.catalog.main import app

# Test database configuration
TEST_DATABASE_URL = "sqlite:///./test_catalog.db"

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override the database dependency
app.dependency_overrides[get_db] = get_test_db

@pytest.fixture(scope="function")
def client():
    """Create a test client for the FastAPI app."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clean up after each test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a database session for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def sample_artist(db_session):
    """Create a sample artist for testing."""
    artist = Artist(name="Test Artist")
    db_session.add(artist)
    db_session.commit()
    db_session.refresh(artist)
    return artist

@pytest.fixture(scope="function")
def sample_category(db_session):
    """Create a sample category for testing."""
    category = Category(name="Test Category")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
def sample_vinyl_record(db_session, sample_artist, sample_category):
    """Create a sample vinyl record for testing."""
    vinyl_record = VinylRecord(
        title="Test Vinyl Record",
        description="Test Description",
        price=19.99,
        artist_id=sample_artist.id,
        categories=[sample_category]
    )
    db_session.add(vinyl_record)
    db_session.commit()
    db_session.refresh(vinyl_record)
    return vinyl_record

class TestHealthCheck:
    """Test the health check endpoint."""
    
    def test_health_check(self, client):
        """Test that the health check endpoint returns 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

class TestArtistCRUD:
    """Test CRUD operations for artists."""
    
    def test_create_artist(self, client):
        """Test creating a new artist."""
        artist_data = {"name": "New Artist"}
        response = client.post("/api/v1/artists", json=artist_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Artist"
        assert "id" in data
    
    def test_get_all_artists(self, client, sample_artist):
        """Test getting all artists."""
        response = client.get("/api/v1/artists")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Artist"

class TestCategoryCRUD:
    """Test CRUD operations for categories."""
    
    def test_create_category(self, client):
        """Test creating a new category."""
        category_data = {"name": "New Category"}
        response = client.post("/api/v1/categories", json=category_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert "id" in data
    
    def test_get_all_categories(self, client, sample_category):
        """Test getting all categories."""
        response = client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Category"

class TestVinylRecordCRUD:
    """Test CRUD operations for vinyl records."""
    
    def test_create_vinyl_record(self, client, sample_artist, sample_category):
        """Test creating a new vinyl record."""
        vinyl_record_data = {
            "title": "New Vinyl Record",
            "description": "New Description",
            "price": 29.99,
            "artist_id": sample_artist.id,
            "category_ids": [sample_category.id]
        }
        response = client.post("/api/v1/vinyl-records", json=vinyl_record_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Vinyl Record"
        assert data["description"] == "New Description"
        assert data["price"] == 29.99
        assert data["artist"]["id"] == sample_artist.id
        assert len(data["categories"]) == 1
        assert data["categories"][0]["id"] == sample_category.id
    
    def test_create_vinyl_record_without_categories(self, client, sample_artist):
        """Test creating a vinyl record without categories."""
        vinyl_record_data = {
            "title": "Simple Vinyl Record",
            "description": "Simple Description",
            "price": 15.99,
            "artist_id": sample_artist.id,
            "category_ids": []
        }
        response = client.post("/api/v1/vinyl-records", json=vinyl_record_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Simple Vinyl Record"
        assert data["categories"] == []
    
    def test_create_vinyl_record_invalid_artist(self, client, sample_category):
        """Test creating a vinyl record with invalid artist ID."""
        vinyl_record_data = {
            "title": "Invalid Vinyl Record",
            "description": "Invalid Description",
            "price": 19.99,
            "artist_id": 999,  # Non-existent artist
            "category_ids": [sample_category.id]
        }
        response = client.post("/api/v1/vinyl-records", json=vinyl_record_data)
        
        assert response.status_code == 404
        assert "Artist not found" in response.json()["detail"]
    
    def test_create_vinyl_record_invalid_category(self, client, sample_artist):
        """Test creating a vinyl record with invalid category ID."""
        vinyl_record_data = {
            "title": "Invalid Vinyl Record",
            "description": "Invalid Description",
            "price": 19.99,
            "artist_id": sample_artist.id,
            "category_ids": [999]  # Non-existent category
        }
        response = client.post("/api/v1/vinyl-records", json=vinyl_record_data)
        
        assert response.status_code == 404
        assert "categories not found" in response.json()["detail"]
    
    def test_get_vinyl_record(self, client, sample_vinyl_record):
        """Test getting a specific vinyl record."""
        response = client.get(f"/api/v1/vinyl-records/{sample_vinyl_record.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_vinyl_record.id
        assert data["title"] == "Test Vinyl Record"
        assert data["artist"]["name"] == "Test Artist"
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "Test Category"
    
    def test_get_vinyl_record_not_found(self, client):
        """Test getting a non-existent vinyl record."""
        response = client.get("/api/v1/vinyl-records/999")
        
        assert response.status_code == 404
        assert "Vinyl record not found" in response.json()["detail"]
    
    def test_get_all_vinyl_records(self, client, sample_vinyl_record):
        """Test getting all vinyl records."""
        response = client.get("/api/v1/vinyl-records")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Vinyl Record"
    
    def test_get_all_vinyl_records_with_pagination(self, client, sample_vinyl_record):
        """Test getting vinyl records with pagination."""
        response = client.get("/api/v1/vinyl-records?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
    
    def test_update_vinyl_record(self, client, sample_vinyl_record, sample_artist):
        """Test updating a vinyl record."""
        update_data = {
            "title": "Updated Vinyl Record",
            "price": 25.99
        }
        response = client.put(f"/api/v1/vinyl-records/{sample_vinyl_record.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Vinyl Record"
        assert data["price"] == 25.99
        assert data["description"] == "Test Description"  # Should remain unchanged
    
    def test_update_vinyl_record_categories(self, client, sample_vinyl_record, db_session):
        """Test updating vinyl record categories."""
        # Create a new category
        new_category = Category(name="New Category")
        db_session.add(new_category)
        db_session.commit()
        db_session.refresh(new_category)
        
        update_data = {
            "category_ids": [new_category.id]
        }
        response = client.put(f"/api/v1/vinyl-records/{sample_vinyl_record.id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["categories"]) == 1
        assert data["categories"][0]["name"] == "New Category"
    
    def test_update_vinyl_record_not_found(self, client):
        """Test updating a non-existent vinyl record."""
        update_data = {"title": "Updated Title"}
        response = client.put("/api/v1/vinyl-records/999", json=update_data)
        
        assert response.status_code == 404
        assert "Vinyl record not found" in response.json()["detail"]
    
    def test_update_vinyl_record_invalid_artist(self, client, sample_vinyl_record):
        """Test updating vinyl record with invalid artist ID."""
        update_data = {"artist_id": 999}
        response = client.put(f"/api/v1/vinyl-records/{sample_vinyl_record.id}", json=update_data)
        
        assert response.status_code == 404
        assert "Artist not found" in response.json()["detail"]
    
    def test_delete_vinyl_record(self, client, sample_vinyl_record):
        """Test deleting a vinyl record."""
        response = client.delete(f"/api/v1/vinyl-records/{sample_vinyl_record.id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify the vinyl record is deleted
        get_response = client.get(f"/api/v1/vinyl-records/{sample_vinyl_record.id}")
        assert get_response.status_code == 404
    
    def test_delete_vinyl_record_not_found(self, client):
        """Test deleting a non-existent vinyl record."""
        response = client.delete("/api/v1/vinyl-records/999")
        
        assert response.status_code == 404
        assert "Vinyl record not found" in response.json()["detail"]

# Clean up test database after all tests
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    """Clean up the test database after all tests are complete."""
    yield
    if os.path.exists("./test_catalog.db"):
        os.remove("./test_catalog.db")
