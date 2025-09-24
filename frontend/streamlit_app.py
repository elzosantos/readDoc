"""
Frontend Streamlit para o Sistema de Busca de Documentos com IA
"""

import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import time

# Importar módulos de autenticação
from auth_pages import render_auth_page
from session_manager import (
    session_manager, 
    logout_user, 
    is_authenticated, 
    get_current_user, 
    has_permission, 
    is_admin,
    get_auth_headers,
    initialize_session
)
from user_management import render_user_management_page
from profile_page import render_profile_page
from top_menu import render_top_menu

# Configuração da página
st.set_page_config(
    page_title="TasqAI - Docs",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado - Design Moderno ChatGPT Style
st.markdown("""
<style>
    /* Importar fontes modernas do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* JavaScript para persistência de sessão */
    <script>
    // Gerenciador de Sessão para TasqAI
    class SessionManager {
        constructor() {
            this.prefix = 'tasqai_';
            this.sessionKeys = [
                'is_authenticated', 'auth_token', 'user', 
                'current_page', 'api_token', 'last_auth_check'
            ];
            this.init();
        }

        init() {
            this.restoreSession();
            this.setupSessionListener();
        }

        saveSessionData(key, value) {
            try {
                const fullKey = this.prefix + key;
                localStorage.setItem(fullKey, JSON.stringify(value));
                console.log(`Sessão salva: ${key}`);
            } catch (e) {
                console.warn('Erro ao salvar no localStorage:', e);
            }
        }

        loadSessionData(key) {
            try {
                const fullKey = this.prefix + key;
                const data = localStorage.getItem(fullKey);
                return data ? JSON.parse(data) : null;
            } catch (e) {
                console.warn('Erro ao carregar do localStorage:', e);
                return null;
            }
        }

        clearSessionData() {
            try {
                this.sessionKeys.forEach(key => {
                    localStorage.removeItem(this.prefix + key);
                });
                console.log('Dados de sessão limpos');
            } catch (e) {
                console.warn('Erro ao limpar localStorage:', e);
            }
        }

        restoreSession() {
            const isAuth = this.loadSessionData('is_authenticated');
            const token = this.loadSessionData('auth_token');
            const user = this.loadSessionData('user');
            const currentPage = this.loadSessionData('current_page');
            const lastCheck = this.loadSessionData('last_auth_check');
            
            if (isAuth && token && user) {
                // Verificar se o token não expirou (24 horas)
                const now = Date.now();
                const lastCheckTime = lastCheck ? lastCheck * 1000 : 0;
                const tokenAge = now - lastCheckTime;
                const maxAge = 24 * 60 * 60 * 1000; // 24 horas
                
                if (tokenAge < maxAge) {
                    console.log('Restaurando sessão do localStorage');
                    
                    // Atualizar timestamp da última verificação
                    this.saveSessionData('last_auth_check', Math.floor(Date.now() / 1000));
                    
                    // Enviar dados para o Streamlit via postMessage
                    window.parent.postMessage({
                        type: 'session_restore',
                        data: {
                            is_authenticated: isAuth,
                            auth_token: token,
                            user: user,
                            current_page: currentPage || 'dashboard',
                            last_auth_check: Math.floor(Date.now() / 1000)
                        }
                    }, '*');
                } else {
                    console.log('Token expirado, limpando sessão');
                    this.clearSessionData();
                }
            }
        }

        setupSessionListener() {
            window.addEventListener('message', (event) => {
                if (event.data.type === 'save_session') {
                    const data = event.data.data;
                    Object.keys(data).forEach(key => {
                        this.saveSessionData(key, data[key]);
                    });
                } else if (event.data.type === 'clear_session') {
                    this.clearSessionData();
                }
            });
        }
    }

    // Inicializar o gerenciador de sessão
    const sessionManager = new SessionManager();

    // Expor funções globalmente para compatibilidade
    window.saveSessionData = (key, value) => sessionManager.saveSessionData(key, value);
    window.loadSessionData = (key) => sessionManager.loadSessionData(key);
    window.clearSessionData = () => sessionManager.clearSessionData();
    </script>
    
    /* Cores principais - Tema ChatGPT Style */
    :root {
        --bg-primary: #212121;
        --bg-secondary: #2f2f2f;
        --bg-tertiary: #3f3f3f;
        --bg-card: #ffffff;
        --bg-sidebar: #171717;
        --bg-input: #ffffff;
        --bg-button: #10a37f;
        --bg-button-hover: #0d8f6f;
        --bg-button-secondary: #f7f7f8;
        --bg-button-secondary-hover: #ececf1;
        
        --text-primary: #2d2d2d;
        --text-secondary: #6e6e80;
        --text-muted: #8e8ea0;
        --text-white: #ffffff;
        --text-accent: #10a37f;
        
        --border-light: #e5e5e5;
        --border-medium: #d1d5db;
        --border-dark: #40414f;
        --border-accent: #10a37f;
        
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
        --radius-2xl: 20px;
    }
    
    /* Layout principal - Design moderno ChatGPT */
    .main .block-container {
        padding: 0 !important;
        padding-top: 0 !important;
        background: var(--bg-card);
        min-height: 100vh;
        max-width: 100% !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Reduzir espaçamento superior */
    .stApp > div:first-child {
        padding-top: 0 !important;
    }
    
    /* Remover margens desnecessárias */
    .main .block-container > div:first-child {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }
    
    /* Sidebar moderna - Estilo ChatGPT */
    .css-1d391kg {
        background: var(--bg-sidebar) !important;
        border-right: 1px solid var(--border-dark);
        box-shadow: var(--shadow-lg);
    }
    
    /* Classe específica para padding customizado */
    .st-emotion-cache-1jicfl2 {
        padding: 1rem 1rem 10rem !important;
    }
    .st-emotion-cache-11ukie {
        height: 0rem !important;
    }
    
    .st-emotion-cache-kgpedg {
        display: flex;
        -webkit-box-pack: justify;
        justify-content: space-between;
        -webkit-box-align: start;
        align-items: start;
        padding: calc(1.375rem) 1.5rem -0.5rem !important;
    }
    
    .css-1d391kg .css-1v0mbdj {
        color: var(--text-white) !important;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }
    
    .css-1d391kg .stMarkdown {
        color: var(--text-white) !important;
        font-family: 'Inter', sans-serif;
    }
    
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3 {
        color: var(--text-white) !important;
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    /* Cards modernos - Estilo ChatGPT */
    .modern-card {
        background: var(--bg-card);
        border-radius: var(--radius-xl);
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-light);
        transition: all 0.2s ease;
        margin: 1rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .modern-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--border-medium);
    }
    
    /* Dashboard grid */
    .dashboard-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 1.5rem;
        margin: 2rem 0;
    }
    
    /* Task cards - Estilo moderno */
    .task-card {
        background: var(--bg-card);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        box-shadow: var(--shadow-sm);
        border-left: 3px solid var(--bg-button);
        transition: all 0.2s ease;
        margin: 0.5rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .task-card:hover {
        transform: translateX(2px);
        box-shadow: var(--shadow-md);
        border-left-color: var(--bg-button-hover);
    }
    
    .task-card.completed {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
    }
    
    .task-card.in-progress {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    }
    
    /* Botões modernos - Estilo ChatGPT */
    .stButton > button {
        background: var(--bg-button) !important;
        color: var(--text-white) !important;
        border: none !important;
        border-radius: var(--radius-lg) !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        font-family: 'Inter', sans-serif !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
        text-transform: none !important;
        letter-spacing: 0.01em !important;
        position: relative !important;
        overflow: hidden !important;
    }
    
    .stButton > button:hover {
        background: var(--bg-button-hover) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    /* Botões secundários modernos */
    .stButton > button[kind="secondary"] {
        background: var(--bg-button-secondary) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-medium) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: var(--bg-button-secondary-hover) !important;
        border-color: var(--border-accent) !important;
        transform: translateY(-1px) !important;
        box-shadow: var(--shadow-md) !important;
    }
    
    /* Botões de ação rápida */
    .action-button {
        background: var(--white) !important;
        color: var(--navy-blue) !important;
        border: 2px solid var(--medium-gray) !important;
        border-radius: 8px !important;
        padding: 0.5rem 1rem !important;
        font-size: 0.875rem !important;
        transition: all 0.2s ease !important;
    }
    
    .action-button:hover {
        border-color: var(--navy-blue) !important;
        background: var(--light-gray) !important;
        transform: translateY(-1px) !important;
    }
    
    /* Inputs modernos - Estilo ChatGPT */
    .stTextInput > div > div > input {
        border-radius: var(--radius-lg) !important;
        border: 1px solid var(--border-medium) !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.75rem 1rem !important;
        transition: all 0.2s ease !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--border-accent) !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1), var(--shadow-sm) !important;
        outline: none !important;
    }
    
    .stTextInput > div > div > input:hover {
        border-color: var(--border-accent) !important;
    }
    
    /* Textarea moderna para prompt - Estilo ChatGPT */
    .stTextArea > div > div > textarea {
        border-radius: var(--radius-xl) !important;
        border: 1px solid var(--border-medium) !important;
        background: var(--bg-input) !important;
        color: var(--text-primary) !important;
        min-height: 120px !important;
        font-size: 0.95rem !important;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.5 !important;
        padding: 1rem !important;
        transition: all 0.2s ease !important;
        resize: vertical !important;
        box-shadow: var(--shadow-sm) !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: var(--border-accent) !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1), var(--shadow-sm) !important;
        outline: none !important;
    }
    
    .stTextArea > div > div > textarea:hover {
        border-color: var(--border-accent) !important;
    }
    
    /* Cards e containers */
    .stContainer {
        background: var(--white) !important;
        border-radius: 15px !important;
        padding: 1rem !important;
        box-shadow: 0 8px 25px rgba(15, 23, 42, 0.1) !important;
        border: 1px solid var(--medium-gray) !important;
        margin: 1rem 0 !important;
    }
    
    /* Títulos modernos - Estilo ChatGPT */
    h1 {
        color: var(--text-primary) !important;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 1.5rem !important;
        letter-spacing: -0.02em !important;
        line-height: 1.2 !important;
    }
    
    h2 {
        color: var(--text-primary) !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 1rem !important;
        letter-spacing: -0.02em !important;
        line-height: 1.3 !important;
    }
    
    h3 {
        color: var(--text-primary) !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        margin-bottom: 0.75rem !important;
        letter-spacing: -0.01em !important;
        line-height: 1.4 !important;
    }
    
    /* Mensagens de chat modernas - Estilo ChatGPT */
    .chat-message {
        background: var(--bg-card) !important;
        border-radius: var(--radius-2xl) !important;
        padding: 1.5rem !important;
        margin: 1rem 0 !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--border-light) !important;
        transition: all 0.2s ease !important;
        position: relative !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .chat-message:hover {
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
        border-color: var(--border-medium) !important;
    }
    
    .chat-message.user {
        background: var(--bg-card) !important;
        border-left: 3px solid var(--bg-button) !important;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
        border-left: 3px solid var(--text-accent) !important;
    }
    
    /* Status indicators - Estilo moderno */
    .status-success {
        color: #059669 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        background: rgba(5, 150, 105, 0.08) !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        border-left: 3px solid #059669 !important;
    }
    
    .status-error {
        color: #dc2626 !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        background: rgba(220, 38, 38, 0.08) !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        border-left: 3px solid #dc2626 !important;
    }
    
    .status-info {
        color: var(--text-accent) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        background: rgba(16, 163, 127, 0.08) !important;
        padding: 0.75rem 1rem !important;
        border-radius: var(--radius-md) !important;
        border-left: 3px solid var(--text-accent) !important;
    }
    
    /* Expanders - Estilo moderno */
    .streamlit-expander {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-light) !important;
        border-radius: var(--radius-lg) !important;
        margin: 0.5rem 0 !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .streamlit-expanderHeader {
        background: var(--bg-button-secondary) !important;
        color: var(--text-primary) !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        border-radius: var(--radius-lg) var(--radius-lg) 0 0 !important;
    }
    
    /* Selectbox - Estilo moderno */
    .stSelectbox > div > div {
        background: var(--bg-input) !important;
        border: 1px solid var(--border-medium) !important;
        border-radius: var(--radius-lg) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stSelectbox > div > div:focus-within {
        border-color: var(--border-accent) !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.1) !important;
    }
    
    /* File uploader - Estilo moderno */
    .stFileUploader > div {
        background: var(--bg-card) !important;
        border: 2px dashed var(--border-medium) !important;
        border-radius: var(--radius-xl) !important;
        padding: 2rem !important;
        transition: all 0.2s ease !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    .stFileUploader > div:hover {
        border-color: var(--border-accent) !important;
        background: rgba(16, 163, 127, 0.02) !important;
    }
    
    /* Scrollbar personalizada - Estilo moderno */
    ::-webkit-scrollbar {
        width: 8px !important;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--bg-button-secondary) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--bg-button) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--bg-button-hover) !important;
    }
    
    /* Métricas - Estilo moderno */
    .metric-container {
        background: var(--bg-card) !important;
        border-radius: var(--radius-xl) !important;
        padding: 1.5rem !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--border-light) !important;
        text-align: center !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Alertas - Estilo moderno */
    .stAlert {
        border-radius: var(--radius-lg) !important;
        border: none !important;
        box-shadow: var(--shadow-md) !important;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Tabelas - Estilo moderno */
    .stDataFrame {
        border-radius: var(--radius-lg) !important;
        overflow: hidden !important;
        box-shadow: var(--shadow-md) !important;
        border: 1px solid var(--border-light) !important;
    }
    
    /* Progress bar - Estilo moderno */
    .stProgress > div > div > div > div {
        background: var(--bg-button) !important;
        border-radius: var(--radius-sm) !important;
    }
    
    /* Spinner - Estilo moderno */
    .stSpinner {
        color: var(--bg-button) !important;
    }
    
    /* Ocultar indicador "Running" */
    .stApp > header {
        display: none !important;
    }
    
    /* Ocultar status bar do Streamlit */
    .stApp > div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    /* Ocultar menu hambúrguer */
    .stApp > div[data-testid="stToolbar"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

# Configurações da API
API_BASE_URL = "http://localhost:8000"
DEFAULT_TOKEN = "seu_token_secreto_aqui"

def save_session_to_storage():
    """Salva dados da sessão no localStorage via JavaScript"""
    if st.session_state.get("is_authenticated"):
        js_code = f"""
        <script>
        saveSessionData('is_authenticated', {str(st.session_state.is_authenticated).lower()});
        saveSessionData('auth_token', '{st.session_state.get("auth_token", "")}');
        saveSessionData('user', {json.dumps(st.session_state.get("user", {}))});
        saveSessionData('current_page', '{st.session_state.get("current_page", "dashboard")}');
        saveSessionData('api_token', '{st.session_state.get("api_token", "")}');
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)

def clear_session_from_storage():
    """Limpa dados da sessão do localStorage via JavaScript"""
    js_code = """
    <script>
    clearSessionData();
    </script>
    """
    st.markdown(js_code, unsafe_allow_html=True)

def restore_session_from_storage():
    """Tenta restaurar sessão do localStorage"""
    # Esta função será chamada no início da aplicação
    # O JavaScript já cuida de enviar os dados via postMessage
    pass

def handle_session_restore():
    """Processa dados de restauração de sessão do localStorage"""
    # Verificar se há dados de sessão no localStorage via JavaScript
    st.markdown("""
    <script>
    // Verificar se há dados de sessão para restaurar
    if (typeof window !== 'undefined' && window.sessionManager) {
        const isAuth = window.sessionManager.loadSessionData('is_authenticated');
        const token = window.sessionManager.loadSessionData('auth_token');
        const user = window.sessionManager.loadSessionData('user');
        const lastCheck = window.sessionManager.loadSessionData('last_auth_check');
        
        if (isAuth && token && user) {
            // Verificar se o token não expirou (24 horas)
            const now = Date.now();
            const lastCheckTime = lastCheck ? lastCheck * 1000 : 0;
            const tokenAge = now - lastCheckTime;
            const maxAge = 24 * 60 * 60 * 1000; // 24 horas
            
            if (tokenAge < maxAge) {
                // Restaurar sessão
                window.parent.postMessage({
                    type: 'streamlit_session_restore',
                    data: {
                        is_authenticated: isAuth,
                        auth_token: token,
                        user: user,
                        current_page: 'dashboard',
                        last_auth_check: lastCheck || Math.floor(Date.now() / 1000)
                    }
                }, '*');
            }
        }
    }
    
    // Listener para capturar mensagens de restauração de sessão
    window.addEventListener('message', function(event) {
        if (event.data.type === 'session_restore') {
            const data = event.data.data;
            
            // Atualizar session state do Streamlit
            if (data.is_authenticated) {
                // Usar st.session_state via JavaScript (se possível)
                console.log('Restaurando sessão:', data);
                
                // Forçar reload da página para aplicar mudanças
                setTimeout(() => {
                    window.location.reload();
                }, 100);
            }
        }
    });
    </script>
    """, unsafe_allow_html=True)

# Inicializar estado da sessão com o novo gerenciador
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = True
    
    # Inicializar variáveis padrão se não existirem
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []
if "current_page" not in st.session_state:
    st.session_state.current_page = "auth"  # Começar com página de autenticação
if "api_token" not in st.session_state:
    st.session_state.api_token = DEFAULT_TOKEN
if "documents_status" not in st.session_state:
    st.session_state.documents_status = None
    # Inicializar o novo gerenciador de sessão
    initialize_session()
    if "last_auth_check" not in st.session_state:
        st.session_state.last_auth_check = 0

# A restauração de sessão agora é gerenciada pelo session_manager

def generate_chat_name(query: str) -> str:
    """Gera um nome para o chat baseado na consulta (máximo 15 caracteres)"""
    # Palavras-chave importantes para identificar o contexto
    keywords = {
        "brasil": "Brasil",
        "descobriu": "Descoberta",
        "capital": "Capital",
        "pedro": "Pedro",
        "cabral": "Cabral",
        "história": "História",
        "colônia": "Colônia",
        "independência": "Independência",
        "império": "Império",
        "república": "República",
        "guerra": "Guerra",
        "revolução": "Revolução",
        "governo": "Governo",
        "presidente": "Presidente",
        "economia": "Economia",
        "cultura": "Cultura",
        "arte": "Arte",
        "literatura": "Literatura",
        "religião": "Religião",
        "educação": "Educação"
    }
    
    query_lower = query.lower()
    
    # Procurar por palavras-chave
    for keyword, name in keywords.items():
        if keyword in query_lower:
            return name[:15]
    
    # Se não encontrar palavra-chave, usar as primeiras palavras
    words = query.split()[:3]
    name = " ".join(words)
    return name[:15]

def save_current_chat_to_history():
    """Salva o chat atual no histórico"""
    if st.session_state.get("current_chat"):
        # Gerar nome baseado na primeira pergunta
        first_query = st.session_state.get("current_chat", [{}])[0].get("query", "Chat")
        chat_name = generate_chat_name(first_query)
        
        # Criar entrada do histórico
        chat_entry = {
            "name": chat_name,
            "messages": st.session_state.get("current_chat", []).copy(),
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "id": len(st.session_state.get("chat_history", [])) + 1
        }
        
        # Adicionar ao histórico
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []
        st.session_state.chat_history.append(chat_entry)
        
        # Limpar chat atual
        st.session_state.current_chat = []

def make_api_request(endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Optional[Dict]:
    """Faz requisição para a API com autenticação"""
    try:
        # Usar token de autenticação se disponível, senão usar token legado
        token = st.session_state.get("auth_token") or st.session_state.api_token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            st.error("❌ Token inválido! Verifique sua autenticação.")
            return None
        else:
            st.error(f"❌ Erro na API: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        st.error("❌ Não foi possível conectar à API. Verifique se o servidor está rodando.")
        return None
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return None

def render_sidebar():
    """Renderiza a sidebar com navegação e histórico usando Tailwind CSS"""
    
    # CSS para Tailwind e sidebar customizada
    st.markdown("""
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
    /* Sidebar customizada */
    .custom-sidebar {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid #334155;
        font-family: 'Inter', sans-serif;
        padding: 0;
        margin: 0;
    }
    
    .custom-sidebar::-webkit-scrollbar {
        width: 4px;
    }
    
    .custom-sidebar::-webkit-scrollbar-track {
        background: #1e293b;
    }
    
    .custom-sidebar::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 2px;
    }
    
    .custom-sidebar::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
    
    /* Botões customizados */
    .sidebar-btn {
        width: 100%;
        padding: 12px 16px;
        margin: 4px 0;
        background: transparent;
        border: none;
        color: #e2e8f0;
        text-align: left;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 14px;
        font-weight: 500;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    .sidebar-btn:hover {
        background: #334155;
        color: #f1f5f9;
        transform: translateX(4px);
    }
    
    .sidebar-btn.active {
        background: #3b82f6;
        color: white;
    }
    
    .sidebar-btn-icon {
        font-size: 16px;
        width: 20px;
        text-align: center;
    }
    
    /* Seções */
    .sidebar-section {
        padding: 16px;
        border-bottom: 1px solid #334155;
    }
    
    .sidebar-section-title {
        color: #94a3b8;
        font-size: 12px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    /* Histórico de chat */
    .chat-history-item {
        padding: 8px 12px;
        margin: 2px 0;
        background: transparent;
        border: none;
        color: #cbd5e1;
        text-align: left;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 13px;
        width: 100%;
    }
    
    .chat-history-item:hover {
        background: #334155;
        color: #f1f5f9;
    }
    
    /* Status */
    .status-indicator {
        display: inline-block;
        width: 8px;
        height: 8px;
        border-radius: 50%;
        margin-right: 8px;
    }
    
    .status-online { background: #10b981; }
    .status-offline { background: #ef4444; }
    
    /* Estilos para elementos do Streamlit na sidebar */
    .stSidebar .stMarkdown {
        color: #e2e8f0 !important;
    }
    
    .stSidebar .stButton > button {
        background: transparent !important;
        border: none !important;
        color: #e2e8f0 !important;
        width: 100% !important;
        text-align: left !important;
        padding: 12px 16px !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        gap: 12px !important;
    }
    
    .stSidebar .stButton > button:hover {
        background: #334155 !important;
        color: #f1f5f9 !important;
        transform: translateX(4px) !important;
    }
    
    .stSidebar .stButton > button:active {
        background: #3b82f6 !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Usar o sidebar nativo do Streamlit
    with st.sidebar:
        # Header da sidebar
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0; border-bottom: 1px solid #334155;">
            <h2 style="color: #f1f5f9; margin: 0; font-size: 1.5rem; font-weight: 700;">🚀 TasqAI</h2>
            <p style="color: #94a3b8; margin: 0.5rem 0 0 0; font-size: 0.9rem;">
                Sistema de Busca Inteligente
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações do usuário
        if is_authenticated():
            user = get_current_user()
            user_name = user.get("name", "Usuário")
            user_role = user.get("role", "user").title()
            user_initial = user_name[0].upper()
            
            st.markdown(f"""
            <div style="background: #334155; padding: 1rem; border-radius: 8px; margin: 1rem 0; border: 1px solid #475569;">
                <div style="display: flex; align-items: center; gap: 0.75rem;">
                    <div style="width: 40px; height: 40px; border-radius: 50%; background: #3b82f6; display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 1.1rem;">
                        {user_initial}
                    </div>
                    <div>
                        <p style="margin: 0; font-weight: 600; color: #f1f5f9; font-size: 1rem;">{user_name}</p>
                        <p style="margin: 0; color: #94a3b8; font-size: 0.85rem;">{user_role}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Navegação principal
        st.markdown("""
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
            Navegação
        </div>
        """, unsafe_allow_html=True)
        
        # Botões de navegação
        if st.button("📊 Dashboard", use_container_width=True, key="sidebar_dashboard"):
            st.session_state.current_page = "dashboard"
            st.rerun()
        
        if st.button("💬 Novo Chat", use_container_width=True, key="sidebar_chat"):
            save_current_chat_to_history()
            st.session_state.current_page = "chat"
            st.rerun()
        
        if st.button("📁 Gerenciar Arquivos", use_container_width=True, key="sidebar_files"):
            st.session_state.current_page = "files"
            st.rerun()
        
        if st.button("⚙️ Configurações", use_container_width=True, key="sidebar_settings"):
            st.session_state.current_page = "settings"
            st.rerun()
        
        # Página de gestão de usuários (apenas para admin)
        if is_authenticated() and is_admin():
            if st.button("👥 Gerenciar Usuários", use_container_width=True, key="sidebar_users"):
                st.session_state.current_page = "user_management"
                st.rerun()
        
        st.divider()
        
        # Histórico de chat
        st.markdown("""
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
            Histórico de Chats
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get("chat_history"):
            for i, chat in enumerate(reversed(st.session_state.get("chat_history", [])[-10:])):
                chat_name = chat.get('name', f"Chat {len(st.session_state.get('chat_history', [])) - i}")
                chat_date = chat.get('timestamp', 'Data não disponível')
                
                if st.button(f"💬 {chat_name}", key=f"sidebar_view_{i}", help=f"Data: {chat_date}"):
                        st.session_state.current_page = "chat"
                        st.session_state.selected_chat = chat
                        st.rerun()
        else:
            st.info("Nenhum chat ainda")
        
        st.divider()
        
        # Status do sistema
        st.markdown("""
        <div style="color: #94a3b8; font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 12px;">
            Status do Sistema
        </div>
        """, unsafe_allow_html=True)
        
        # Status online
        st.markdown("""
        <div style="display: flex; align-items: center; margin-bottom: 8px;">
            <span style="display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: #10b981; margin-right: 8px;"></span>
            <span style="color: #e2e8f0; font-size: 14px;">Sistema Online</span>
        </div>
        """, unsafe_allow_html=True)
        
        # Informações dos documentos
        doc_count = st.session_state.documents_status.get('documents_count', 0) if st.session_state.documents_status else 0
        last_update = st.session_state.documents_status.get('last_loaded', 'Nunca') if st.session_state.documents_status else 'Nunca'
        
        st.markdown(f"""
        <div style="color: #94a3b8; font-size: 12px; margin-bottom: 8px;">
            <p style="margin: 0;">📊 {doc_count} documentos carregados</p>
            <p style="margin: 0;">🔄 Última atualização: {last_update}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔄 Atualizar Status", use_container_width=True, key="sidebar_refresh"):
            with st.spinner("Atualizando..."):
                status = make_api_request("/documents/status")
                if status:
                    st.session_state.documents_status = status
                    st.success("Status atualizado!")
                st.rerun()
        
        st.divider()
        
        # Footer
        st.markdown("""
        <div style="text-align: center; color: #64748b; font-size: 11px;">
            <p style="margin: 0;">LLMChat v1.0.0</p>
            <p style="margin: 0;">Sistema de Busca com IA</p>
        </div>
        """, unsafe_allow_html=True)

def render_dashboard_page():
    """Renderiza a página principal do dashboard moderno"""
    # Verificar permissão de leitura
    if not has_permission("read_documents"):
        st.error("❌ Você não tem permissão para acessar esta funcionalidade.")
        return
    
    # Header do dashboard
    st.markdown("""
    <div class="modern-card" style="margin-bottom: 2rem;">
        <h1 style="margin: 0; color: var(--text-primary);">🚀 TasqAI Dashboard</h1>
        <p style="margin: 0.5rem 0 0 0; color: var(--text-secondary); font-size: 1.1rem;">
            Sistema inteligente de busca e análise de documentos
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">📊</div>
            <h3 style="margin: 0; color: var(--text-accent);">Documentos</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0; color: var(--text-primary);">
                {doc_count}
            </p>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Carregados no sistema</p>
        </div>
        """.format(doc_count=st.session_state.documents_status.get("documents_count", 0) if st.session_state.documents_status else 0), 
        unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">💬</div>
            <h3 style="margin: 0; color: var(--text-accent);">Conversas</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0; color: var(--text-primary);">
                {chat_count}
            </p>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Chats realizados</p>
        </div>
        """.format(chat_count=len(st.session_state.get("chat_history", []))), 
        unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">⚡</div>
            <h3 style="margin: 0; color: var(--text-accent);">Status</h3>
            <p style="font-size: 1.5rem; font-weight: bold; margin: 0.5rem 0; color: #10b981;">
                ✅ Ativo
            </p>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Sistema funcionando</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="modern-card" style="text-align: center; padding: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎯</div>
            <h3 style="margin: 0; color: var(--text-accent);">Precisão</h3>
            <p style="font-size: 2rem; font-weight: bold; margin: 0.5rem 0; color: var(--text-primary);">
                95%
            </p>
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">Taxa de acerto</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Seção de ações rápidas
    st.markdown("""
    <div class="modern-card" style="margin: 2rem 0;">
        <h2 style="margin: 0 0 1.5rem 0; color: var(--text-primary);">🚀 Ações Rápidas</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💬 Novo Chat", use_container_width=True, key="new_chat_dash"):
            st.session_state.current_page = "chat"
            st.rerun()
    
    with col2:
        if st.button("📁 Gerenciar Arquivos", use_container_width=True, key="manage_files_dash"):
            st.session_state.current_page = "files"
            st.rerun()
    
    with col3:
        if st.button("⚙️ Configurações", use_container_width=True, key="settings_dash"):
            st.session_state.current_page = "settings"
            st.rerun()
    
    # Seções removidas conforme solicitado:
    # - Atividades Recentes
    # - Chat Rápido  
    # - Resumo de conteúdo educacional

def render_chat_page():
    """Renderiza a página principal de chat"""
    # Verificar permissão de leitura
    if not has_permission("read_documents"):
        st.error("❌ Você não tem permissão para acessar esta funcionalidade.")
        return
    
    st.title("💬 Chat com IA")
    st.markdown("Faça perguntas sobre os documentos carregados no sistema.")
    
    # Verificar se há um chat selecionado do histórico
    if st.session_state.get('selected_chat'):
        # Exibir chat selecionado
        st.info(f"📚 Visualizando: {st.session_state.get('selected_chat', {}).get('name', 'Chat')}")
        
        # Botão para voltar ao chat atual
        if st.button("🆕 Voltar ao Chat Atual"):
            st.session_state.selected_chat = None
            st.rerun()
        
        # Exibir mensagens do chat selecionado
        for message in st.session_state.get('selected_chat', {}).get('messages', []):
            with st.chat_message("user"):
                st.write(message["query"])
            
            with st.chat_message("assistant"):
                st.write(message["answer"])
                documents_used = message.get("documents_used", [])
                
                # Garantir que documents_used seja sempre uma lista
                if not isinstance(documents_used, list):
                    documents_used = []
                
                if documents_used and len(documents_used) > 0:
                    with st.expander("📄 Documentos utilizados"):
                        for doc in documents_used:
                            if isinstance(doc, str):
                                st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                            else:
                                st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
    else:
        # Área de chat atual
        chat_container = st.container()
        
        with chat_container:
            # Exibir mensagens do chat atual
            for message in st.session_state.get("current_chat", []):
                with st.chat_message("user"):
                    st.write(message["query"])
                
                with st.chat_message("assistant"):
                    st.write(message["answer"])
                    documents_used = message.get("documents_used", [])
                    
                    # Garantir que documents_used seja sempre uma lista
                    if not isinstance(documents_used, list):
                        documents_used = []
                    
                    if documents_used and len(documents_used) > 0:
                        with st.expander("📄 Documentos utilizados"):
                            for doc in documents_used:
                                if isinstance(doc, str):
                                    st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                                else:
                                    st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
    
    # Input para nova pergunta
    st.markdown("### 💬 Nova Consulta")
    
    col1, col2 = st.columns([4, 1])
    
    with col1:
        prompt = st.text_area(
            "Digite sua pergunta aqui...",
            placeholder="Ex: Qual foi a importância da descoberta do Brasil?",
            height=120,
            key="prompt_input"
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Espaçamento
        send_button = st.button("🚀 Enviar", use_container_width=True, type="primary")
    
    if send_button and prompt.strip():
        # Adicionar pergunta do usuário
        with st.chat_message("user"):
            st.write(prompt)
        
        # Processar pergunta
        with st.chat_message("assistant"):
            with st.spinner("Processando sua pergunta..."):
                response = make_api_request("/query", "POST", {"query": prompt})
                
                if response and response.get("success"):
                    answer = response.get("answer", "Não foi possível obter uma resposta.")
                    documents_used = response.get("documents_used", [])
                    
                    # Garantir que documents_used seja sempre uma lista
                    if not isinstance(documents_used, list):
                        documents_used = []
                    
                    st.write(answer)
                    
                    if documents_used and len(documents_used) > 0:
                        with st.expander("📄 Documentos utilizados"):
                            for doc in documents_used:
                                if isinstance(doc, str):
                                    st.text(doc[:200] + "..." if len(doc) > 200 else doc)
                                else:
                                    st.text(str(doc)[:200] + "..." if len(str(doc)) > 200 else str(doc))
                    
                    # Salvar no chat atual
                    chat_entry = {
                        "query": prompt,
                        "answer": answer,
                        "documents_used": documents_used,
                        "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M")
                    }
                    if "current_chat" not in st.session_state:
                        st.session_state.current_chat = []
                    st.session_state.current_chat.append(chat_entry)
                    
                else:
                    st.error("❌ Não foi possível processar sua pergunta. Verifique se há documentos carregados.")

def render_files_page():
    """Renderiza a página de gerenciamento de arquivos"""
    # Verificar permissão de escrita
    if not has_permission("write_documents"):
        st.error("❌ Você não tem permissão para gerenciar arquivos.")
        return
    
    st.title("📁 Gerenciar Arquivos")
    st.markdown("Visualize e carregue documentos no sistema.")
    
    # Status dos documentos
    st.subheader("📊 Status dos Documentos")
    
    if st.button("🔄 Atualizar Status", key="refresh_status"):
        with st.spinner("Atualizando status..."):
            status = make_api_request("/documents/status")
            if status:
                st.session_state.documents_status = status
                st.rerun()
    
    if st.session_state.get("documents_status"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Documentos Carregados",
                st.session_state.get("documents_status", {}).get("documents_count", 0)
            )
        
        with col2:
            st.metric(
                "Sistema Ativo",
                "✅ Sim" if st.session_state.get("documents_status", {}).get("has_documents") else "❌ Não"
            )
        
        with col3:
            last_loaded = st.session_state.get("documents_status", {}).get("last_loaded", "Nunca")
            st.metric("Último Carregamento", last_loaded)
    
    st.divider()
    
    # Carregar novos documentos
    st.subheader("📤 Carregar Novo Documento")
    
    # Upload de arquivo
    uploaded_file = st.file_uploader(
        "Escolha um arquivo para carregar",
        type=['txt', 'pdf', 'docx', 'md'],
        help="Selecione um arquivo de texto, PDF, Word ou Markdown"
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Arquivo selecionado: {uploaded_file.name}")
        
        with st.form("load_document_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                chunk_size = st.number_input(
                    "Tamanho do Chunk",
                    min_value=100,
                    max_value=2000,
                    value=600,
                    help="Tamanho dos pedaços de texto para processamento"
                )
            
            with col2:
                chunk_overlap = st.slider(
                    "Sobreposição entre Chunks",
                    min_value=0,
                    max_value=200,
                    value=200,
                    help="Quantos caracteres se sobrepõem entre chunks consecutivos"
                )
            
            submitted = st.form_submit_button("📤 Carregar Documento", use_container_width=True)
            
            if submitted:
                with st.spinner("Carregando documento..."):
                    # Ler o conteúdo do arquivo
                    file_content = uploaded_file.read()
                    
                    # Enviar para o backend
                    try:
                        headers = get_auth_headers()
                        if not headers:
                            st.error("❌ Você precisa estar logado para carregar documentos")
                            return
                        
                        # Preparar dados para envio
                        files = {
                            'file': (uploaded_file.name, file_content, uploaded_file.type)
                        }
                        data = {
                            'chunk_size': chunk_size,
                            'chunk_overlap': chunk_overlap
                        }
                        
                        # Fazer requisição para o backend
                        response = requests.post(
                            "http://localhost:8000/documents/upload",
                            files=files,
                            data=data,
                            headers={"Authorization": headers["Authorization"]}
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            if result.get("success"):
                                st.success(f"✅ {result.get('message')}")
                                st.info(f"📊 {result.get('documents_count')} documentos processados")
                                # Atualizar status
                                status = make_api_request("/documents/status")
                                if status:
                                    st.session_state.documents_status = status
                                st.rerun()
                            else:
                                st.error("❌ Falha ao carregar documento")
                        else:
                            st.error(f"❌ Erro: {response.status_code}")
                    except Exception as e:
                        st.error(f"❌ Erro ao carregar documento: {str(e)}")
    
    # Alternativa: carregar por caminho (para arquivos no backend)
    st.subheader("📁 Ou carregar arquivo do servidor")
    
    with st.form("load_server_file_form"):
        file_path = st.text_input(
            "Caminho do Arquivo no Servidor",
            placeholder="ex: historia.txt ou /caminho/arquivo.pdf",
            help="Caminho do arquivo no servidor backend"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            chunk_size_server = st.number_input(
                "Tamanho do Chunk",
                min_value=100,
                max_value=2000,
                value=600,
                help="Tamanho dos pedaços de texto para processamento",
                key="chunk_size_server"
            )
        
        with col2:
            chunk_overlap_server = st.slider(
                "Sobreposição entre Chunks",
                min_value=0,
                max_value=200,
                value=200,
                help="Quantos caracteres se sobrepõem entre chunks consecutivos",
                key="chunk_overlap_server"
            )
        
        submitted_server = st.form_submit_button("📤 Carregar do Servidor", use_container_width=True)
        
        if submitted_server and file_path:
            with st.spinner("Carregando documento do servidor..."):
                response = make_api_request(
                    "/documents/load",
                    "POST",
                    {
                        "file_path": file_path,
                        "chunk_size": chunk_size_server,
                        "chunk_overlap": chunk_overlap_server
                    }
                )
                
                if response and response.get("success"):
                    st.success(f"✅ {response.get('message')}")
                    st.info(f"📊 {response.get('documents_count')} documentos processados")
                    # Atualizar status
                    status = make_api_request("/documents/status")
                    if status:
                        st.session_state.documents_status = status
                    st.rerun()
                else:
                    st.error("❌ Falha ao carregar documento")
        elif submitted_server and not file_path:
            st.error("❌ Por favor, informe o caminho do arquivo.")
    
    # Lista de arquivos disponíveis no backend
    st.subheader("📋 Arquivos Disponíveis no Servidor")
    
    # CSS para melhorar a aparência da tabela
    st.markdown("""
    <style>
    .files-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
        background: var(--bg-card);
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .files-table th {
        background: var(--bg-secondary);
        color: var(--text-primary);
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        border-bottom: 2px solid var(--bg-secondary);
    }
    
    .files-table td {
        padding: 1rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        color: var(--text-primary);
    }
    
    .files-table tr:hover {
        background: rgba(255, 255, 255, 0.05);
    }
    
    .files-table tr:last-child td {
        border-bottom: none;
    }
    
    .status-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    
    .status-concluido {
        background: #10b981;
        color: white;
    }
    
    .status-pendente {
        background: #f59e0b;
        color: white;
    }
    
    .file-icon {
        font-size: 1.2rem;
        margin-right: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Mostrar arquivos na pasta backend
    try:
        backend_files = []
        # Usar caminho absoluto para evitar problemas de diretório
        current_dir = os.path.dirname(os.path.abspath(__file__))
        backend_path = os.path.join(os.path.dirname(current_dir), "backend")
        
        st.info(f"🔍 Procurando arquivos em: {backend_path}")
        
        if os.path.exists(backend_path):
            st.success(f"✅ Pasta backend encontrada!")
            
            try:
                files = os.listdir(backend_path)
                st.info(f"📁 Total de arquivos na pasta: {len(files)}")
                
                for file in files:
                    if file.endswith(('.txt', '.pdf', '.docx', '.md')):
                        # Verificar se o arquivo está carregado no sistema
                        is_loaded = False
                        if st.session_state.get("documents_status", {}).get("has_documents"):
                            # Aqui você pode implementar uma verificação mais específica
                            # Por enquanto, vamos assumir que se há documentos carregados, alguns arquivos estão carregados
                            is_loaded = True
                        
                        file_path = os.path.join(backend_path, file)
                        file_size = 0
                        
                        try:
                            if os.path.exists(file_path):
                                file_size = os.path.getsize(file_path)
                        except Exception as e:
                            st.warning(f"⚠️ Erro ao obter tamanho do arquivo {file}: {str(e)}")
                        
                        backend_files.append({
                            'name': file,
                            'type': file.split('.')[-1].upper(),
                            'size': file_size,
                            'status': 'Concluído' if is_loaded else 'Pendente'
                        })
                        
            except Exception as e:
                st.error(f"❌ Erro ao listar arquivos da pasta backend: {str(e)}")
                return
        
        if backend_files:
            # Criar tabela HTML
            table_html = """
            <table class="files-table">
                <thead>
                    <tr>
                        <th>📄 Arquivo</th>
                        <th>📁 Tipo</th>
                        <th>📊 Tamanho</th>
                        <th>📈 Status</th>
                        <th>⚡ Ação</th>
                    </tr>
                </thead>
                <tbody>
            """
            
            for file_info in backend_files:
                # Determinar ícone baseado no tipo
                icon_map = {
                    'TXT': '📄',
                    'PDF': '📕',
                    'DOCX': '📘',
                    'MD': '📝'
                }
                icon = icon_map.get(file_info['type'], '📄')
                
                # Formatar tamanho
                size_kb = file_info['size'] / 1024
                size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
                
                # Determinar classe do status
                status_class = "status-concluido" if file_info['status'] == 'Concluído' else "status-pendente"
                
                table_html += f"""
                    <tr>
                        <td><span class="file-icon">{icon}</span>{file_info['name']}</td>
                        <td>{file_info['type']}</td>
                        <td>{size_str}</td>
                        <td><span class="status-badge {status_class}">{file_info['status']}</span></td>
                        <td>
                            <button onclick="loadFile('{file_info['name']}')" 
                                    style="background: var(--bg-accent); color: white; border: none; padding: 0.5rem 1rem; border-radius: 4px; cursor: pointer;">
                                📤 Carregar
                            </button>
                        </td>
                    </tr>
                """
            
            table_html += """
                </tbody>
            </table>
            """
            
            st.markdown(table_html, unsafe_allow_html=True)
            
            # JavaScript para carregar arquivos
            st.markdown("""
            <script>
            function loadFile(filename) {
                // Aqui você pode implementar a lógica de carregamento
                alert('Carregando arquivo: ' + filename);
                // Você pode fazer uma requisição AJAX aqui ou usar Streamlit
            }
            </script>
            """, unsafe_allow_html=True)
            
            # Botões de carregamento usando Streamlit
            st.markdown("### ⚡ Ações Rápidas")
            for file_info in backend_files:
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(f"📄 {file_info['name']}")
                with col2:
                    st.write(f"📁 {file_info['type']}")
                with col3:
                    status_color = "🟢" if file_info['status'] == 'Concluído' else "🟡"
                    st.write(f"{status_color} {file_info['status']}")
                with col4:
                    if st.button(f"Carregar", key=f"load_{file_info['name']}"):
                        with st.spinner(f"Carregando {file_info['name']}..."):
                            response = make_api_request(
                                "/documents/load",
                                "POST",
                                {
                                    "file_path": os.path.join(backend_path, file_info['name']),
                                    "chunk_size": 600,
                                    "chunk_overlap": 200
                                }
                            )
                            
                            if response and response.get("success"):
                                st.success(f"✅ {file_info['name']} carregado com sucesso!")
                                st.rerun()
                            else:
                                st.error(f"❌ Falha ao carregar {file_info['name']}")
        else:
            st.info("📭 Nenhum arquivo de documento encontrado na pasta backend.")
            st.info("💡 Tipos de arquivo suportados: .txt, .pdf, .docx, .md")
    except Exception as e:
        st.error(f"❌ Erro ao listar arquivos: {str(e)}")
        st.error("🔧 Verifique se a pasta backend existe e se você tem permissão para acessá-la.")
        import traceback
        st.code(traceback.format_exc())

def render_settings_page():
    """Renderiza a página de configurações"""
    st.title("⚙️ Configurações")
    
    st.subheader("🔐 Autenticação")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Token Atual:**")
        st.code(st.session_state.get("api_token", "Não configurado"))
    
    with col2:
        st.write("**Tokens Disponíveis:**")
        st.code("""
seu_token_secreto_aqui (Admin)
admin_token_123 (Admin)
user_token_456 (User)
        """)
    
    st.subheader("🌐 Configurações da API")
    
    api_url = st.text_input(
        "URL da API",
        value=API_BASE_URL,
        help="URL base da API backend"
    )
    
    st.subheader("💾 Gerenciar Histórico")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            if "chat_history" not in st.session_state:
                st.session_state.chat_history = []
            st.session_state.chat_history = []
            st.success("Histórico limpo!")
            st.rerun()
    
    with col2:
        if st.button("💾 Exportar Histórico", use_container_width=True):
            if st.session_state.get("chat_history"):
                # Criar arquivo JSON com histórico
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"chat_history_{timestamp}.json"
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.chat_history, f, ensure_ascii=False, indent=2)
                
                st.success(f"Histórico exportado para {filename}")
            else:
                st.info("Nenhum histórico para exportar")
    
    st.subheader("ℹ️ Informações do Sistema")
    
    # Testar conexão com API
    if st.button("🔍 Testar Conexão com API"):
        with st.spinner("Testando..."):
            health = make_api_request("/health")
            user_info = make_api_request("/user/me")
            
            if health and user_info:
                st.success("✅ API funcionando corretamente")
                
                with st.expander("Informações do Usuário"):
                    st.json(user_info)
            else:
                st.error("❌ Problemas na conexão com a API")

def main():
    """Função principal da aplicação"""
    
    # Salvar sessão automaticamente se autenticado
    if st.session_state.get("is_authenticated"):
        save_session_to_storage()
    
    # Verificar autenticação
    if not is_authenticated() and st.session_state.get("current_page") != "auth":
        st.session_state.current_page = "auth"
    
    # Renderizar página de autenticação se necessário
    if st.session_state.get("current_page") == "auth":
        render_auth_page()
        return
    
    # Renderizar menu superior
    render_top_menu()
    
    # Renderizar sidebar apenas se autenticado
    render_sidebar()
    
    # Renderizar página principal baseada na seleção
    if st.session_state.get("current_page") == "dashboard":
        render_dashboard_page()
    elif st.session_state.get("current_page") == "chat":
        render_chat_page()
    elif st.session_state.get("current_page") == "files":
        render_files_page()
    elif st.session_state.get("current_page") == "settings":
        render_settings_page()
    elif st.session_state.get("current_page") == "user_management":
        render_user_management_page()
    elif st.session_state.get("current_page") == "profile":
        render_profile_page()
    else:
        # Página padrão - Dashboard
        render_dashboard_page()

if __name__ == "__main__":
    main()
