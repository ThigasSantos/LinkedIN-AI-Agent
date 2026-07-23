import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Pegando a URL do .env
DATABASE_URL = os.getenv("DATABASE_URL")

# Engine do SQLAlchemy
engine = create_engine(DATABASE_URL)

# Criando a fábrica de sessões
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos do banco
Base = declarative_base()

# Dependência para injetar a sessão do banco nas rotas do FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()