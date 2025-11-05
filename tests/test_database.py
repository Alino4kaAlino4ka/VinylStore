import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, Author, Category, Audiobook

# Use a separate database file for testing
TEST_DATABASE_URL = "sqlite:///./test_audio_store.db"

engine = create_engine(
    TEST_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(
    autocommit=False, 
    autoflush=False, 
    bind=engine
)

Base.metadata.create_all(bind=engine)

def get_test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

class TestDatabase(unittest.TestCase):
    
    def setUp(self):
        """Set up a new database session for each test."""
        Base.metadata.create_all(bind=engine)
        self.db = next(get_test_db())

    def tearDown(self):
        """Tear down the database session and clean up the database file."""
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    @classmethod
    def tearDownClass(cls):
        """Remove the test database file after all tests are done."""
        # Dispose of the engine's connection pool to release file locks
        engine.dispose()
        if os.path.exists("./test_audio_store.db"):
            os.remove("./test_audio_store.db")

    def test_01_create_author(self):
        """Test creating a new author and adding it to the database."""
        new_author = Author(name="J.K. Rowling")
        self.db.add(new_author)
        self.db.commit()
        self.db.refresh(new_author)

        author_from_db = self.db.query(Author).filter(Author.id == new_author.id).first()
        
        self.assertIsNotNone(author_from_db)
        self.assertEqual(author_from_db.name, "J.K. Rowling")

    def test_02_create_audiobook(self):
        """Test creating an audiobook with a relationship to an author."""
        author = Author(name="George R.R. Martin")
        self.db.add(author)
        self.db.commit()

        new_audiobook = Audiobook(
            title="A Game of Thrones",
            description="The first book in A Song of Ice and Fire.",
            price=29.99,
            author_id=author.id
        )
        self.db.add(new_audiobook)
        self.db.commit()
        self.db.refresh(new_audiobook)

        audiobook_from_db = self.db.query(Audiobook).filter(Audiobook.id == new_audiobook.id).first()

        self.assertIsNotNone(audiobook_from_db)
        self.assertEqual(audiobook_from_db.title, "A Game of Thrones")
        self.assertEqual(audiobook_from_db.author.name, "George R.R. Martin")

    def test_03_many_to_many_relationship(self):
        """Test the many-to-many relationship between Audiobook and Category."""
        author = Author(name="J.R.R. Tolkien")
        category1 = Category(name="Fantasy")
        category2 = Category(name="Adventure")
        
        self.db.add(author)
        self.db.add(category1)
        self.db.add(category2)
        self.db.commit()

        new_audiobook = Audiobook(
            title="The Hobbit",
            description="An unexpected journey.",
            price=19.99,
            author_id=author.id,
            categories=[category1, category2]
        )
        self.db.add(new_audiobook)
        self.db.commit()
        self.db.refresh(new_audiobook)

        audiobook_from_db = self.db.query(Audiobook).filter(Audiobook.id == new_audiobook.id).first()
        
        self.assertIsNotNone(audiobook_from_db)
        self.assertEqual(len(audiobook_from_db.categories), 2)
        self.assertIn("Fantasy", [cat.name for cat in audiobook_from_db.categories])
        self.assertIn("Adventure", [cat.name for cat in audiobook_from_db.categories])

if __name__ == "__main__":
    unittest.main()
