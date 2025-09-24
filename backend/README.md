# 🚀 Backend - Sistema de Busca de Documentos com IA

API REST desenvolvida com FastAPI para carregar documentos e fazer consultas inteligentes usando LangChain e OpenAI.

## 📋 Funcionalidades

- **Carregamento de Documentos**: Suporte a PDF, TXT e outros formatos
- **Busca Inteligente**: Consultas usando IA com LangChain e OpenAI
- **Autenticação**: Sistema de Bearer Token com diferentes níveis de acesso
- **Armazenamento Vetorial**: ChromaDB para busca semântica eficiente
- **API REST**: Endpoints documentados com Swagger UI

## 🛠️ Tecnologias

- **FastAPI**: Framework web moderno e rápido
- **LangChain**: Framework para aplicações com IA
- **OpenAI**: Modelos de linguagem para processamento
- **ChromaDB**: Banco de dados vetorial
- **Uvicorn**: Servidor ASGI
- **Pydantic**: Validação de dados

## 📦 Instalação

### 1. Pré-requisitos

- Python 3.8+
- Chave da API OpenAI

### 2. Instalar Dependências

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configuração

Copie o arquivo de exemplo e configure suas variáveis:

```bash
cp env_example.txt .env
```

Edite o arquivo `.env`:

```env
API_TOKEN=seu_token_secreto_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
PERSIST_DIRECTORY=./chromadb
```

## 🚀 Execução

### Desenvolvimento (com reload automático)

```bash
python run_api.py
```

### Produção (sem reload)

```bash
python run_api_simple.py
```

### Inicialização Simples

```bash
python start_api.py
```

## 📚 Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **API**: http://localhost:8000

## 🔐 Autenticação

A API utiliza autenticação Bearer Token. Inclua o token no header:

```
Authorization: Bearer seu_token_aqui
```

### Tokens Disponíveis

- **Admin Token**: `seu_token_secreto_aqui` (permissões completas)
- **User Token**: `user_token_456` (apenas leitura)
- **Admin Token 2**: `admin_token_123` (permissões completas)

### Permissões

- **Leitura**: Consultar documentos e verificar status
- **Escrita**: Carregar novos documentos
- **Admin**: Acesso completo + gerenciamento de tokens

## 📡 Endpoints

### Autenticação

- `GET /user/me` - Informações do usuário atual
- `GET /admin/tokens` - Listar tokens válidos (admin)

### Documentos

- `POST /documents/load` - Carregar documento
- `GET /documents/status` - Status dos documentos carregados

### Consultas

- `POST /query` - Fazer consulta nos documentos

### Sistema

- `GET /health` - Status da API

## 🧪 Testes

### Teste do Sistema Completo

```bash
python test_system.py
```

### Teste de Chat

```bash
python test_chat.py
```

### Teste de Funcionalidades

```bash
python test_chat_features.py
```

### Exemplo de Uso

```bash
python exemplo_uso.py
```

## 📁 Estrutura do Projeto

```
backend/
├── api.py                 # Aplicação FastAPI principal
├── auth.py                # Sistema de autenticação
├── config.py              # Configurações
├── document_service.py    # Serviço de documentos
├── filter_retriever.py    # Filtros de busca
├── models.py              # Modelos Pydantic
├── run_api.py             # Script de execução com reload
├── run_api_simple.py      # Script de execução simples
├── start_api.py           # Script de inicialização
├── requirements.txt       # Dependências Python
├── env_example.txt        # Exemplo de variáveis de ambiente
├── test_system.py         # Testes do sistema
├── test_chat.py           # Testes de chat
├── test_chat_features.py  # Testes de funcionalidades
├── exemplo_uso.py         # Exemplos de uso
├── DEMO.md                # Demonstração completa
├── INSTRUCOES_RAPIDAS.md  # Instruções rápidas
├── STATUS_FINAL.md        # Status final do projeto
└── README.md              # Este arquivo
```

## 🔧 Configurações Avançadas

### Parâmetros de Busca

- `lambda_mult`: Controle de diversidade (0.0-1.0)
- `k_documents`: Número de documentos retornados
- `chunk_size`: Tamanho dos fragmentos de texto
- `chunk_overlap`: Sobreposição entre fragmentos

### Modelos OpenAI

- **Chat Model**: `gpt-4o-mini`
- **Embedding Model**: `text-embedding-3-small`
- **Temperatura**: 0.7

## 🐛 Solução de Problemas

### Erro de Porta em Uso

```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f python
```

### Erro de Autenticação

Verifique se o token está correto no header `Authorization`.

### Erro de OpenAI

Confirme se a chave da API está configurada corretamente no `.env`.

## 📈 Monitoramento

A API inclui logs detalhados para monitoramento:

- Requisições HTTP
- Erros de autenticação
- Status de carregamento de documentos
- Consultas processadas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para suporte e dúvidas:

- Abra uma issue no GitHub
- Consulte a documentação da API em `/docs`
- Verifique os logs do servidor

---

**Desenvolvido com ❤️ usando FastAPI, LangChain e OpenAI**
