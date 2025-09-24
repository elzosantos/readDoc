# Sistema de Busca de Documentos com IA

Este projeto implementa um sistema de busca de documentos usando LangChain, ChromaDB e modelos de IA da OpenAI. O sistema permite carregar documentos e fazer consultas inteligentes sobre seu conteúdo.

## Funcionalidades

- **Carregamento de documentos**: Suporte para arquivos de texto (.txt)
- **Busca inteligente**: Utiliza embeddings e Max Marginal Relevance Search para reduzir redundância
- **API REST**: Interface FastAPI para integração com outras aplicações
- **Interface de linha de comando**: Fácil de usar via terminal
- **Configuração centralizada**: Parâmetros organizados em arquivo de configuração
- **Documentação automática**: Swagger UI integrado

## Estrutura do Projeto

```
readDoc/
├── api.py                 # API FastAPI principal
├── run_api.py             # Script para executar a API
├── document_service.py    # Serviço de documentos
├── models.py              # Modelos Pydantic
├── main.py                # Script CLI (legado)
├── filter_retriever.py    # Retriever personalizado
├── config.py              # Configurações do sistema
├── requirements.txt       # Dependências Python
├── convert.py             # Utilitário de conversão (legado)
├── main2.py               # Script alternativo (legado)
├── chromadb/              # Banco de dados ChromaDB
├── historia.txt           # Arquivo de exemplo
├── História_do_Brasil.pdf # PDF de exemplo
└── README.md              # Este arquivo
```

## Instalação

1. Clone o repositório ou baixe os arquivos
2. Instale as dependências:
   ```bash
   pip install langchain langchain-openai langchain-community langchain-chroma chromadb python-dotenv
   ```

3. Configure suas chaves da OpenAI no arquivo `.env`:
   ```
   OPENAI_API_KEY=sua_chave_aqui
   ```

## Uso

### 🔐 Autenticação

A API utiliza autenticação via **Bearer Token**. Todos os endpoints (exceto `/` e `/health`) requerem autenticação.

#### Níveis de Permissão:

- **Admin**: Acesso completo (leitura, escrita, gerenciamento)
- **User**: Apenas leitura (consultas e status)

#### Como usar:

1. Inclua o header `Authorization` em todas as requisições:
   ```
   Authorization: Bearer seu_token_aqui
   ```

2. Use a documentação interativa em `/docs` para testar com autenticação

### 🚀 API REST (Recomendado)

#### 1. Configurar Autenticação

A API agora requer autenticação via Bearer Token. Configure o token no arquivo `.env`:

```bash
# Copie o arquivo de exemplo
cp env_example.txt .env

# Edite o arquivo .env e configure seu token
API_TOKEN=seu_token_secreto_aqui
```

**Tokens disponíveis para teste:**
- `seu_token_secreto_aqui` (Admin - permissões completas)
- `admin_token_123` (Admin - permissões completas)  
- `user_token_456` (User - apenas leitura)

#### 2. Iniciar a API

```bash
python run_api.py
```

A API estará disponível em:
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

#### 3. Carregar Documentos via API

```bash
curl -X POST "http://localhost:8000/documents/load" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer seu_token_secreto_aqui" \
     -d '{
       "file_path": "historia.txt",
       "chunk_size": 600,
       "chunk_overlap": 200
     }'
```

#### 4. Fazer Consultas via API

```bash
curl -X POST "http://localhost:8000/query" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer seu_token_secreto_aqui" \
     -d '{
       "query": "Quem foi Pedro Alvares Cabral?",
       "lambda_mult": 0.8,
       "k_documents": 4
     }'
```

#### 5. Verificar Status dos Documentos

```bash
curl -X GET "http://localhost:8000/documents/status" \
     -H "Authorization: Bearer seu_token_secreto_aqui"
```

#### 6. Obter Informações do Usuário

```bash
curl -X GET "http://localhost:8000/user/me" \
     -H "Authorization: Bearer seu_token_secreto_aqui"
```

#### 7. Endpoints Administrativos (apenas para admins)

```bash
# Listar tokens válidos
curl -X GET "http://localhost:8000/admin/tokens" \
     -H "Authorization: Bearer seu_token_secreto_aqui"
```

### 💻 Interface de Linha de Comando (Legado)

#### Carregar Documentos

```bash
python main.py --load load --file historia.txt
```

#### Fazer Consultas

```bash
python main.py --load query --task "Sua pergunta aqui"
```

#### Exemplo Completo

```bash
# 1. Carregar documento
python main.py --load load --file historia.txt

# 2. Fazer consulta
python main.py --load query --task "Quem foi Pedro Alvares Cabral?"
```

## Configuração

As configurações do sistema podem ser ajustadas no arquivo `config.py`:

- **EMBEDDING_MODEL**: Modelo de embedding da OpenAI
- **CHAT_MODEL**: Modelo de chat da OpenAI
- **CHUNK_SIZE**: Tamanho dos chunks de texto
- **CHUNK_OVERLAP**: Sobreposição entre chunks
- **LAMBDA_MULT**: Parâmetro para Max Marginal Relevance Search
- **K_DOCUMENTS**: Número de documentos a retornar

## 📡 Endpoints da API

### GET `/`
- **Descrição**: Informações básicas da API
- **Resposta**: Status e versão da API

### GET `/health`
- **Descrição**: Health check da API
- **Resposta**: Status de saúde do sistema

### POST `/documents/load`
- **Descrição**: Carrega um documento no banco de dados
- **Body**:
  ```json
  {
    "file_path": "historia.txt",
    "chunk_size": 600,
    "chunk_overlap": 200
  }
  ```
- **Resposta**: Status do carregamento e número de documentos

### POST `/query`
- **Descrição**: Executa uma consulta nos documentos
- **Body**:
  ```json
  {
    "query": "Sua pergunta aqui",
    "lambda_mult": 0.8,
    "k_documents": 4
  }
  ```
- **Resposta**: Resposta da consulta e documentos utilizados

### GET `/documents/status`
- **Descrição**: Retorna o status dos documentos carregados
- **Resposta**: Informações sobre documentos e banco de dados

## Arquitetura

### API FastAPI
- **api.py**: Aplicação principal FastAPI com endpoints
- **document_service.py**: Serviço de negócio para documentos
- **models.py**: Modelos Pydantic para validação

### DocumentSearchSystem (CLI)
Classe principal que gerencia:
- Carregamento de documentos
- Criação do banco de dados ChromaDB
- Execução de consultas

### RedundantFilterRetriever
Retriever personalizado que:
- Utiliza Max Marginal Relevance Search
- Reduz redundância nos resultados
- Melhora a qualidade das respostas

## Dependências

### Core
- `langchain`: Framework principal para aplicações de IA
- `langchain-openai`: Integração com modelos da OpenAI
- `langchain-community`: Componentes da comunidade
- `langchain-chroma`: Integração com ChromaDB
- `chromadb`: Banco de dados vetorial
- `python-dotenv`: Gerenciamento de variáveis de ambiente

### API
- `fastapi`: Framework web moderno e rápido
- `uvicorn`: Servidor ASGI para FastAPI
- `pydantic`: Validação de dados e modelos

## Exemplos de Uso

### Perguntas sobre História do Brasil

```bash
python main.py --load query --task "Quando foi descoberto o Brasil?"
python main.py --load query --task "Quais foram as principais capitanias hereditárias?"
python main.py --load query --task "Explique o período colonial brasileiro"
```

### Perguntas sobre Documentos Técnicos

```bash
python main.py --load query --task "Resuma os principais pontos do documento"
python main.py --load query --task "Quais são as conclusões apresentadas?"
```

## Troubleshooting

### Erro de API Key
Certifique-se de que a variável `OPENAI_API_KEY` está configurada no arquivo `.env`.

### Erro de Banco de Dados
Se o banco de dados não existir, execute primeiro o modo `load` para carregar documentos.

### Erro de Memória
Para documentos muito grandes, ajuste `CHUNK_SIZE` e `CHUNK_OVERLAP` no arquivo `config.py`.

## Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.
