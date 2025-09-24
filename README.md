# 🤖 Sistema de Busca de Documentos com IA

Sistema completo para carregar documentos e fazer consultas inteligentes usando LangChain, OpenAI e uma interface web moderna.

## 🏗️ Arquitetura

O projeto está organizado em duas partes principais:

```
📁 readDoc/
├── 📁 backend/          # API REST com FastAPI
├── 📁 frontend/         # Interface web com Streamlit
├── 📄 README.md         # Este arquivo
└── 📄 .gitignore        # Arquivos ignorados pelo Git
```

## 🚀 Início Rápido

### 1. Backend (API)

```bash
cd backend
pip install -r requirements.txt
cp env_example.txt .env
# Edite o .env com sua chave OpenAI
python start_api.py
```

**Acesse**: http://localhost:8000/docs

### 2. Frontend (Interface)

```bash
cd frontend
pip install -r requirements_frontend.txt
python run_frontend_simple.py
```

**Acesse**: http://localhost:8501

## 📋 Funcionalidades

### 🔧 Backend
- **API REST** com FastAPI
- **Autenticação** Bearer Token
- **Carregamento** de documentos (PDF, TXT)
- **Busca Inteligente** com LangChain + OpenAI
- **Armazenamento Vetorial** com ChromaDB
- **Documentação** automática com Swagger

### 🎨 Frontend
- **Interface de Chat** moderna e intuitiva
- **Histórico de Conversas** com nomes contextuais
- **Gerenciamento de Arquivos** com upload
- **Configurações** de autenticação
- **Navegação** entre chats e histórico

## 🛠️ Tecnologias

### Backend
- **FastAPI**: Framework web moderno
- **LangChain**: Framework para IA
- **OpenAI**: Modelos de linguagem
- **ChromaDB**: Banco vetorial
- **Uvicorn**: Servidor ASGI

### Frontend
- **Streamlit**: Interface web em Python
- **Requests**: Cliente HTTP
- **Python-dotenv**: Variáveis de ambiente

## 📚 Documentação

- **[Backend README](backend/README.md)**: Documentação completa da API
- **[Frontend README](frontend/README.md)**: Documentação da interface
- **[API Docs](http://localhost:8000/docs)**: Documentação interativa (quando rodando)

## 🔐 Autenticação

O sistema usa Bearer Token para autenticação:

```bash
Authorization: Bearer seu_token_aqui
```

### Tokens Disponíveis
- **Admin**: `seu_token_secreto_aqui` (acesso completo)
- **User**: `user_token_456` (apenas leitura)
- **Admin 2**: `admin_token_123` (acesso completo)

## 🎯 Uso

### 1. Carregar Documentos
```bash
curl -X POST "http://localhost:8000/documents/load" \
  -H "Authorization: Bearer seu_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "documento.pdf"}'
```

### 2. Fazer Consultas
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Authorization: Bearer seu_token_aqui" \
  -H "Content-Type: application/json" \
  -d '{"query": "Qual é o tema principal do documento?"}'
```

### 3. Interface Web
1. Acesse http://localhost:8501
2. Configure o token de autenticação
3. Faça upload de documentos
4. Inicie conversas com a IA

## 🧪 Testes

### Backend
```bash
cd backend
python test_system.py      # Teste completo
python test_chat.py        # Teste de chat
python exemplo_uso.py      # Exemplos de uso
```

### Frontend
1. Inicie backend e frontend
2. Acesse http://localhost:8501
3. Teste todas as funcionalidades da interface

## 📁 Estrutura Detalhada

```
📁 readDoc/
├── 📁 backend/
│   ├── 📄 api.py                    # Aplicação FastAPI
│   ├── 📄 auth.py                   # Sistema de autenticação
│   ├── 📄 config.py                 # Configurações
│   ├── 📄 document_service.py       # Serviço de documentos
│   ├── 📄 models.py                 # Modelos Pydantic
│   ├── 📄 run_api.py                # Script de execução
│   ├── 📄 start_api.py              # Inicialização
│   ├── 📄 requirements.txt          # Dependências
│   ├── 📄 env_example.txt           # Exemplo de configuração
│   ├── 📄 test_*.py                 # Scripts de teste
│   ├── 📄 exemplo_uso.py            # Exemplos
│   ├── 📄 *.md                      # Documentação
│   └── 📄 README.md                 # Documentação do backend
├── 📁 frontend/
│   ├── 📄 streamlit_app.py          # Aplicação Streamlit
│   ├── 📄 run_frontend.py           # Script de execução
│   ├── 📄 requirements_frontend.txt # Dependências
│   ├── 📁 .streamlit/               # Configurações
│   └── 📄 README.md                 # Documentação do frontend
├── 📄 README.md                     # Este arquivo
└── 📄 .gitignore                    # Arquivos ignorados
```

## 🔧 Configuração

### Variáveis de Ambiente

Crie um arquivo `.env` na pasta `backend/`:

```env
API_TOKEN=seu_token_secreto_aqui
OPENAI_API_KEY=sua_chave_openai_aqui
PERSIST_DIRECTORY=./chromadb
```

### Dependências

**Backend**:
```bash
cd backend
pip install -r requirements.txt
```

**Frontend**:
```bash
cd frontend
pip install -r requirements_frontend.txt
```

## 🚀 Deploy

### Desenvolvimento Local

1. **Backend**:
   ```bash
   cd backend
   python start_api.py
   ```

2. **Frontend**:
   ```bash
   cd frontend
   python run_frontend_simple.py
   ```

### Produção

1. Configure variáveis de ambiente
2. Use servidores de produção (Gunicorn, Nginx)
3. Configure HTTPS e domínio

## 🐛 Solução de Problemas

### Erro de Porta em Uso
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f python
```

### Erro de Autenticação
- Verifique o token no header `Authorization`
- Confirme se o token está correto

### Erro de OpenAI
- Verifique a chave da API no arquivo `.env`
- Confirme se há créditos disponíveis

## 📈 Monitoramento

### Backend
- Logs detalhados no console
- Métricas de requisições
- Status de saúde em `/health`

### Frontend
- Logs do Streamlit
- Teste de conectividade
- Status da API

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

- **Issues**: Abra uma issue no GitHub
- **Documentação**: Consulte os READMEs específicos
- **API Docs**: http://localhost:8000/docs (quando rodando)

## 🎉 Funcionalidades Implementadas

### ✅ Backend
- [x] API REST com FastAPI
- [x] Autenticação Bearer Token
- [x] Carregamento de documentos
- [x] Busca inteligente com IA
- [x] Armazenamento vetorial
- [x] Documentação automática
- [x] Testes automatizados

### ✅ Frontend
- [x] Interface de chat moderna
- [x] Histórico com nomes contextuais
- [x] Gerenciamento de arquivos
- [x] Configurações de autenticação
- [x] Navegação intuitiva
- [x] Design responsivo

### ✅ Sistema
- [x] Separação frontend/backend
- [x] Documentação completa
- [x] Scripts de execução
- [x] Testes de integração
- [x] Configuração flexível

---

**Desenvolvido com ❤️ usando FastAPI, Streamlit, LangChain e OpenAI**