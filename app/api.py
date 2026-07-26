import os

from fastapi import FastAPI, Depends, HTTPException 
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.connection import engine, Base, get_db
from app.models.post import Post, PostGenerateResponse, IdeiaTrend
from app.services.gemini import generate_linkedin_post
from app.services.flux import generate_image
from app.services.trends import capture_and_generate_trend 

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(title="LinkedIn AI Agent")

# 1. Encontra a raiz do projeto 
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
    
    # 3. Salva no banco de dados 
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
    
    # 4. Retorna para a interface 
    return generated_content

# ---  ENDPOINT DE TRENDS  ---

@app.post("/trends/capture", summary="Captura notícias do dia e gera uma ideia de post")
def capture_trends(db: Session = Depends(get_db)):
    try:
        nova_ideia = capture_and_generate_trend(db)
        return {
            "message": "Nova ideia de trend capturada com sucesso!",
            "noticia_base": nova_ideia.titulo_noticia,
            "link_referencia": nova_ideia.link_noticia,
            "ideia_gerada": nova_ideia.tema_gerado
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/trends/pending", summary="Busca a ideia mais antiga que ainda está pendente")
def get_pending_trend(db: Session = Depends(get_db)):
    # Busca o primeiro registro onde o status é 'pendente', ordenado pela data mais antiga
    ideia = db.query(IdeiaTrend).filter(IdeiaTrend.status == "pendente").order_by(IdeiaTrend.data_captura.asc()).first()
    
    if not ideia:
        raise HTTPException(status_code=404, detail="Nenhuma ideia pendente encontrada na fila.")
        
    return {
        "id": ideia.id,
        "topic": ideia.tema_gerado,
        "noticia_base": ideia.titulo_noticia
    }

@app.get("/trends/{ideia_id}", summary="Busca uma ideia específica pelo ID")
def get_trend_by_id(ideia_id: int, db: Session = Depends(get_db)):
    ideia = db.query(IdeiaTrend).filter(IdeiaTrend.id == ideia_id).first()
    
    if not ideia:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
        
    return {
        "id": ideia.id,
        "topic": ideia.tema_gerado,
        "noticia_base": ideia.titulo_noticia
    }

@app.get("/posts/latest", summary="Busca o post mais recente de um tópico específico")
def get_latest_post_by_topic(topic: str, db: Session = Depends(get_db)):
    # Busca o último post gerado com esse tópico
    post = db.query(Post).filter(Post.topic == topic).order_by(Post.id.desc()).first()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post não encontrado para este tópico")
        
    # Reconstrói a URL da imagem para o n8n conseguir baixar
    image_url = None
    if post.image_path:
        filename = os.path.basename(post.image_path)
        image_url = f"http://api:8000/images/{filename}"
        
    return {
        "title": post.title,
        "content": post.content,
        "image_url": image_url
    }

class UpdateStatusRequest(BaseModel):
    status: str

@app.put("/trends/{ideia_id}/status", summary="Atualiza o status de uma ideia (ex: usado, descartado)")
def update_trend_status(ideia_id: int, request: UpdateStatusRequest, db: Session = Depends(get_db)):
    ideia = db.query(IdeiaTrend).filter(IdeiaTrend.id == ideia_id).first()
    
    if not ideia:
        raise HTTPException(status_code=404, detail="Ideia não encontrada.")
        
    ideia.status = request.status
    db.commit()
    
    return {"message": f"Status da ideia {ideia_id} atualizado para '{request.status}'"}