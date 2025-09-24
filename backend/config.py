"""
Arquivo de configuração para o sistema de busca de documentos.
"""

import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações do modelo de embedding
EMBEDDING_MODEL = "text-embedding-3-large"

# Configurações do modelo de chat
CHAT_MODEL = "gpt-4o-mini"
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.7

# Configurações da OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Verificar se a API key está configurada
if not OPENAI_API_KEY or OPENAI_API_KEY == "sua_chave_openai_aqui":
    print("⚠️ AVISO: OPENAI_API_KEY não está configurada!")
    print("Configure a variável de ambiente OPENAI_API_KEY ou edite o arquivo config.py")
    OPENAI_API_KEY = None

# Configurações do text splitter
CHUNK_SIZE = 600
CHUNK_OVERLAP = 200
SEPARATOR = "\n"

# Configurações do retriever
LAMBDA_MULT = 0.8
K_DOCUMENTS = 4

# Configurações do banco de dados
PERSIST_DIRECTORY = "./chromadb"

# Configurações padrão dos argumentos
DEFAULT_LOAD_MODE = "query"
DEFAULT_FILE = "historia.txt"
DEFAULT_QUERY = "Quem foi Pedro Alvares Cabral?"

# Configurações de debug
DEBUG_MODE = False
 