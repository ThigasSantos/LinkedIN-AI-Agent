import os
import uuid
import requests
import urllib.parse

def generate_image(prompt: str) -> str:
    """
    Envia o prompt para a API gratuita do Pollinations.ai,
    recebe a imagem e salva localmente com um nome único.
    """
    print(f"Gerando imagem via Pollinations.ai para o prompt: {prompt}")
    
    # Prepara o texto para ser seguro de usar em uma URL
    encoded_prompt = urllib.parse.quote(prompt)
    
    # Endpoint mágico: não precisa de auth, já vem com tamanho 1024x1024 e sem logo
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true"
    
    # Fazemos a requisição e baixamos a imagem
    response = requests.get(url)
    
    if response.status_code != 200:
        raise Exception(f"Erro na geração de imagem: Status {response.status_code}")
    
    # Garante que a pasta images existe
    images_dir = os.path.join(os.getcwd(), "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Gera o nome final
    filename = f"post_{uuid.uuid4().hex[:8]}.jpg"
    filepath = os.path.join(images_dir, filename)
    
    # Salva o arquivo no disco
    with open(filepath, "wb") as f:
        f.write(response.content)
        
    print(f"Imagem salva com sucesso em: {filepath}")
    return filepath