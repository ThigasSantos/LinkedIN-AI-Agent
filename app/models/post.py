from sqlalchemy import Column, Integer, String, Text, DateTime, CheckConstraint
from sqlalchemy.sql import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.database.connection import Base

# ==========================================
# MODELO SQLALCHEMY (Banco de Dados)
# ==========================================
class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    topic = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    image_path = Column(String(500), nullable=True)
    status = Column(String(50), default="draft", nullable=False)
    
    # Datas
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Métricas com bloqueio contra valores negativos
    likes = Column(Integer, default=0, nullable=False)
    comments = Column(Integer, default=0, nullable=False)
    views = Column(Integer, default=0, nullable=False)

    __table_args__ = (
        CheckConstraint('likes >= 0', name='check_likes_positive'),
        CheckConstraint('comments >= 0', name='check_comments_positive'),
        CheckConstraint('views >= 0', name='check_views_positive'),
    )

# ==========================================
# SCHEMAS PYDANTIC (Validação da API)
# ==========================================
class PostGenerateResponse(BaseModel):
    title: str
    post: str
    image: Optional[str] = None