# 🚀 LinkedIn AutoPoster (AI Agent)

Um agente de Inteligência Artificial de ponta a ponta para ideação, criação, aprovação e publicação automática de conteúdo no LinkedIn.

## 🧠 Sobre o Projeto
Este projeto automatiza a criação de posts para o LinkedIn utilizando IA, mas mantém o controle de qualidade nas mãos do usuário (Human-in-the-Loop). O sistema gera ideias, escreve o texto, cria a imagem e envia uma prévia para o Telegram. Após a aprovação humana, o backend formata o texto para os padrões corporativos e o n8n publica diretamente no LinkedIn.

## 🛠️ Tecnologias Utilizadas
* **Orquestração:** [n8n](https://n8n.io/)
* **Backend:** Python + FastAPI
* **Banco de Dados:** PostgreSQL
* **Infraestrutura:** Docker & Docker Compose
* **Inteligência Artificial:** Google Gemini API (Texto) & Pollinations.ai (Imagens)
* **Mensageria/Aprovação:** Telegram Bot API
* **Integração Externa:** LinkedIn API (OAuth2) + Ngrok (Túnel Webhook)

## ✨ Funcionalidades
- **Ideação Automática:** Geração de tópicos e tendências de conteúdo.
- **Criação de Mídia:** Textos gerados por IA e imagens renderizadas automaticamente.
- **Aprovação via Telegram (Human-in-the-Loop):** O bot envia o post com botões de ação (Aprovar, Refazer, Cancelar).
- **Filtro Corporativo:** Limpeza automática de formatação Markdown (*) e padronização do título em CAIXA ALTA direto na API Python.
- **Publicação Direta:** Integração com a API do LinkedIn via OAuth2.

## 🚀 Como Executar o Projeto

### 1. Pré-requisitos
* Docker e Docker Compose instalados.
* Executável do Ngrok configurado.
* Tokens de API: Telegram Bot, Gemini API e LinkedIn App (Client ID/Secret).

### 2. Configuração do Ambiente
Crie um arquivo `.env` na raiz do projeto com as suas variáveis:
```env
POSTGRES_USER=seu_usuario
POSTGRES_PASSWORD=sua_senha
POSTGRES_DB=seu_banco
WEBHOOK_URL=sua_url_do_ngrok
```

### 3. Subindo os Containers
Execute o comando abaixo no terminal para iniciar o Banco de Dados, a API e o n8n:
```bash
docker compose up -d
```

### 4. Configurando o Ngrok e n8n
1. Inicie o Ngrok apontando para a porta 5678: `ngrok http --domain=seu-dominio.ngrok-free.dev 5678`
2. Acesse o n8n através da URL do Ngrok.
3. Importe os arquivos `workflows.json`.
4. Configure as credenciais do Telegram e o OAuth2 do LinkedIn (usando a URL de redirect).
5. Ative os fluxos!

## 🔒 Segurança
As credenciais sensíveis e bancos de dados estão protegidos e não sobem para o repositório graças ao `.gitignore`.
