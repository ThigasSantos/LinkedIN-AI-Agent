from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import engine, Base, get_db
from app.models.post import Post, PostGenerateResponse
from app.services.gemini import generate_linkedin_post

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Personal Branding AI")

class GenerateRequest(BaseModel):
    topic: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API rodando perfeitamente!"}

@app.post("/generate", response_model=PostGenerateResponse)
def generate_post(request: GenerateRequest, db: Session = Depends(get_db)):
    """
    Endpoint que o n8n irá chamar para gerar um novo conteúdo.
    """
    # 1. Chama o agente da OpenAI para gerar o conteúdo
    generated_content = generate_linkedin_post(request.topic)
    
    # 2. Salva o rascunho no banco de dados PostgreSQL
    novo_post = Post(
        title=generated_content.title,
        topic=request.topic,
        content=generated_content.post,
        image_path=None,  # Será preenchido na Fase 2 (Geração de Imagem)
        status="draft"
    )
    db.add(novo_post)
    db.commit()
    db.refresh(novo_post) # Atualiza o objeto com o ID gerado pelo banco
    
    # 3. Retorna o JSON validado
    return generated_content