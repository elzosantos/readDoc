"""
Páginas de autenticação para o frontend Streamlit
"""

import streamlit as st
import requests
import json
import time
from typing import Optional, Dict

# Importar o novo gerenciador de sessão
from session_manager import session_manager, login_user, logout_user, get_current_user, has_permission, is_admin, get_auth_headers, is_authenticated

# Configurações da API
API_BASE_URL = "http://localhost:8000"

# Funções de sessão agora são gerenciadas pelo session_manager

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
                    # Usar o novo sistema de login
                    if login_user(email, password):
                        st.success("✅ Login realizado com sucesso!")
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
        # Redirecionar automaticamente para o dashboard
        st.session_state.current_page = "dashboard"
        st.rerun()
        return
    
    # CSS para página de login
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
        background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 50%, #2563eb 100%);
        border-radius: 20px;
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    .login-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
    }
    
    .login-subtitle {
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        opacity: 0.9;
    }
    
    .login-form {
        background: rgba(255, 255, 255, 0.1);
       
        border-radius: 15px;
        backdrop-filter: blur(10px);
      
    }
    
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.9);
        border: 2px solid rgba(255, 255, 255, 0.3);
        border-radius: 10px;
        color: #1e3a8a;
        font-weight: 500;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #60a5fa;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.3);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Container principal
    st.markdown("""
    <div class="login-container">
        <h1 class="login-title">TasqAI - Docs</h1>
        <p class="login-subtitle">Sistema Inteligente de Busca de Documentos</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Formulário de login/cadastro
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-form">', unsafe_allow_html=True)
        
        # Mostrar página de login ou cadastro
        if st.session_state.get("show_register", False):
            render_register_page()
        else:
            render_login_page()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
 

# Funções de autenticação agora são gerenciadas pelo session_manager
