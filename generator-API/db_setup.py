from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
from CONSTANTS import DATABASE_URL
from sqlalchemy_utils import database_exists, create_database, drop_database

# Create engine and session factory
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Define base
Base = declarative_base()

# Define models
class ScrapedContent(Base):
    __tablename__ = 'scraped_content'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)

class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, nullable=False)
    embedding = Column(Text, nullable=False)

# Database initializer
def initialize_database():
    inspector = reflection.Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if 'scraped_content' not in existing_tables:
        ScrapedContent.__table__.create(bind=engine)
        print("Table 'scraped_content' created.")

    if 'embeddings' not in existing_tables:
        Embedding.__table__.create(bind=engine)
        print("Table 'embeddings' created.")

# Only initialize when run as a script
if __name__ == "__main__":
    initialize_database()
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import reflection
from CONSTANTS import DATABASE_URL
from sqlalchemy_utils import database_exists, create_database, drop_database

# Create engine and session factory
engine = create_engine(DATABASE_URL)





Session = sessionmaker(bind=engine)
session = Session()

# Define base
Base = declarative_base()

# Define models
class ScrapedContent(Base):
    __tablename__ = 'scraped_content'
    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)

class Embedding(Base):
    __tablename__ = 'embeddings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    content_id = Column(Integer, nullable=False)
    embedding = Column(Text, nullable=False)

# Database initializer
def initialize_database():
    # Drop the database for testing only (remove in production)
    drop_database(engine.url)

    if not database_exists(engine.url):
        create_database(engine.url)
        print("Database created1.")

    inspector = reflection.Inspector.from_engine(engine)
    existing_tables = inspector.get_table_names()

    if 'scraped_content' not in existing_tables:
        ScrapedContent.__table__.create(bind=engine)
        print("Table 'scraped_content' created.")

    if 'embeddings' not in existing_tables:
        Embedding.__table__.create(bind=engine)
        print("Table 'embeddings' created.")

# Only initialize when run as a script
if __name__ == "__main__":
    initialize_database()
