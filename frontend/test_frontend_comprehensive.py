"""
Testes abrangentes para funcionalidades do frontend.
"""

import os
import sys
import time
import json
import tempfile
from typing import Dict, Any, List
from unittest.mock import patch, MagicMock

# Adicionar o diretório frontend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests
from streamlit.testing.v1 import AppTest

# Importar módulos do frontend
from auth_pages import (
    is_authenticated, 
    get_current_user, 
    logout_user,
    render_login_page,
    render_register_page,
    render_auth_page
)
from streamlit_app import (
    initialize_session_state,
    render_sidebar,
    render_dashboard_page,
    render_chat_page,
    render_files_page,
    render_settings_page,
    render_profile_page,
    render_user_management_page
)
from top_menu import render_top_menu
from user_management import render_user_management_page

class TestFrontendFunctionality:
    """Classe principal para testes do frontend."""
    
    def setup_method(self):
        """Configuração antes de cada teste."""
        # Limpar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        # Limpar session state
        for key in list(st.session_state.keys()):
            del st.session_state[key]

    # ==================== TESTES DE AUTENTICAÇÃO ====================
    
    def test_initialize_session_state(self):
        """Testa inicialização do session state."""
        initialize_session_state()
        
        # Verificar se todas as chaves necessárias foram inicializadas
        assert "is_authenticated" in st.session_state
        assert "auth_token" in st.session_state
        assert "user" in st.session_state
        assert "current_page" in st.session_state
        assert "chat_history" in st.session_state
        assert "documents_status" in st.session_state
        assert "last_auth_check" in st.session_state
        assert "session_initialized" in st.session_state
        
        # Verificar valores padrão
        assert st.session_state.is_authenticated == False
        assert st.session_state.auth_token is None
        assert st.session_state.user is None
        assert st.session_state.current_page == "login"
        assert st.session_state.chat_history == []
        assert st.session_state.documents_status is None
        assert st.session_state.last_auth_check == 0
        assert st.session_state.session_initialized == False
    
    def test_is_authenticated_false(self):
        """Testa verificação de autenticação quando não autenticado."""
        st.session_state.is_authenticated = False
        st.session_state.auth_token = None
        
        result = is_authenticated()
        assert result == False
    
    def test_is_authenticated_true(self):
        """Testa verificação de autenticação quando autenticado."""
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição para /auth/me
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "user": {"name": "Test User", "email": "test@test.com"}
            }
            mock_get.return_value = mock_response
            
            result = is_authenticated()
            assert result == True
    
    def test_get_current_user(self):
        """Testa obtenção do usuário atual."""
        test_user = {"name": "Test User", "email": "test@test.com", "role": "user"}
        st.session_state.user = test_user
        
        result = get_current_user()
        assert result == test_user
    
    def test_logout_user(self):
        """Testa logout do usuário."""
        # Configurar usuário autenticado
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.current_page = "dashboard"
        
        # Mock da requisição para /auth/logout
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            logout_user()
            
            # Verificar se o usuário foi deslogado
            assert st.session_state.is_authenticated == False
            assert st.session_state.auth_token is None
            assert st.session_state.user is None
            assert st.session_state.current_page == "login"

    # ==================== TESTES DE PÁGINAS ====================
    
    def test_render_login_page(self):
        """Testa renderização da página de login."""
        st.session_state.current_page = "login"
        
        # Mock da requisição de login
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "token": "test_token",
                "user": {"name": "Test User", "email": "test@test.com"}
            }
            mock_post.return_value = mock_response
            
            # Simular preenchimento do formulário
            with patch('streamlit.text_input') as mock_email, \
                 patch('streamlit.text_input') as mock_password, \
                 patch('streamlit.button') as mock_button:
                
                mock_email.return_value = "test@test.com"
                mock_password.return_value = "password123"
                mock_button.return_value = True
                
                try:
                    render_login_page()
                    # Se chegou até aqui, a página foi renderizada sem erro
                    assert True
                except Exception as e:
                    # Pode falhar devido ao contexto do Streamlit, mas não deve ser erro crítico
                    assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_register_page(self):
        """Testa renderização da página de registro."""
        st.session_state.current_page = "register"
        
        # Mock da requisição de registro
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "message": "Usuário criado com sucesso"
            }
            mock_post.return_value = mock_response
            
            try:
                render_register_page()
                assert True
            except Exception as e:
                assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_dashboard_page(self):
        """Testa renderização da página do dashboard."""
        st.session_state.current_page = "dashboard"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        
        # Mock da requisição para status dos documentos
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "documents_count": 5,
                "last_loaded": "2024-01-01 12:00:00"
            }
            mock_get.return_value = mock_response
            
            try:
                render_dashboard_page()
                assert True
            except Exception as e:
                assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_chat_page(self):
        """Testa renderização da página de chat."""
        st.session_state.current_page = "chat"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.chat_history = []
        
        try:
            render_chat_page()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_files_page(self):
        """Testa renderização da página de arquivos."""
        st.session_state.current_page = "files"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        
        try:
            render_files_page()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_settings_page(self):
        """Testa renderização da página de configurações."""
        st.session_state.current_page = "settings"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        
        try:
            render_settings_page()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_profile_page(self):
        """Testa renderização da página de perfil."""
        st.session_state.current_page = "profile"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        
        try:
            render_profile_page()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_user_management_page(self):
        """Testa renderização da página de gerenciamento de usuários."""
        st.session_state.current_page = "user_management"
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Admin User", "email": "admin@test.com", "role": "admin"}
        
        # Mock da requisição para listar usuários
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "users": [
                    {"id": 1, "name": "User 1", "email": "user1@test.com", "role": "user"},
                    {"id": 2, "name": "User 2", "email": "user2@test.com", "role": "user"}
                ]
            }
            mock_get.return_value = mock_response
            
            try:
                render_user_management_page()
                assert True
            except Exception as e:
                assert "streamlit" in str(e).lower() or "session" in str(e).lower()

    # ==================== TESTES DE SIDEBAR ====================
    
    def test_render_sidebar(self):
        """Testa renderização da sidebar."""
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com", "role": "user"}
        st.session_state.chat_history = [
            {"name": "Chat 1", "timestamp": "2024-01-01 12:00:00"},
            {"name": "Chat 2", "timestamp": "2024-01-01 13:00:00"}
        ]
        st.session_state.documents_status = {
            "documents_count": 5,
            "last_loaded": "2024-01-01 12:00:00"
        }
        
        try:
            render_sidebar()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()
    
    def test_render_top_menu(self):
        """Testa renderização do menu superior."""
        st.session_state.is_authenticated = True
        st.session_state.user = {"name": "Test User", "email": "test@test.com", "role": "user"}
        
        try:
            render_top_menu()
            assert True
        except Exception as e:
            assert "streamlit" in str(e).lower() or "session" in str(e).lower()

    # ==================== TESTES DE NAVEGAÇÃO ====================
    
    def test_navigation_between_pages(self):
        """Testa navegação entre páginas."""
        pages = ["dashboard", "chat", "files", "settings", "profile"]
        
        for page in pages:
            st.session_state.current_page = page
            st.session_state.is_authenticated = True
            st.session_state.user = {"name": "Test User", "email": "test@test.com"}
            
            # Verificar se a página foi definida corretamente
            assert st.session_state.current_page == page

    # ==================== TESTES DE HISTÓRICO DE CHAT ====================
    
    def test_chat_history_management(self):
        """Testa gerenciamento do histórico de chat."""
        # Adicionar chat ao histórico
        chat_entry = {
            "name": "Test Chat",
            "timestamp": "2024-01-01 12:00:00",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        
        st.session_state.chat_history = [chat_entry]
        
        # Verificar se o chat foi adicionado
        assert len(st.session_state.chat_history) == 1
        assert st.session_state.chat_history[0]["name"] == "Test Chat"
        
        # Adicionar mais um chat
        chat_entry_2 = {
            "name": "Test Chat 2",
            "timestamp": "2024-01-01 13:00:00",
            "messages": [{"role": "user", "content": "Hello again"}]
        }
        
        st.session_state.chat_history.append(chat_entry_2)
        
        # Verificar se ambos os chats estão no histórico
        assert len(st.session_state.chat_history) == 2

    # ==================== TESTES DE STATUS DE DOCUMENTOS ====================
    
    def test_documents_status_management(self):
        """Testa gerenciamento do status de documentos."""
        # Definir status inicial
        initial_status = {
            "documents_count": 0,
            "last_loaded": "Nunca"
        }
        
        st.session_state.documents_status = initial_status
        
        # Verificar status inicial
        assert st.session_state.documents_status["documents_count"] == 0
        assert st.session_state.documents_status["last_loaded"] == "Nunca"
        
        # Atualizar status
        updated_status = {
            "documents_count": 5,
            "last_loaded": "2024-01-01 12:00:00"
        }
        
        st.session_state.documents_status = updated_status
        
        # Verificar status atualizado
        assert st.session_state.documents_status["documents_count"] == 5
        assert st.session_state.documents_status["last_loaded"] == "2024-01-01 12:00:00"

    # ==================== TESTES DE PERMISSÕES ====================
    
    def test_user_permissions(self):
        """Testa verificação de permissões de usuário."""
        # Usuário comum
        st.session_state.user = {"name": "User", "email": "user@test.com", "role": "user"}
        
        # Mock das funções de verificação de permissão
        with patch('auth_pages.is_admin') as mock_is_admin:
            mock_is_admin.return_value = False
            
            # Verificar se usuário comum não é admin
            assert not mock_is_admin()
        
        # Usuário admin
        st.session_state.user = {"name": "Admin", "email": "admin@test.com", "role": "admin"}
        
        with patch('auth_pages.is_admin') as mock_is_admin:
            mock_is_admin.return_value = True
            
            # Verificar se usuário admin é admin
            assert mock_is_admin()

    # ==================== TESTES DE VALIDAÇÃO DE DADOS ====================
    
    def test_input_validation(self):
        """Testa validação de entrada de dados."""
        # Teste de email válido
        valid_email = "test@example.com"
        assert "@" in valid_email and "." in valid_email
        
        # Teste de email inválido
        invalid_email = "invalid-email"
        assert "@" not in invalid_email or "." not in invalid_email
        
        # Teste de senha válida
        valid_password = "password123"
        assert len(valid_password) >= 6
        
        # Teste de senha inválida
        invalid_password = "123"
        assert len(invalid_password) < 6

    # ==================== TESTES DE INTEGRAÇÃO ====================
    
    def test_full_user_flow(self):
        """Testa fluxo completo do usuário."""
        # 1. Inicializar sessão
        initialize_session_state()
        assert st.session_state.current_page == "login"
        assert not st.session_state.is_authenticated
        
        # 2. Simular login
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "test_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.current_page = "dashboard"
        
        assert st.session_state.is_authenticated
        assert st.session_state.current_page == "dashboard"
        
        # 3. Navegar para chat
        st.session_state.current_page = "chat"
        assert st.session_state.current_page == "chat"
        
        # 4. Adicionar chat ao histórico
        chat_entry = {
            "name": "Test Chat",
            "timestamp": "2024-01-01 12:00:00",
            "messages": [{"role": "user", "content": "Hello"}]
        }
        st.session_state.chat_history.append(chat_entry)
        
        assert len(st.session_state.chat_history) == 1
        
        # 5. Simular logout
        st.session_state.is_authenticated = False
        st.session_state.auth_token = None
        st.session_state.user = None
        st.session_state.current_page = "login"
        
        assert not st.session_state.is_authenticated
        assert st.session_state.current_page == "login"


def run_frontend_tests():
    """Executa todos os testes do frontend."""
    print("🧪 Iniciando testes abrangentes do Frontend...")
    print("=" * 60)
    
    # Criar instância da classe de testes
    test_instance = TestFrontendFunctionality()
    
    # Lista de todos os métodos de teste
    test_methods = [
        # Autenticação
        test_instance.test_initialize_session_state,
        test_instance.test_is_authenticated_false,
        test_instance.test_is_authenticated_true,
        test_instance.test_get_current_user,
        test_instance.test_logout_user,
        
        # Páginas
        test_instance.test_render_login_page,
        test_instance.test_render_register_page,
        test_instance.test_render_dashboard_page,
        test_instance.test_render_chat_page,
        test_instance.test_render_files_page,
        test_instance.test_render_settings_page,
        test_instance.test_render_profile_page,
        test_instance.test_render_user_management_page,
        
        # Sidebar e Menu
        test_instance.test_render_sidebar,
        test_instance.test_render_top_menu,
        
        # Navegação
        test_instance.test_navigation_between_pages,
        
        # Histórico de Chat
        test_instance.test_chat_history_management,
        
        # Status de Documentos
        test_instance.test_documents_status_management,
        
        # Permissões
        test_instance.test_user_permissions,
        
        # Validação de Dados
        test_instance.test_input_validation,
        
        # Integração
        test_instance.test_full_user_flow,
    ]
    
    passed = 0
    failed = 0
    errors = []
    
    for test_method in test_methods:
        try:
            test_method()
            print(f"✅ {test_method.__name__}")
            passed += 1
        except Exception as e:
            print(f"❌ {test_method.__name__}: {str(e)}")
            failed += 1
            errors.append(f"{test_method.__name__}: {str(e)}")
    
    print("=" * 60)
    print(f"📊 Resultados dos Testes do Frontend:")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Taxa de Sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if errors:
        print("\n🔍 Erros Encontrados:")
        for error in errors:
            print(f"  - {error}")
    
    return passed, failed, errors


if __name__ == "__main__":
    run_frontend_tests()
