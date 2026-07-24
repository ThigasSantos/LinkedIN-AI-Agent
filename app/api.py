import os

from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import engine, Base, get_db
from app.models.post import Post, PostGenerateResponse
from app.services.gemini import generate_linkedin_post
from app.services.flux import generate_image

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn AI Agent")

# 1. Encontra a raiz do projeto (uma pasta acima de app/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(BASE_DIR, "images")

# 2. Garante que a pasta existe na raiz e a expõe na rota /images
os.makedirs(IMAGES_DIR, exist_ok=True)
app.mount("/images", StaticFiles(directory=IMAGES_DIR), name="images")

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
            # Salva no disco
            image_path = generate_image(generated_content.image)
            
            # Extrai o nome do arquivo e monta a URL interna
            filename = os.path.basename(image_path)
            image_url = f"http://api:8000/images/{filename}"
            
            # Devolve a URL para o n8n em vez do caminho do disco
            generated_content.image = image_url
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