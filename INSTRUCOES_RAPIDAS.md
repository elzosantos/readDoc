# 🚀 Instruções Rápidas - Sistema Reorganizado

## 📁 Estrutura do Projeto

```
📁 readDoc/
├── 📁 backend/          # API REST (FastAPI)
├── 📁 frontend/         # Interface Web (Streamlit)
├── 📄 start_backend.py  # Iniciar apenas backend
├── 📄 start_frontend.py # Iniciar apenas frontend
├── 📄 start_full_system.py # Iniciar sistema completo
└── 📄 README.md         # Documentação principal
```

## ⚡ Início Rápido

### 1. Configuração Inicial

```bash
# Backend
cd backend
pip install -r requirements.txt
cp env_example.txt .env
# Edite o .env com sua chave OpenAI

# Frontend
cd ../frontend
pip install -r requirements_frontend.txt
```

### 2. Executar Sistema

#### Opção 1: Sistema Completo (Recomendado)
```bash
python start_full_system.py
```

#### Opção 2: Separadamente
```bash
# Terminal 1 - Backend
python start_backend.py

# Terminal 2 - Frontend
python start_frontend.py
```

### 3. Acessar

- **Frontend**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API**: http://localhost:8000

## 🔧 Comandos Úteis

### Testar Sistema
```bash
python test_reorganized_system.py
```

### Parar Sistema
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f python
```

### Verificar Status
```bash
# Testar API
curl http://localhost:8000/health

# Testar Frontend
curl http://localhost:8501
```

## 📚 Documentação

- **[README Principal](README.md)**: Visão geral do projeto
- **[Backend README](backend/README.md)**: Documentação da API
- **[Frontend README](frontend/README.md)**: Documentação da interface

## 🔐 Autenticação

Token padrão: `seu_token_secreto_aqui`

Configure no frontend ou use nos headers:
```
Authorization: Bearer seu_token_secreto_aqui
```

## 🎯 Funcionalidades

### Backend
- ✅ API REST com FastAPI
- ✅ Autenticação Bearer Token
- ✅ Carregamento de documentos
- ✅ Busca inteligente com IA
- ✅ Armazenamento vetorial

### Frontend
- ✅ Interface de chat moderna
- ✅ Histórico com nomes contextuais
- ✅ Gerenciamento de arquivos
- ✅ Configurações de autenticação
- ✅ Navegação intuitiva

## 🐛 Solução de Problemas

### Erro de Porta
```bash
taskkill /f /im python.exe
```

### Erro de Dependências
```bash
# Backend
cd backend && pip install -r requirements.txt

# Frontend
cd frontend && pip install -r requirements_frontend.txt
```

### Erro de Configuração
- Verifique o arquivo `.env` no backend
- Confirme a chave OpenAI
- Teste a conectividade

## 📞 Suporte

- Consulte os READMEs específicos
- Verifique os logs do console
- Teste com `python test_reorganized_system.py`

---

**Sistema reorganizado e funcionando! 🎉**