# 🔐 Instruções de Login - TasqAI

## ✅ **Sistema de Autenticação Funcionando!**

O sistema de autenticação está **100% funcional**. Aqui estão as credenciais para teste:

### 📝 **Credenciais de Teste:**

#### **Administrador:**
- **Email:** `admin@system.com`
- **Senha:** `admin123`
- **Role:** Admin (acesso completo)

#### **Usuário Comum:**
- **Email:** `teste@exemplo.com`
- **Senha:** `teste123`
- **Role:** User (acesso básico)

## 🚀 **Como Testar:**

### **1. Iniciar o Sistema:**
```bash
# Terminal 1 - Backend
cd backend
python start_api.py

# Terminal 2 - Frontend
cd frontend
python run_frontend.py
```

### **2. Acessar o Sistema:**
- Abra o navegador em: `http://localhost:8501`
- Use as credenciais acima para fazer login

### **3. Verificar Funcionalidades:**
- ✅ Login com credenciais corretas
- ✅ Redirecionamento para Dashboard
- ✅ Sessão persistente por 24 horas
- ✅ Logout funcionando
- ✅ Navegação entre páginas

## 🔧 **Se o Login Não Funcionar:**

### **Verificar se o Backend está Rodando:**
```bash
# Testar API diretamente
curl -X GET http://localhost:8000/health
```

### **Verificar se o Frontend está Rodando:**
- Acesse: `http://localhost:8501`
- Deve aparecer a página de login

### **Verificar Logs:**
- Backend: Terminal onde executou `python start_api.py`
- Frontend: Terminal onde executou `python run_frontend.py`

## 🐛 **Problemas Comuns:**

### **1. "Email ou senha incorretos"**
- ✅ Verifique se está usando as credenciais corretas
- ✅ Verifique se o backend está rodando na porta 8000

### **2. "Erro de conexão"**
- ✅ Verifique se o backend está rodando
- ✅ Verifique se não há firewall bloqueando

### **3. "Página não carrega"**
- ✅ Verifique se o frontend está rodando na porta 8501
- ✅ Tente acessar `http://localhost:8501`

## 📊 **Status do Sistema:**

- ✅ **Backend API:** Funcionando
- ✅ **Autenticação:** Funcionando
- ✅ **Banco de Dados:** Funcionando
- ✅ **Frontend:** Funcionando
- ✅ **Sessão 24h:** Implementada

## 🎯 **Próximos Passos:**

1. **Teste o login** com as credenciais fornecidas
2. **Verifique a navegação** entre as páginas
3. **Teste o logout** e login novamente
4. **Teste a persistência** da sessão (F5)

---

**✨ O sistema está pronto para uso! Use as credenciais acima para fazer login.**
