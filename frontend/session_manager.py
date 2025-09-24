"""
Gerenciador de Sessão Robusto para TasqAI
Implementa uma estratégia de sessão de 24 horas com múltiplas camadas de persistência
"""

import streamlit as st
import requests
import json
import time
import hashlib
import hmac
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
import os

# Configurações da API
API_BASE_URL = "http://localhost:8000"

class SessionManager:
    """Gerenciador de sessão robusto com múltiplas camadas de persistência"""
    
    def __init__(self):
        self.session_keys = [
            'is_authenticated', 'auth_token', 'user', 'current_page', 
            'session_id', 'login_timestamp', 'last_activity', 'session_hash'
        ]
        self.session_duration = 24 * 60 * 60  # 24 horas em segundos
        self.refresh_interval = 30 * 60  # 30 minutos
        self.max_idle_time = 2 * 60 * 60  # 2 horas de inatividade
        
    def generate_session_id(self, user_data: Dict) -> str:
        """Gera um ID único de sessão baseado nos dados do usuário"""
        user_string = f"{user_data.get('email', '')}{user_data.get('id', '')}{time.time()}"
        return hashlib.sha256(user_string.encode()).hexdigest()[:16]
    
    def generate_session_hash(self, session_data: Dict) -> str:
        """Gera um hash de verificação da sessão"""
        data_string = f"{session_data.get('auth_token', '')}{session_data.get('user', {}).get('id', '')}{session_data.get('login_timestamp', 0)}"
        return hashlib.sha256(data_string.encode()).hexdigest()[:32]
    
    def is_session_valid(self, session_data: Dict) -> bool:
        """Verifica se a sessão é válida baseada em múltiplos critérios"""
        if not session_data:
            return False
        
        current_time = time.time()
        login_time = session_data.get('login_timestamp', 0)
        last_activity = session_data.get('last_activity', login_time)
        
        # Verificar se a sessão não expirou (24 horas)
        if current_time - login_time > self.session_duration:
            return False
        
        # Verificar se não houve inatividade excessiva (2 horas)
        if current_time - last_activity > self.max_idle_time:
            return False
        
        # Verificar se o hash da sessão é válido
        expected_hash = self.generate_session_hash(session_data)
        if session_data.get('session_hash') != expected_hash:
            return False
        
        return True
    
    def save_session_to_storage(self, session_data: Dict):
        """Salva dados da sessão no localStorage via JavaScript"""
        # Gerar hash de verificação
        session_data['session_hash'] = self.generate_session_hash(session_data)
        
        js_code = f"""
        <script>
        // Salvar dados da sessão no localStorage
        const sessionData = {json.dumps(session_data)};
        
        // Salvar cada chave individualmente
        Object.keys(sessionData).forEach(key => {{
            localStorage.setItem('tasqai_' + key, JSON.stringify(sessionData[key]));
        }});
        
        // Salvar timestamp de salvamento
        localStorage.setItem('tasqai_save_timestamp', Date.now());
        
        // Configurar listener para detectar mudanças na aba
        window.addEventListener('beforeunload', function() {{
            localStorage.setItem('tasqai_last_activity', Date.now());
        }});
        
        // Configurar listener para detectar foco na aba
        window.addEventListener('focus', function() {{
            localStorage.setItem('tasqai_last_activity', Date.now());
        }});
        
        console.log('Sessão salva com sucesso');
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    
    def clear_session_from_storage(self):
        """Limpa dados da sessão do localStorage via JavaScript"""
        js_code = """
        <script>
        // Limpar todos os dados de sessão
        const sessionKeys = [
            'is_authenticated', 'auth_token', 'user', 'current_page', 
            'session_id', 'login_timestamp', 'last_activity', 'session_hash',
            'save_timestamp', 'last_activity'
        ];
        
        sessionKeys.forEach(key => {
            localStorage.removeItem('tasqai_' + key);
        });
        
        // Limpar também sessionStorage
        sessionStorage.clear();
        
        console.log('Sessão limpa com sucesso');
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    
    def restore_session_from_storage(self) -> Optional[Dict]:
        """Restaura sessão do localStorage via JavaScript"""
        js_code = """
        <script>
        // Verificar e restaurar sessão do localStorage
        function restoreSession() {
            try {
                const isAuth = localStorage.getItem('tasqai_is_authenticated');
                const token = localStorage.getItem('tasqai_auth_token');
                const user = localStorage.getItem('tasqai_user');
                const sessionId = localStorage.getItem('tasqai_session_id');
                const loginTime = localStorage.getItem('tasqai_login_timestamp');
                const lastActivity = localStorage.getItem('tasqai_last_activity');
                const sessionHash = localStorage.getItem('tasqai_session_hash');
                
                if (isAuth === 'true' && token && user && sessionId) {
                    const now = Date.now();
                    const loginTimestamp = parseInt(loginTime) || 0;
                    const lastActivityTime = parseInt(lastActivity) || loginTimestamp;
                    
                    // Verificar se a sessão não expirou (24 horas)
                    const sessionAge = now - loginTimestamp;
                    const maxSessionAge = 24 * 60 * 60 * 1000; // 24 horas
                    
                    // Verificar se não houve inatividade excessiva (2 horas)
                    const idleTime = now - lastActivityTime;
                    const maxIdleTime = 2 * 60 * 60 * 1000; // 2 horas
                    
                    if (sessionAge < maxSessionAge && idleTime < maxIdleTime) {
                        // Sessão válida, restaurar
                        const sessionData = {
                            is_authenticated: true,
                            auth_token: token,
                            user: JSON.parse(user),
                            session_id: sessionId,
                            login_timestamp: loginTimestamp / 1000,
                            last_activity: lastActivityTime / 1000,
                            session_hash: sessionHash
                        };
                        
                        // Enviar dados para o Python via postMessage
                        window.parent.postMessage({
                            type: 'restore_session',
                            data: sessionData
                        }, '*');
                        
                        // Atualizar timestamp de atividade
                        localStorage.setItem('tasqai_last_activity', now);
                        
                        return true;
                    } else {
                        // Sessão expirada, limpar
                        console.log('Sessão expirada, limpando dados');
                        const sessionKeys = [
                            'is_authenticated', 'auth_token', 'user', 'current_page', 
                            'session_id', 'login_timestamp', 'last_activity', 'session_hash'
                        ];
                        sessionKeys.forEach(key => {
                            localStorage.removeItem('tasqai_' + key);
                        });
                    }
                }
            } catch (e) {
                console.warn('Erro ao restaurar sessão:', e);
            }
            return false;
        }
        
        // Executar restauração
        restoreSession();
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
        return None
    
    def create_session(self, user_data: Dict, auth_token: str) -> Dict:
        """Cria uma nova sessão"""
        current_time = time.time()
        session_id = self.generate_session_id(user_data)
        
        session_data = {
            'is_authenticated': True,
            'auth_token': auth_token,
            'user': user_data,
            'current_page': 'dashboard',
            'session_id': session_id,
            'login_timestamp': current_time,
            'last_activity': current_time,
            'session_hash': None  # Será gerado abaixo
        }
        
        # Gerar hash da sessão
        session_data['session_hash'] = self.generate_session_hash(session_data)
        
        # Salvar no session state do Streamlit
        for key, value in session_data.items():
            st.session_state[key] = value
        
        # Salvar no localStorage
        self.save_session_to_storage(session_data)
        
        return session_data
    
    def update_activity(self):
        """Atualiza timestamp de última atividade"""
        current_time = time.time()
        st.session_state['last_activity'] = current_time
        
        # Atualizar no localStorage
        js_code = f"""
        <script>
        localStorage.setItem('tasqai_last_activity', {int(current_time * 1000)});
        </script>
        """
        st.markdown(js_code, unsafe_allow_html=True)
    
    def refresh_session(self) -> bool:
        """Atualiza a sessão se necessário"""
        if not st.session_state.get('is_authenticated'):
            return False
        
        current_time = time.time()
        last_check = st.session_state.get('last_auth_check', 0)
        
        # Verificar se precisa atualizar (a cada 30 minutos)
        if current_time - last_check > self.refresh_interval:
            try:
                # Verificar com o servidor
                headers = {"Authorization": f"Bearer {st.session_state.get('auth_token')}"}
                response = requests.get(f"{API_BASE_URL}/auth/me", headers=headers, timeout=5)
                
                if response.status_code == 200:
                    st.session_state['last_auth_check'] = current_time
                    self.update_activity()
                    
                    # Atualizar dados do usuário se necessário
                    user_data = response.json()
                    if user_data.get("user"):
                        st.session_state['user'] = user_data["user"]
                        self.save_session_to_storage({
                            'is_authenticated': True,
                            'auth_token': st.session_state.get('auth_token'),
                            'user': st.session_state.get('user'),
                            'current_page': st.session_state.get('current_page', 'dashboard'),
                            'session_id': st.session_state.get('session_id'),
                            'login_timestamp': st.session_state.get('login_timestamp'),
                            'last_activity': current_time
                        })
                    return True
                else:
                    # Token inválido, limpar sessão
                    self.clear_session()
                    return False
            except Exception as e:
                # Em caso de erro, manter sessão por mais tempo
                st.session_state['last_auth_check'] = current_time
                self.update_activity()
                return True
        
        return True
    
    def clear_session(self):
        """Limpa completamente a sessão"""
        # Limpar session state
        for key in self.session_keys:
            if key in st.session_state:
                del st.session_state[key]
        
        # Limpar localStorage
        self.clear_session_from_storage()
    
    def is_authenticated(self) -> bool:
        """Verifica se o usuário está autenticado com validação robusta"""
        if not st.session_state.get('is_authenticated', False):
            return False
        
        # Verificar se a sessão é válida
        session_data = {
            'auth_token': st.session_state.get('auth_token'),
            'user': st.session_state.get('user'),
            'login_timestamp': st.session_state.get('login_timestamp'),
            'session_hash': st.session_state.get('session_hash')
        }
        
        if not self.is_session_valid(session_data):
            self.clear_session()
            return False
        
        # Atualizar sessão se necessário
        return self.refresh_session()

# Instância global do gerenciador de sessão
session_manager = SessionManager()

def initialize_session():
    """Inicializa a sessão com restauração automática"""
    # Verificar se já foi inicializado
    if st.session_state.get('session_initialized'):
        return
    
    # Tentar restaurar sessão do localStorage
    session_manager.restore_session_from_storage()
    
    # Marcar como inicializado
    st.session_state['session_initialized'] = True

def login_user(email: str, password: str) -> bool:
    """Realiza login do usuário com criação de sessão robusta"""
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        }, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("token"):
                # Criar sessão robusta
                session_manager.create_session(data["user"], data["token"])
                return True
        
        return False
    except Exception as e:
        st.error(f"Erro ao fazer login: {str(e)}")
        return False

def logout_user():
    """Realiza logout com limpeza completa da sessão"""
    # Fazer logout na API se possível
    if st.session_state.get("auth_token"):
        try:
            headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
            requests.post(f"{API_BASE_URL}/auth/logout", headers=headers, timeout=5)
        except:
            pass  # Ignorar erros de logout
    
    # Limpar sessão completamente
    session_manager.clear_session()
    
    # Redirecionar para login
    st.session_state['current_page'] = 'auth'
    st.rerun()

def get_current_user() -> Optional[Dict]:
    """Retorna dados do usuário atual"""
    return st.session_state.get('user')

def has_permission(permission: str) -> bool:
    """Verifica se o usuário tem uma permissão específica"""
    user = get_current_user()
    if not user:
        return False
    
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

def get_auth_headers() -> Dict[str, str]:
    """Retorna headers de autenticação para requisições"""
    token = st.session_state.get("auth_token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def is_authenticated() -> bool:
    """Verifica se o usuário está autenticado (função wrapper)"""
    return session_manager.is_authenticated()
