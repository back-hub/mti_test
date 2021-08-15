from sqlalchemy import create_engine
from sqlalchemy.ext import declarative
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker



# Для локального подключения
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123456@localhost/blogs"


# Для подключения с докера
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:1@db:5432/blog"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False,autoflush=False, bind=engine)
Base = declarative_base()

data = SessionLocal()
