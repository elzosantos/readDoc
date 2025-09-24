"""
Arquivo de configuração para o sistema de busca de documentos.
"""

# Configurações do modelo de embedding
EMBEDDING_MODEL = "text-embedding-3-large"

# Configurações do modelo de chat
CHAT_MODEL = "gpt-4o-mini"
MODEL_NAME = "gpt-4o-mini"
TEMPERATURE = 0.7

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

 