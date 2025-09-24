# 🚀 Instruções Rápidas - LLMChat

## ⚡ Execução Rápida

### 1. Instalar Dependências
```bash
pip install -r requirements.txt
pip install -r requirements_frontend.txt
```

### 2. Executar Sistema

**Terminal 1 (Backend):**
```bash
python run_api_simple.py
```

**Terminal 2 (Frontend):**
```bash
python run_frontend_simple.py
```

### 3. Testar Sistema
```bash
python test_system.py
```

## 🌐 Acessos

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs

## 🔐 Tokens para Teste

- `seu_token_secreto_aqui` (Admin)
- `admin_token_123` (Admin)
- `user_token_456` (User)

## 🎯 Como Usar

1. **Acesse**: http://localhost:8501
2. **Configure Token**: Na sidebar, insira um dos tokens acima
3. **Teste Conexão**: Clique em "Testar Conexão"
4. **Navegue**: Use os botões da sidebar
5. **Chat**: Digite perguntas na área de chat
6. **Arquivos**: Carregue documentos na página "Gerenciar Arquivos"

## 🐛 Problemas Comuns

### API não conecta
- Verifique se `python run_api_simple.py` está rodando
- Teste: http://localhost:8000/health

### Frontend não carrega
- Verifique se `python run_frontend_simple.py` está rodando
- Teste: http://localhost:8501

### Token inválido
- Use um dos tokens listados acima
- Verifique se não há espaços extras

## 📞 Suporte

Se algo não funcionar:
1. Execute `python test_system.py`
2. Verifique os logs nos terminais
3. Confirme se as portas 8000 e 8501 estão livres
