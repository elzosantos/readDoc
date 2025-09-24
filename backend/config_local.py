"""
Configuração local para desenvolvimento.
"""

import os

# Configurações da OpenAI - configure sua chave aqui
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sua_chave_openai_aqui")

# Outras configurações
API_TOKEN = "seu_token_secreto_aqui"
PERSIST_DIRECTORY = "./chromadb"
DEBUG_MODE = False
