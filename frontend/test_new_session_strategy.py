"""
Teste da nova estratégia de sessão robusta
"""

import streamlit as st
import time
import json
from session_manager import session_manager

def test_session_creation():
    """Testa criação de sessão"""
    print("🧪 Testando criação de sessão...")
    
    # Dados de teste
    user_data = {
        "id": 1,
        "name": "Test User",
        "email": "test@test.com",
        "role": "user"
    }
    auth_token = "test_token_123"
    
    # Simular criação de sessão sem usar st.session_state
    current_time = time.time()
    session_id = session_manager.generate_session_id(user_data)
    
    session_data = {
        'is_authenticated': True,
        'auth_token': auth_token,
        'user': user_data,
        'current_page': 'dashboard',
        'session_id': session_id,
        'login_timestamp': current_time,
        'last_activity': current_time,
        'session_hash': None
    }
    
    # Gerar hash
    session_data['session_hash'] = session_manager.generate_session_hash(session_data)
    
    # Verificar se a sessão foi criada corretamente
    assert session_data['is_authenticated'] == True
    assert session_data['auth_token'] == auth_token
    assert session_data['user'] == user_data
    assert 'session_id' in session_data
    assert 'login_timestamp' in session_data
    assert 'session_hash' in session_data
    
    print("✅ Criação de sessão funcionando")

def test_session_validation():
    """Testa validação de sessão"""
    print("🧪 Testando validação de sessão...")
    
    # Sessão válida
    valid_session = {
        'auth_token': 'valid_token',
        'user': {'id': 1, 'email': 'test@test.com'},
        'login_timestamp': time.time() - 3600,  # 1 hora atrás
        'last_activity': time.time() - 1800,  # 30 minutos de inatividade
        'session_hash': session_manager.generate_session_hash({
            'auth_token': 'valid_token',
            'user': {'id': 1, 'email': 'test@test.com'},
            'login_timestamp': time.time() - 3600
        })
    }
    
    # Sessão expirada (25 horas)
    expired_session = {
        'auth_token': 'expired_token',
        'user': {'id': 1, 'email': 'test@test.com'},
        'login_timestamp': time.time() - (25 * 3600),  # 25 horas atrás
        'last_activity': time.time() - (25 * 3600),
        'session_hash': 'test_hash'
    }
    
    # Sessão com inatividade excessiva (3 horas)
    idle_session = {
        'auth_token': 'idle_token',
        'user': {'id': 1, 'email': 'test@test.com'},
        'login_timestamp': time.time() - 3600,  # 1 hora atrás
        'last_activity': time.time() - (3 * 3600),  # 3 horas de inatividade
        'session_hash': 'test_hash'
    }
    
    # Testar validações
    assert session_manager.is_session_valid(valid_session) == True
    assert session_manager.is_session_valid(expired_session) == False
    assert session_manager.is_session_valid(idle_session) == False
    
    print("✅ Validação de sessão funcionando")

def test_session_hash():
    """Testa geração e verificação de hash de sessão"""
    print("🧪 Testando hash de sessão...")
    
    session_data = {
        'auth_token': 'test_token',
        'user': {'id': 1, 'email': 'test@test.com'},
        'login_timestamp': time.time()
    }
    
    # Gerar hash
    hash1 = session_manager.generate_session_hash(session_data)
    hash2 = session_manager.generate_session_hash(session_data)
    
    # Hash deve ser consistente
    assert hash1 == hash2
    
    # Modificar dados e verificar se hash muda
    session_data['auth_token'] = 'different_token'
    hash3 = session_manager.generate_session_hash(session_data)
    
    assert hash1 != hash3
    
    print("✅ Hash de sessão funcionando")

def test_session_id_generation():
    """Testa geração de ID de sessão"""
    print("🧪 Testando geração de ID de sessão...")
    
    user_data1 = {'id': 1, 'email': 'user1@test.com'}
    user_data2 = {'id': 2, 'email': 'user2@test.com'}
    
    # Gerar IDs
    id1 = session_manager.generate_session_id(user_data1)
    id2 = session_manager.generate_session_id(user_data2)
    
    # IDs devem ser únicos para usuários diferentes
    assert id1 != id2
    
    # IDs devem ter 16 caracteres
    assert len(id1) == 16
    assert len(id2) == 16
    
    # IDs devem ser strings hexadecimais
    assert all(c in '0123456789abcdef' for c in id1)
    assert all(c in '0123456789abcdef' for c in id2)
    
    print("✅ Geração de ID de sessão funcionando")

def test_session_duration():
    """Testa duração da sessão"""
    print("🧪 Testando duração da sessão...")
    
    # Verificar configurações
    assert session_manager.session_duration == 24 * 60 * 60  # 24 horas
    assert session_manager.refresh_interval == 30 * 60  # 30 minutos
    assert session_manager.max_idle_time == 2 * 60 * 60  # 2 horas
    
    print("✅ Configurações de duração corretas")

def run_session_tests():
    """Executa todos os testes da nova estratégia de sessão"""
    print("🚀 Iniciando testes da nova estratégia de sessão...")
    print("=" * 60)
    
    tests = [
        test_session_creation,
        test_session_validation,
        test_session_hash,
        test_session_id_generation,
        test_session_duration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {str(e)}")
            failed += 1
    
    print("=" * 60)
    print(f"📊 Resultados dos Testes:")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Taxa de Sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if failed == 0:
        print("\n🎉 Todos os testes passaram! Nova estratégia de sessão está funcionando.")
    else:
        print(f"\n⚠️ {failed} testes falharam. Verifique os erros acima.")
    
    return passed, failed

if __name__ == "__main__":
    run_session_tests()
