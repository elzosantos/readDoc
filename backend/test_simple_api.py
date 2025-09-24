"""
Testes simplificados para a API (sem dependências externas).
"""

import os
import sys
import tempfile
import requests
import time

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_health():
    """Testa se a API está funcionando."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API Health Check - OK")
            return True
        else:
            print(f"❌ API Health Check - Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Health Check - Erro: {str(e)}")
        return False

def test_api_login():
    """Testa login na API."""
    try:
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        response = requests.post("http://localhost:8000/auth/login", json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ API Login - OK")
            return True
        else:
            print(f"❌ API Login - Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Login - Erro: {str(e)}")
        return False

def test_api_documents_status():
    """Testa status dos documentos."""
    try:
        headers = {"Authorization": "Bearer seu_token_secreto_aqui"}
        response = requests.get("http://localhost:8000/documents/status", headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ API Documents Status - OK")
            return True
        else:
            print(f"❌ API Documents Status - Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Documents Status - Erro: {str(e)}")
        return False

def test_api_upload():
    """Testa upload de documento."""
    try:
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("Este é um arquivo de teste para validação do sistema.")
            temp_file = f.name
        
        headers = {"Authorization": "Bearer seu_token_secreto_aqui"}
        
        with open(temp_file, "rb") as file:
            files = {"file": ("test.txt", file, "text/plain")}
            data = {"chunk_size": 600, "chunk_overlap": 200}
            
            response = requests.post("http://localhost:8000/documents/upload", 
                                   files=files, data=data, headers=headers, timeout=10)
        
        # Limpar arquivo temporário
        os.unlink(temp_file)
        
        if response.status_code == 200:
            print("✅ API Upload - OK")
            return True
        else:
            print(f"❌ API Upload - Erro {response.status_code}")
            if response.status_code == 500:
                print(f"   Detalhes: {response.text}")
            return False
    except Exception as e:
        print(f"❌ API Upload - Erro: {str(e)}")
        return False

def test_api_query():
    """Testa consulta de documentos."""
    try:
        headers = {"Authorization": "Bearer seu_token_secreto_aqui"}
        query_data = {
            "query": "teste",
            "lambda_mult": 0.8,
            "k_documents": 4
        }
        
        response = requests.post("http://localhost:8000/query", json=query_data, headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API Query - OK")
            return True
        elif response.status_code == 400:
            print("⚠️ API Query - Nenhum documento carregado (esperado)")
            return True
        else:
            print(f"❌ API Query - Erro {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API Query - Erro: {str(e)}")
        return False

def run_tests():
    """Executa todos os testes."""
    print("🧪 Iniciando testes simplificados da API...")
    print("=" * 60)
    
    tests = [
        ("Health Check", test_api_health),
        ("Login", test_api_login),
        ("Documents Status", test_api_documents_status),
        ("Upload", test_api_upload),
        ("Query", test_api_query),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testando: {test_name}")
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} - Exceção: {str(e)}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Resultados dos Testes:")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Taxa de Sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    return passed, failed

if __name__ == "__main__":
    run_tests()
