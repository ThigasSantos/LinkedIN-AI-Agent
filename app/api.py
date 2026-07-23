from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import engine, Base, get_db
from app.models.post import Post, PostGenerateResponse
from app.services.gemini import generate_linkedin_post
from app.services.flux import generate_image

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn AI Agent")

class GenerateRequest(BaseModel):
    topic: str

@app.get("/")
def read_root():
    return {"status": "ok", "message": "API rodando perfeitamente!"}

@app.post("/generate", response_model=PostGenerateResponse)
def generate_post(request: GenerateRequest, db: Session = Depends(get_db)):
    # 1. Gemini gera o texto e o prompt da imagem
    generated_content = generate_linkedin_post(request.topic)
    
    # 2. FLUX gera a imagem com base no prompt em inglês criado pelo Gemini
    image_path = None
    if generated_content.image:
        try:
            image_path = generate_image(generated_content.image)
            # Substituímos o prompt pelo caminho do arquivo salvo para retornar no JSON
            generated_content.image = image_path
        except Exception as e:
            print(f"Aviso: Falha ao gerar imagem - {e}")
    
    # 3. Salva no banco de dados (agora com o caminho da imagem)
    novo_post = Post(
        title=generated_content.title,
        topic=request.topic,
        content=generated_content.post,
        image_path=image_path,
        status="draft"
    )
    db.add(novo_post)
    db.commit()
    db.refresh(novo_post)
    
    # 4. Retorna para a interface (n8n no futuro)
    return generated_content