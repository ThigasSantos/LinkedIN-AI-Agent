import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from app.models.post import PostGenerateResponse

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def load_prompt() -> str:
    """Lê o conteúdo do arquivo markdown com as instruções do agente."""
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompts', 'post_prompt.md')
    with open(prompt_path, 'r', encoding='utf-8') as file:
        return file.read()

def generate_linkedin_post(topic: str) -> PostGenerateResponse:
    """
    Envia o tema para o Gemini usando o alias oficial gratuito mais recente 
    e retorna o objeto Pydantic estritamente validado.
    """
    system_prompt = load_prompt()
    
    # O alias que o Google mantém sempre atualizado e com cota gratuita
    active_model = 'gemini-flash-latest'
    print(f"Gerando post com o modelo gratuito: {active_model}")

    response = client.models.generate_content(
        model=active_model,
        contents=f"Crie um post no LinkedIn sobre o seguinte tema: {topic}",
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            response_schema=PostGenerateResponse,
        ),
    )

    return PostGenerateResponse.model_validate_json(response.text)