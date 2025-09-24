# 🎨 Frontend - Interface de Chat com IA

Interface web moderna desenvolvida com Streamlit para interagir com o sistema de busca de documentos com IA.

## ✨ Funcionalidades

- **Chat Inteligente**: Interface de conversação com IA
- **Histórico de Chats**: Sistema de histórico com nomes contextuais
- **Gerenciamento de Arquivos**: Upload e visualização de documentos
- **Autenticação**: Configuração de tokens de acesso
- **Interface Responsiva**: Design moderno e intuitivo
- **Navegação Intuitiva**: Menu lateral com histórico e configurações

## 🎯 Características Principais

### 💬 Sistema de Chat
- **Novo Chat**: Botão para iniciar nova conversa
- **Histórico Contextual**: Nomes automáticos baseados no conteúdo
- **Navegação**: Alternar entre chat atual e histórico
- **Documentos Utilizados**: Visualização dos trechos consultados

### 📁 Gerenciamento de Arquivos
- **Status dos Documentos**: Informações sobre documentos carregados
- **Upload de Arquivos**: Carregar novos documentos
- **Visualização**: Lista de arquivos disponíveis

### ⚙️ Configurações
- **Autenticação**: Configuração de tokens
- **Teste de Conexão**: Verificação da API
- **Informações do Sistema**: Status e métricas

## 🛠️ Tecnologias

- **Streamlit**: Framework para aplicações web em Python
- **Requests**: Cliente HTTP para comunicação com API
- **Python-dotenv**: Gerenciamento de variáveis de ambiente

## 📦 Instalação

### 1. Pré-requisitos

- Python 3.8+
- Backend da API rodando (http://localhost:8000)

### 2. Instalar Dependências

```bash
cd frontend
pip install -r requirements_frontend.txt
```

### 3. Configuração

O frontend se conecta automaticamente com a API backend. Certifique-se de que:

- A API está rodando em `http://localhost:8000`
- O token de autenticação está configurado

## 🚀 Execução

### Desenvolvimento

```bash
python run_frontend.py
```

### Produção

```bash
python run_frontend_simple.py
```

### Acesso

Após iniciar, acesse: **http://localhost:8501**

## 🎨 Interface

### 📱 Layout Principal

```
┌─────────────────────────────────────────────────────────┐
│                    🤖 LLMChat                          │
├─────────────────────────────────────────────────────────┤
│ Sidebar                    │ Área Principal            │
│ ┌─────────────────────────┐ │ ┌─────────────────────────┐ │
│ │ 🔐 Autenticação         │ │ │ 💬 Chat com IA          │ │
│ │ 📋 Navegação            │ │ │                         │ │
│ │ 🆕 Novo Chat            │ │ │ [Área de conversação]   │ │
│ │ 💬 Chat                 │ │ │                         │ │
│ │ 📁 Gerenciar Arquivos   │ │ │ [Input de mensagem]     │ │
│ │ ⚙️ Configurações        │ │ │                         │ │
│ │                         │ │ │                         │ │
│ │ 📚 Histórico de Chats   │ │ │                         │ │
│ │ [Lista de chats]        │ │ │                         │ │
│ │                         │ │ │                         │ │
│ │ ℹ️ Sistema              │ │ │                         │ │
│ │ [Status e métricas]     │ │ │                         │ │
│ └─────────────────────────┘ │ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 🔄 Fluxo de Navegação

1. **Novo Chat**: Salva chat atual no histórico e inicia nova conversa
2. **Histórico**: Visualiza conversas anteriores com nomes contextuais
3. **Chat Atual**: Retorna à conversa em andamento
4. **Gerenciar Arquivos**: Upload e status de documentos
5. **Configurações**: Token e informações do sistema

## 🎯 Funcionalidades Detalhadas

### 💬 Sistema de Chat

#### Novo Chat
- Salva automaticamente o chat atual no histórico
- Gera nome baseado na primeira pergunta
- Limita nomes a 15 caracteres
- Inicia nova conversa limpa

#### Histórico Contextual
- **Nomes Inteligentes**: Baseados em palavras-chave da consulta
- **Palavras-chave**: Brasil, História, Capital, Independência, etc.
- **Fallback**: Primeiras palavras da pergunta se não houver palavra-chave
- **Navegação**: Clique para visualizar chat anterior

#### Chat Atual
- Conversa em tempo real
- Exibe documentos utilizados
- Salva automaticamente no histórico ao criar novo chat

### 📁 Gerenciamento de Arquivos

#### Status dos Documentos
- Contador de documentos carregados
- Data do último carregamento
- Botão de atualização

#### Upload de Arquivos
- Suporte a múltiplos formatos
- Feedback visual do progresso
- Validação de arquivos

### ⚙️ Configurações

#### Autenticação
- Campo para token Bearer
- Teste de conexão com API
- Validação em tempo real

#### Sistema
- Status da conexão
- Métricas de uso
- Informações de versão

## 🎨 Personalização

### Tema

O frontend usa um tema personalizado configurado em `.streamlit/config.toml`:

```toml
[theme]
base="light"
primaryColor="#6D28D9"
backgroundColor="#F9FAFB"
secondaryBackgroundColor="#F3F4F6"
textColor="#1F2937"
font="sans serif"
```

### Cores

- **Primária**: Roxo (#6D28D9)
- **Fundo**: Cinza claro (#F9FAFB)
- **Secundário**: Cinza médio (#F3F4F6)
- **Texto**: Cinza escuro (#1F2937)

## 📁 Estrutura do Projeto

```
frontend/
├── streamlit_app.py           # Aplicação principal Streamlit
├── run_frontend.py            # Script de execução com reload
├── run_frontend_simple.py     # Script de execução simples
├── requirements_frontend.txt  # Dependências do frontend
├── .streamlit/                # Configurações do Streamlit
│   └── config.toml           # Tema e configurações
└── README.md                 # Este arquivo
```

## 🔧 Configurações

### Porta do Servidor

Por padrão, o frontend roda na porta 8501. Para alterar:

```bash
streamlit run streamlit_app.py --server.port 8502
```

### URL da API

Para conectar a uma API em outro endereço, edite `streamlit_app.py`:

```python
API_BASE_URL = "http://seu-servidor:8000"
```

## 🧪 Testes

### Teste Manual

1. Inicie o backend: `cd ../backend && python start_api.py`
2. Inicie o frontend: `python run_frontend_simple.py`
3. Acesse: http://localhost:8501
4. Teste as funcionalidades:
   - Novo Chat
   - Histórico
   - Upload de arquivos
   - Configurações

### Teste de Conectividade

O frontend inclui botão "Testar Conexão" que verifica:
- Conectividade com a API
- Validação do token
- Status dos serviços

## 🐛 Solução de Problemas

### Erro de Conexão

- Verifique se o backend está rodando
- Confirme a URL da API
- Teste o token de autenticação

### Erro de Porta

```bash
# Windows
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8501 | xargs kill -9
```

### Erro de Dependências

```bash
pip install --upgrade -r requirements_frontend.txt
```

## 🚀 Deploy

### Local

```bash
python run_frontend_simple.py
```

### Docker (Exemplo)

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements_frontend.txt .
RUN pip install -r requirements_frontend.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true"]
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT.

## 📞 Suporte

Para suporte e dúvidas:

- Abra uma issue no GitHub
- Consulte a documentação do backend
- Verifique os logs do Streamlit

---

**Desenvolvido com ❤️ usando Streamlit**
