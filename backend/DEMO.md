# 🚀 Demonstração do Sistema LLMChat

## 📋 Visão Geral

Este sistema combina uma **API FastAPI** com autenticação Bearer Token e uma **interface web Streamlit** moderna para busca inteligente de documentos usando IA.

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   Banco de      │
│   Streamlit     │◄──►│   FastAPI       │◄──►│   Dados         │
│   (Port 8501)   │    │   (Port 8000)   │    │   ChromaDB      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Como Executar

### 1. Iniciar o Backend (API)

```bash
# Terminal 1
python run_api.py
```

**✅ API disponível em:** http://localhost:8000
**📖 Documentação:** http://localhost:8000/docs

### 2. Iniciar o Frontend (Interface Web)

```bash
# Terminal 2
python run_frontend.py
```

**✅ Interface disponível em:** http://localhost:8501

## 🔐 Autenticação

### Tokens Disponíveis:

- **`seu_token_secreto_aqui`** - Admin (todas as permissões)
- **`admin_token_123`** - Admin (todas as permissões)
- **`user_token_456`** - User (apenas leitura)

### Como Configurar:

1. Na interface web, vá para a sidebar
2. Insira o token no campo "Bearer Token"
3. Clique em "Testar Conexão"

## 🎯 Funcionalidades

### 💬 Chat com IA

- Interface de conversação intuitiva
- Histórico de conversas persistente
- Exibição de documentos utilizados
- Respostas em tempo real

### 📁 Gerenciamento de Arquivos

- Visualizar status dos documentos
- Carregar novos arquivos (PDF, TXT, DOCX, MD)
- Configurar parâmetros de processamento
- Lista de arquivos disponíveis

### 📚 Histórico de Chats

- Acompanhar conversas anteriores
- Navegar entre diferentes chats
- Exportar histórico em JSON
- Limpar histórico

### ⚙️ Configurações

- Gerenciar tokens de autenticação
- Configurar URL da API
- Testar conexões
- Informações do sistema

## 🧪 Exemplo de Uso

### 1. Carregar um Documento

```bash
# Via API
curl -X POST "http://localhost:8000/documents/load" \
     -H "Authorization: Bearer seu_token_secreto_aqui" \
     -H "Content-Type: application/json" \
     -d '{"file_path": "historia.txt"}'
```

**Ou via Interface Web:**
1. Vá para "Gerenciar Arquivos"
2. Insira o caminho do arquivo
3. Clique em "Carregar Documento"

### 2. Fazer uma Consulta

```bash
# Via API
curl -X POST "http://localhost:8000/query" \
     -H "Authorization: Bearer seu_token_secreto_aqui" \
     -H "Content-Type: application/json" \
     -d '{"query": "Quem descobriu o Brasil?"}'
```

**Ou via Interface Web:**
1. Vá para "Chat"
2. Digite sua pergunta
3. Pressione Enter ou clique em "Send"

### 3. Verificar Status

```bash
# Via API
curl -X GET "http://localhost:8000/documents/status" \
     -H "Authorization: Bearer seu_token_secreto_aqui"
```

**Ou via Interface Web:**
1. Na sidebar, clique em "Atualizar Status"
2. Veja as métricas na sidebar

## 🎨 Interface

### Sidebar (Menu Lateral)

- **🔐 Autenticação**: Configuração de tokens
- **📋 Navegação**: Botões para diferentes páginas
- **📚 Histórico**: Lista de conversas anteriores
- **ℹ️ Sistema**: Status e métricas

### Página Principal

- **💬 Chat**: Área de conversação
- **📁 Arquivos**: Gerenciamento de documentos
- **⚙️ Configurações**: Configurações do sistema

## 🔧 Configurações Avançadas

### Personalizar Tokens

Edite o arquivo `auth.py`:

```python
VALID_TOKENS = {
    "seu_token_secreto_aqui",
    "admin_token_123",
    "user_token_456",
    # Adicione seus tokens aqui:
    "meu_token_personalizado",
    "token_empresa_xyz"
}
```

### Configurar API URL

No arquivo `streamlit_app.py`:

```python
API_BASE_URL = "http://localhost:8000"  # Altere conforme necessário
```

### Personalizar Tema

No arquivo `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#FF6B6B"      # Cor principal
backgroundColor = "#FFFFFF"   # Cor de fundo
secondaryBackgroundColor = "#F0F2F6"  # Cor secundária
textColor = "#262730"         # Cor do texto
```

## 🐛 Solução de Problemas

### API não conecta

1. Verifique se a API está rodando: http://localhost:8000/health
2. Confirme o token de autenticação
3. Verifique se não há firewall bloqueando

### Frontend não carrega

1. Verifique se o Streamlit está instalado: `pip install streamlit`
2. Confirme se a porta 8501 está livre
3. Verifique os logs no terminal

### Documentos não carregam

1. Verifique se o arquivo existe
2. Confirme as permissões de leitura
3. Verifique se o formato é suportado (PDF, TXT, DOCX, MD)

## 📊 Métricas e Monitoramento

### Status dos Documentos

- **Documentos Carregados**: Quantidade total
- **Sistema Ativo**: Se há documentos disponíveis
- **Último Carregamento**: Timestamp do último arquivo

### Logs da API

A API registra todas as operações:
- Carregamento de documentos
- Consultas realizadas
- Erros e exceções
- Status de autenticação

## 🚀 Próximos Passos

1. **Deploy em Produção**: Configurar servidor web
2. **Banco de Dados**: Migrar para PostgreSQL/MySQL
3. **Autenticação**: Implementar JWT ou OAuth2
4. **Cache**: Adicionar Redis para performance
5. **Monitoramento**: Integrar com Prometheus/Grafana

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique os logs da API e frontend
2. Consulte a documentação em `/docs`
3. Teste a conectividade com os endpoints
4. Verifique as configurações de autenticação
