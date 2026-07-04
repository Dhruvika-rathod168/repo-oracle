from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid

SQLALCHEMY_DATABASE_URL = "sqlite:///./codebaserag.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── User model ─────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id             = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email          = Column(String, unique=True, index=True, nullable=False)
    name           = Column(String, nullable=True)
    password_hash  = Column(String, nullable=True)  # None for Google OAuth users
    google_id      = Column(String, nullable=True)
    avatar_url     = Column(String, nullable=True)
    is_google_user = Column(Boolean, default=False)

# Create tables
Base.metadata.create_all(bind=engine)

# ── Dependency ─────────────────────────────────────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()