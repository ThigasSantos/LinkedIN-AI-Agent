import feedparser
import os
from google import genai
from sqlalchemy.orm import Session
from app.models.post import IdeiaTrend  

def capture_and_generate_trend(db: Session):
    """
    Pipeline ETL para captura de tendências e geração de tópicos via LLM.
    """
    print("Iniciando busca de tendências no Google News...")
    
    # 1. EXTRACT (Extração): Consome o feed RSS gratuito do Google News (Assuntos: IA e Dados)
    url = "https://news.google.com/rss/search?q=Inteligência+Artificial+OR+Análise+de+Dados&hl=pt-BR&gl=BR&ceid=BR:pt-419"
    feed = feedparser.parse(url)
    
    if not feed.entries:
        raise Exception("Nenhuma notícia encontrada no feed.")
        
    # Pegamos as 3 notícias mais relevantes do momento
    top_news = feed.entries[:3]
    contexto_noticias = "\n".join([f"- {news.title}" for news in top_news])
    print(f"Notícias capturadas:\n{contexto_noticias}")
    
    # 2. TRANSFORM (Transformação): Pedimos ao Gemini para criar o insight
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    prompt = f"""
    Você é um estrategista de conteúdo sênior para o LinkedIn, especializado em dados e tecnologia.
    Aqui estão as manchetes mais quentes de hoje no Brasil:
    
    {contexto_noticias}
    
    Sua missão: Escolha a notícia mais interessante e crie APENAS UM tópico (uma ideia central de post) 
    que conecte essa notícia com a carreira de dados, engenharia de software ou IA.
    
    O tópico deve ser provocativo e engajador, servindo como base para um post futuro.
    Regra: Não escreva o post inteiro! Escreva apenas o tema central (1 a 2 frases no máximo).
    """
    
    print("Enviando para o Gemini processar...")
    response = client.models.generate_content(
        model='gemini-flash-latest',
        contents=prompt
    )
    tema_gerado = response.text.strip()
    
    noticia_principal = top_news[0]
    
    # 3. LOAD (Carga): Salva no banco de dados
    print("Salvando nova ideia no PostgreSQL...")
    nova_ideia = IdeiaTrend(
        titulo_noticia=noticia_principal.title,
        link_noticia=noticia_principal.link,
        tema_gerado=tema_gerado,
        status="pendente"
    )
    
    db.add(nova_ideia)
    db.commit()
    db.refresh(nova_ideia)
    
    print(f"Ideia salva com sucesso: {tema_gerado}")
    return nova_ideia