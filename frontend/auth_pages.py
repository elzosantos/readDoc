"""
Páginas de autenticação para o frontend Streamlit
"""

import streamlit as st
import requests
import json
import time
from typing import Optional, Dict

# Configurações da API
API_BASE_URL = "http://localhost:8000"

def make_auth_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """Faz requisição para a API de autenticação"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erro na requisição: {response.status_code}")
            try:
                error_data = response.json()
                st.error(f"Detalhes: {error_data.get('detail', 'Erro desconhecido')}")
            except:
                st.error(f"Resposta: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API. Verifique se o backend está rodando.")
        return None
    except Exception as e:
        st.error(f"❌ Erro na requisição: {str(e)}")
        return None

def render_login_page():
    """Renderiza a página de login"""
    st.title("🔐 Login")
    st.markdown("Faça login para acessar o sistema")
    
    with st.form("login_form"):
        email = st.text_input("📧 Email", placeholder="seu@email.com")
        password = st.text_input("🔒 Senha", type="password", placeholder="Sua senha")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            login_button = st.form_submit_button("🚀 Entrar", use_container_width=True)
        
        with col2:
            register_button = st.form_submit_button("📝 Cadastrar", use_container_width=True)
        
        if login_button:
            if email and password:
                with st.spinner("Fazendo login..."):
                    response = make_auth_request("/auth/login", "POST", {
                        "email": email,
                        "password": password
                    })
                    
                    if response and response.get("success"):
                        # Salvar dados do usuário na sessão
                        st.session_state.user = response.get("user")
                        st.session_state.auth_token = response.get("token")
                        st.session_state.is_authenticated = True
                        
                        # Redirecionar automaticamente para o chat
                        st.session_state.current_page = "chat"
                        st.rerun()
                    else:
                        st.error("❌ Email ou senha incorretos")
            else:
                st.error("❌ Preencha todos os campos")
        
        if register_button:
            st.session_state.show_register = True
            st.rerun()

def render_register_page():
    """Renderiza a página de cadastro"""
    st.title("📝 Cadastro")
    st.markdown("Crie sua conta para acessar o sistema")
    
    with st.form("register_form"):
        name = st.text_input("👤 Nome Completo", placeholder="Seu nome completo")
        email = st.text_input("📧 Email", placeholder="seu@email.com")
        password = st.text_input("🔒 Senha", type="password", placeholder="Mínimo 6 caracteres")
        confirm_password = st.text_input("🔒 Confirmar Senha", type="password", placeholder="Digite a senha novamente")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            register_button = st.form_submit_button("📝 Cadastrar", use_container_width=True)
        
        with col2:
            login_button = st.form_submit_button("🔐 Voltar ao Login", use_container_width=True)
        
        if register_button:
            if name and email and password and confirm_password:
                if password != confirm_password:
                    st.error("❌ As senhas não coincidem")
                elif len(password) < 6:
                    st.error("❌ A senha deve ter pelo menos 6 caracteres")
                else:
                    with st.spinner("Criando conta..."):
                        response = make_auth_request("/auth/register", "POST", {
                            "name": name,
                            "email": email,
                            "password": password,
                            "role": "user"
                        })
                        
                        if response and response.get("success"):
                            st.success("✅ Conta criada com sucesso!")
                            st.info("💡 Agora você pode fazer login com suas credenciais")
                            st.session_state.show_register = False
                            st.rerun()
                        else:
                            st.error("❌ Erro ao criar conta")
            else:
                st.error("❌ Preencha todos os campos")
        
        if login_button:
            st.session_state.show_register = False
            st.rerun()

def render_auth_page():
    """Renderiza a página principal de autenticação"""
    # Verificar se já está autenticado (com validação real do token)
    if is_authenticated():
        # Redirecionar automaticamente para o chat
        st.session_state.current_page = "chat"
        st.rerun()
        return
    
    # Mostrar página de login ou cadastro
    if st.session_state.get("show_register", False):
        render_register_page()
    else:
        render_login_page()
    
    # Informações sobre o sistema
    st.divider()
    st.markdown("### ℹ️ Sobre o Sistema")
    st.info("""
    **Sistema de Busca de Documentos com IA**
    
    - 🔍 **Busca Inteligente**: Faça perguntas sobre seus documentos
    - 📄 **Gerenciamento**: Carregue e organize seus arquivos
    - 👥 **Perfis**: Usuário comum ou administrador
    - 🔐 **Seguro**: Autenticação e controle de acesso
    
    **Usuário Padrão Admin:**
    - Email: admin@system.com
    - Senha: admin123
    """)

def logout_user():
    """Realiza logout do usuário"""
    if st.session_state.get("auth_token"):
        # Fazer logout na API
        headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
        try:
            response = requests.post(f"{API_BASE_URL}/auth/logout", headers=headers)
        except:
            pass  # Ignorar erros de logout
    
    # Limpar dados da sessão
    st.session_state.user = None
    st.session_state.auth_token = None
    st.session_state.is_authenticated = False
    st.session_state.current_page = "auth"
    
    st.success("✅ Logout realizado com sucesso!")
    st.rerun()

def get_auth_headers() -> Dict[str, str]:
    """Retorna headers de autenticação para requisições"""
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def is_authenticated() -> bool:
    """Verifica se o usuário está autenticado"""
    if not st.session_state.get("is_authenticated", False):
        return False
    
    # Verificar se o token ainda é válido
    token = st.session_state.get("auth_token")
    if not token:
        return False
    
    # Verificar se o token expirou (cache local para evitar muitas requisições)
    last_check = st.session_state.get("last_auth_check", 0)
    current_time = time.time()
    
    # Só verificar com o servidor a cada 5 minutos
    if current_time - last_check > 300:  # 5 minutos
        try:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=5)
            if response.status_code == 200:
                st.session_state.last_auth_check = current_time
                return True
            else:
                # Token inválido, limpar sessão
                st.session_state.is_authenticated = False
                st.session_state.auth_token = None
                st.session_state.user = None
                st.session_state.last_auth_check = 0
                return False
        except:
            # Em caso de erro de rede, manter sessão por mais tempo
            st.session_state.last_auth_check = current_time
            return True
    
    return True

def get_current_user() -> Optional[Dict]:
    """Retorna dados do usuário atual"""
    return st.session_state.get("user")

def has_permission(permission: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    user = get_current_user()
    if not user:
        return False
    
    # Mapear roles para permissões
    role_permissions = {
        "admin": [
            "read_documents", "write_documents", "manage_users", 
            "view_admin_panel", "delete_documents", "view_system_logs"
        ],
        "user": [
            "read_documents", "write_documents"
        ]
    }
    
    user_role = user.get("role", "user")
    return permission in role_permissions.get(user_role, [])

def is_admin() -> bool:
    """Verifica se o usuário é administrador"""
    user = get_current_user()
    return user and user.get("role") == "admin"
