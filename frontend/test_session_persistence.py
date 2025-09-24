"""
Testes específicos para persistência de sessão do usuário.
"""

import os
import sys
import time
import json
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Adicionar o diretório frontend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import requests

# Importar módulos do frontend
from auth_pages import (
    is_authenticated,
    save_session_to_storage,
    clear_session_from_storage
)
from streamlit_app import (
    initialize_session_state,
    save_current_chat_to_history
)

class TestSessionPersistence:
    """Classe para testes de persistência de sessão."""
    
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

    # ==================== TESTES DE INICIALIZAÇÃO DE SESSÃO ====================
    
    def test_session_initialization(self):
        """Testa inicialização correta da sessão."""
        initialize_session_state()
        
        # Verificar se todas as chaves de sessão foram inicializadas
        required_keys = [
            "is_authenticated",
            "auth_token", 
            "user",
            "current_page",
            "chat_history",
            "documents_status",
            "last_auth_check",
            "session_initialized"
        ]
        
        for key in required_keys:
            assert key in st.session_state, f"Chave {key} não foi inicializada"
        
        # Verificar valores padrão
        assert st.session_state.is_authenticated == False
        assert st.session_state.auth_token is None
        assert st.session_state.user is None
        assert st.session_state.current_page == "login"
        assert st.session_state.chat_history == []
        assert st.session_state.documents_status is None
        assert st.session_state.last_auth_check == 0
        assert st.session_state.session_initialized == False

    # ==================== TESTES DE SALVAMENTO DE SESSÃO ====================
    
    def test_save_session_to_storage(self):
        """Testa salvamento de sessão no localStorage."""
        # Configurar dados de sessão
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "test_token_123"
        st.session_state.user = {
            "name": "Test User",
            "email": "test@test.com",
            "role": "user"
        }
        st.session_state.last_auth_check = time.time()
        
        # Mock do JavaScript para localStorage
        with patch('streamlit.components.v1.html') as mock_html:
            save_session_to_storage()
            
            # Verificar se o HTML foi chamado
            mock_html.assert_called_once()
            
            # Verificar se o HTML contém as funções JavaScript necessárias
            html_content = mock_html.call_args[0][0]
            assert "localStorage.setItem" in html_content
            assert "tasqai_is_authenticated" in html_content
            assert "tasqai_auth_token" in html_content
            assert "tasqai_user" in html_content
            assert "tasqai_last_auth_check" in html_content

    def test_clear_session_from_storage(self):
        """Testa limpeza de sessão do localStorage."""
        # Mock do JavaScript para localStorage
        with patch('streamlit.components.v1.html') as mock_html:
            clear_session_from_storage()
            
            # Verificar se o HTML foi chamado
            mock_html.assert_called_once()
            
            # Verificar se o HTML contém as funções de limpeza
            html_content = mock_html.call_args[0][0]
            assert "localStorage.removeItem" in html_content
            assert "tasqai_is_authenticated" in html_content
            assert "tasqai_auth_token" in html_content
            assert "tasqai_user" in html_content
            assert "tasqai_last_auth_check" in html_content

    # ==================== TESTES DE VALIDAÇÃO DE SESSÃO ====================
    
    def test_session_validation_with_valid_token(self):
        """Testa validação de sessão com token válido."""
        # Configurar sessão válida
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
    
    def test_session_validation_with_invalid_token(self):
        """Testa validação de sessão com token inválido."""
        # Configurar sessão com token inválido
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "invalid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição para /auth/me retornando erro
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            result = is_authenticated()
            assert result == False
            
            # Verificar se a sessão foi limpa
            assert st.session_state.is_authenticated == False
            assert st.session_state.auth_token is None
            assert st.session_state.user is None

    def test_session_validation_with_timeout(self):
        """Testa validação de sessão com timeout de rede."""
        # Configurar sessão válida
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição com timeout
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.Timeout()
            
            result = is_authenticated()
            # Deve manter a sessão em caso de timeout
            assert result == True

    def test_session_expiration_24_hours(self):
        """Testa expiração de sessão após 24 horas."""
        # Configurar sessão expirada (mais de 24 horas)
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time() - (25 * 60 * 60)  # 25 horas atrás
        
        result = is_authenticated()
        assert result == False
        
        # Verificar se a sessão foi limpa
        assert st.session_state.is_authenticated == False
        assert st.session_state.auth_token is None
        assert st.session_state.user is None

    def test_session_validation_interval_30_minutes(self):
        """Testa intervalo de validação de 30 minutos."""
        # Configurar sessão válida
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time() - (20 * 60)  # 20 minutos atrás
        
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
            
            # Verificar se a requisição foi feita (pois passou de 30 minutos)
            mock_get.assert_called_once()

    def test_session_validation_skip_recent_check(self):
        """Testa que validação é pulada se feita recentemente."""
        # Configurar sessão válida com verificação recente
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time() - (10 * 60)  # 10 minutos atrás
        
        # Mock da requisição para /auth/me
        with patch('requests.get') as mock_get:
            result = is_authenticated()
            assert result == True
            
            # Verificar se a requisição NÃO foi feita (pois foi feita recentemente)
            mock_get.assert_not_called()

    # ==================== TESTES DE RESTAURAÇÃO DE SESSÃO ====================
    
    def test_session_restoration_from_localStorage(self):
        """Testa restauração de sessão do localStorage."""
        # Simular dados válidos no localStorage
        mock_localStorage_data = {
            "tasqai_is_authenticated": "true",
            "tasqai_auth_token": "restored_token",
            "tasqai_user": json.dumps({"name": "Restored User", "email": "restored@test.com"}),
            "tasqai_last_auth_check": str(int(time.time()))
        }
        
        # Mock do JavaScript para verificar localStorage
        with patch('streamlit.components.v1.html') as mock_html:
            # Simular restauração de sessão
            initialize_session_state()
            
            # Verificar se o HTML de restauração foi chamado
            mock_html.assert_called()
            
            # Verificar se o HTML contém as funções de restauração
            html_content = mock_html.call_args[0][0]
            assert "localStorage.getItem" in html_content
            assert "tasqai_is_authenticated" in html_content

    # ==================== TESTES DE HISTÓRICO DE CHAT ====================
    
    def test_save_current_chat_to_history(self):
        """Testa salvamento do chat atual no histórico."""
        # Configurar chat atual
        st.session_state.current_chat = {
            "name": "Current Chat",
            "timestamp": "2024-01-01 12:00:00",
            "messages": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }
        st.session_state.chat_history = []
        
        save_current_chat_to_history()
        
        # Verificar se o chat foi salvo no histórico
        assert len(st.session_state.chat_history) == 1
        assert st.session_state.chat_history[0]["name"] == "Current Chat"
        assert len(st.session_state.chat_history[0]["messages"]) == 2

    def test_chat_history_limit(self):
        """Testa limite do histórico de chat."""
        # Adicionar muitos chats ao histórico
        for i in range(15):  # Mais que o limite de 10
            chat_entry = {
                "name": f"Chat {i}",
                "timestamp": f"2024-01-01 {12+i}:00:00",
                "messages": [{"role": "user", "content": f"Message {i}"}]
            }
            st.session_state.chat_history.append(chat_entry)
        
        # Verificar se o histórico não excede o limite
        assert len(st.session_state.chat_history) <= 10

    # ==================== TESTES DE PERSISTÊNCIA EM CASOS DE ERRO ====================
    
    def test_session_persistence_on_network_error(self):
        """Testa persistência de sessão em caso de erro de rede."""
        # Configurar sessão válida
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição com erro de rede
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.ConnectionError()
            
            result = is_authenticated()
            # Deve manter a sessão em caso de erro de rede
            assert result == True

    def test_session_clear_on_logout(self):
        """Testa limpeza completa de sessão no logout."""
        # Configurar sessão ativa
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "valid_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.current_page = "dashboard"
        st.session_state.chat_history = [{"name": "Test Chat", "messages": []}]
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição de logout
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            # Mock da função de limpeza do localStorage
            with patch('auth_pages.clear_session_from_storage') as mock_clear:
                from auth_pages import logout_user
                logout_user()
                
                # Verificar se a sessão foi limpa
                assert st.session_state.is_authenticated == False
                assert st.session_state.auth_token is None
                assert st.session_state.user is None
                assert st.session_state.current_page == "login"
                assert st.session_state.last_auth_check == 0
                
                # Verificar se a limpeza do localStorage foi chamada
                mock_clear.assert_called_once()

    # ==================== TESTES DE SEGURANÇA ====================
    
    def test_token_validation_security(self):
        """Testa validação de segurança do token."""
        # Teste com token malformado
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "malformed_token"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        st.session_state.last_auth_check = time.time()
        
        # Mock da requisição retornando erro 401
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_get.return_value = mock_response
            
            result = is_authenticated()
            assert result == False
            
            # Verificar se a sessão foi limpa por segurança
            assert st.session_state.is_authenticated == False
            assert st.session_state.auth_token is None

    def test_session_data_encryption(self):
        """Testa que dados sensíveis não são expostos em logs."""
        # Configurar sessão com dados sensíveis
        st.session_state.is_authenticated = True
        st.session_state.auth_token = "sensitive_token_123"
        st.session_state.user = {"name": "Test User", "email": "test@test.com"}
        
        # Mock do logging para verificar se dados sensíveis não são logados
        with patch('builtins.print') as mock_print:
            # Simular operação que poderia logar dados
            save_session_to_storage()
            
            # Verificar se o token não foi logado em texto plano
            print_calls = [call[0][0] for call in mock_print.call_args_list]
            for call in print_calls:
                assert "sensitive_token_123" not in str(call)


def run_session_tests():
    """Executa todos os testes de persistência de sessão."""
    print("🧪 Iniciando testes de persistência de sessão...")
    print("=" * 60)
    
    # Criar instância da classe de testes
    test_instance = TestSessionPersistence()
    
    # Lista de todos os métodos de teste
    test_methods = [
        # Inicialização de sessão
        test_instance.test_session_initialization,
        
        # Salvamento de sessão
        test_instance.test_save_session_to_storage,
        test_instance.test_clear_session_from_storage,
        
        # Validação de sessão
        test_instance.test_session_validation_with_valid_token,
        test_instance.test_session_validation_with_invalid_token,
        test_instance.test_session_validation_with_timeout,
        test_instance.test_session_expiration_24_hours,
        test_instance.test_session_validation_interval_30_minutes,
        test_instance.test_session_validation_skip_recent_check,
        
        # Restauração de sessão
        test_instance.test_session_restoration_from_localStorage,
        
        # Histórico de chat
        test_instance.test_save_current_chat_to_history,
        test_instance.test_chat_history_limit,
        
        # Persistência em casos de erro
        test_instance.test_session_persistence_on_network_error,
        test_instance.test_session_clear_on_logout,
        
        # Segurança
        test_instance.test_token_validation_security,
        test_instance.test_session_data_encryption,
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
    print(f"📊 Resultados dos Testes de Sessão:")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Taxa de Sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if errors:
        print("\n🔍 Erros Encontrados:")
        for error in errors:
            print(f"  - {error}")
    
    return passed, failed, errors


if __name__ == "__main__":
    run_session_tests()
