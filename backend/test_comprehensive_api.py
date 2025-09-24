"""
Testes abrangentes para todos os endpoints da API.
"""

import os
import sys
import pytest
import asyncio
import tempfile
import json
from typing import Dict, Any
from unittest.mock import patch, MagicMock

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import requests
from fastapi.testclient import TestClient
from fastapi import status

# Importar a aplicação
from api import app
from config import API_BASE_URL
from auth import LEGACY_TOKENS

# Cliente de teste
client = TestClient(app)

# Tokens de teste
ADMIN_TOKEN = "seu_token_secreto_aqui"
USER_TOKEN = "user_token_456"
ADMIN_TOKEN_2 = "admin_token_123"

# Headers de autenticação
ADMIN_HEADERS = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
USER_HEADERS = {"Authorization": f"Bearer {USER_TOKEN}"}
ADMIN_HEADERS_2 = {"Authorization": f"Bearer {ADMIN_TOKEN_2}"}

class TestAPIEndpoints:
    """Classe principal para testes da API."""
    
    def setup_method(self):
        """Configuração antes de cada teste."""
        self.test_file_content = "Este é um arquivo de teste para validação do sistema."
        self.test_file_path = None
    
    def teardown_method(self):
        """Limpeza após cada teste."""
        if self.test_file_path and os.path.exists(self.test_file_path):
            os.remove(self.test_file_path)
    
    def create_test_file(self, extension: str = ".txt") -> str:
        """Cria um arquivo temporário para testes."""
        with tempfile.NamedTemporaryFile(mode='w', suffix=extension, delete=False, encoding='utf-8') as f:
            f.write(self.test_file_content)
            self.test_file_path = f.name
        return self.test_file_path

    # ==================== TESTES DE HEALTH CHECK ====================
    
    def test_root_endpoint(self):
        """Testa o endpoint raiz."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "API de busca de documentos funcionando!" in data["message"]
        assert data["version"] == "1.0.0"
    
    def test_health_check(self):
        """Testa o health check."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "API funcionando" in data["message"]

    # ==================== TESTES DE AUTENTICAÇÃO ====================
    
    def test_login_success(self):
        """Testa login bem-sucedido."""
        login_data = {
            "email": "admin@test.com",
            "password": "admin123"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "token" in data
        assert data["user"]["email"] == "admin@test.com"
    
    def test_login_invalid_credentials(self):
        """Testa login com credenciais inválidas."""
        login_data = {
            "email": "invalid@test.com",
            "password": "wrongpassword"
        }
        response = client.post("/auth/login", json=login_data)
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Credenciais inválidas" in data["message"]
    
    def test_register_success(self):
        """Testa registro de novo usuário."""
        register_data = {
            "name": "Test User",
            "email": "testuser@test.com",
            "password": "testpass123",
            "role": "user"
        }
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Usuário criado com sucesso" in data["message"]
    
    def test_register_duplicate_email(self):
        """Testa registro com email duplicado."""
        register_data = {
            "name": "Duplicate User",
            "email": "admin@test.com",  # Email já existe
            "password": "testpass123",
            "role": "user"
        }
        response = client.post("/auth/register", json=register_data)
        assert response.status_code == 400
        data = response.json()
        assert data["success"] is False
        assert "Email já está em uso" in data["message"]
    
    def test_logout_success(self):
        """Testa logout bem-sucedido."""
        response = client.post("/auth/logout", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Logout realizado com sucesso" in data["message"]
    
    def test_get_current_user(self):
        """Testa obtenção de informações do usuário atual."""
        response = client.get("/auth/me", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert data["user"]["email"] == "admin@test.com"
    
    def test_get_current_user_unauthorized(self):
        """Testa obtenção de usuário sem autenticação."""
        response = client.get("/auth/me")
        assert response.status_code == 401

    # ==================== TESTES DE PERMISSÕES ====================
    
    def test_admin_tokens_endpoint(self):
        """Testa listagem de tokens (apenas admin)."""
        response = client.get("/admin/tokens", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "tokens" in data
    
    def test_admin_tokens_unauthorized(self):
        """Testa listagem de tokens sem permissão admin."""
        response = client.get("/admin/tokens", headers=USER_HEADERS)
        assert response.status_code == 403
    
    def test_user_me_endpoint(self):
        """Testa endpoint /user/me."""
        response = client.get("/user/me", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "user" in data
        assert "message" in data

    # ==================== TESTES DE DOCUMENTOS ====================
    
    def test_documents_status(self):
        """Testa status dos documentos."""
        response = client.get("/documents/status", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "documents_count" in data
        assert "last_loaded" in data
    
    def test_documents_status_unauthorized(self):
        """Testa status dos documentos sem autenticação."""
        response = client.get("/documents/status")
        assert response.status_code == 401
    
    def test_load_document_success(self):
        """Testa carregamento de documento."""
        test_file = self.create_test_file()
        
        load_data = {
            "file_path": test_file,
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/load", json=load_data, headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["documents_count"] > 0
    
    def test_load_document_file_not_found(self):
        """Testa carregamento de arquivo inexistente."""
        load_data = {
            "file_path": "/path/to/nonexistent/file.txt",
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/load", json=load_data, headers=ADMIN_HEADERS)
        assert response.status_code == 404
        data = response.json()
        assert "Arquivo não encontrado" in data["detail"]
    
    def test_load_document_unauthorized(self):
        """Testa carregamento de documento sem permissão."""
        test_file = self.create_test_file()
        
        load_data = {
            "file_path": test_file,
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/load", json=load_data, headers=USER_HEADERS)
        assert response.status_code == 403
    
    def test_upload_document_success(self):
        """Testa upload de documento."""
        test_file = self.create_test_file()
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            data = {
                "chunk_size": 600,
                "chunk_overlap": 200
            }
            
            response = client.post("/documents/upload", files=files, data=data, headers=ADMIN_HEADERS)
            assert response.status_code == 200
            response_data = response.json()
            assert response_data["success"] is True
            assert response_data["documents_count"] > 0
    
    def test_upload_document_invalid_extension(self):
        """Testa upload de arquivo com extensão inválida."""
        test_file = self.create_test_file(".exe")  # Extensão não permitida
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.exe", f, "application/octet-stream")}
            data = {
                "chunk_size": 600,
                "chunk_overlap": 200
            }
            
            response = client.post("/documents/upload", files=files, data=data, headers=ADMIN_HEADERS)
            assert response.status_code == 400
            data = response.json()
            assert "Tipo de arquivo não suportado" in data["detail"]
    
    def test_upload_document_no_file(self):
        """Testa upload sem arquivo."""
        data = {
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/upload", data=data, headers=ADMIN_HEADERS)
        assert response.status_code == 422  # Validation error
    
    def test_test_upload_endpoint(self):
        """Testa endpoint de teste de upload."""
        test_file = self.create_test_file()
        
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            
            response = client.post("/test/upload", files=files, headers=ADMIN_HEADERS)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["file_size"] > 0
            assert data["file_extension"] == ".txt"

    # ==================== TESTES DE CONSULTAS ====================
    
    def test_query_documents_success(self):
        """Testa consulta de documentos."""
        # Primeiro carregar um documento
        test_file = self.create_test_file()
        load_data = {
            "file_path": test_file,
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        client.post("/documents/load", json=load_data, headers=ADMIN_HEADERS)
        
        # Agora fazer a consulta
        query_data = {
            "query": "teste",
            "lambda_mult": 0.8,
            "k_documents": 4
        }
        
        response = client.post("/query", json=query_data, headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "answer" in data
        assert data["query"] == "teste"
    
    def test_query_documents_no_documents(self):
        """Testa consulta sem documentos carregados."""
        query_data = {
            "query": "teste",
            "lambda_mult": 0.8,
            "k_documents": 4
        }
        
        response = client.post("/query", json=query_data, headers=ADMIN_HEADERS)
        assert response.status_code == 400
        data = response.json()
        assert "Nenhum documento carregado" in data["detail"]
    
    def test_query_documents_unauthorized(self):
        """Testa consulta sem permissão."""
        query_data = {
            "query": "teste",
            "lambda_mult": 0.8,
            "k_documents": 4
        }
        
        response = client.post("/query", json=query_data, headers=USER_HEADERS)
        assert response.status_code == 403

    # ==================== TESTES DE GERENCIAMENTO DE USUÁRIOS ====================
    
    def test_list_users_admin(self):
        """Testa listagem de usuários (admin)."""
        response = client.get("/admin/users", headers=ADMIN_HEADERS)
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert isinstance(data["users"], list)
    
    def test_list_users_unauthorized(self):
        """Testa listagem de usuários sem permissão."""
        response = client.get("/admin/users", headers=USER_HEADERS)
        assert response.status_code == 403
    
    def test_update_user_admin(self):
        """Testa atualização de usuário (admin)."""
        # Primeiro obter lista de usuários para pegar um ID
        users_response = client.get("/admin/users", headers=ADMIN_HEADERS)
        users_data = users_response.json()
        
        if users_data["users"]:
            user_id = users_data["users"][0]["id"]
            
            update_data = {
                "name": "Updated Name",
                "role": "user"
            }
            
            response = client.put(f"/admin/users/{user_id}", json=update_data, headers=ADMIN_HEADERS)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
    
    def test_delete_user_admin(self):
        """Testa exclusão de usuário (admin)."""
        # Primeiro obter lista de usuários para pegar um ID
        users_response = client.get("/admin/users", headers=ADMIN_HEADERS)
        users_data = users_response.json()
        
        if users_data["users"]:
            user_id = users_data["users"][0]["id"]
            
            response = client.delete(f"/admin/users/{user_id}", headers=ADMIN_HEADERS)
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

    # ==================== TESTES DE VALIDAÇÃO ====================
    
    def test_invalid_token(self):
        """Testa token inválido."""
        invalid_headers = {"Authorization": "Bearer invalid_token"}
        response = client.get("/user/me", headers=invalid_headers)
        assert response.status_code == 401
    
    def test_malformed_token(self):
        """Testa token malformado."""
        malformed_headers = {"Authorization": "InvalidFormat token"}
        response = client.get("/user/me", headers=malformed_headers)
        assert response.status_code == 401
    
    def test_missing_token(self):
        """Testa requisição sem token."""
        response = client.get("/user/me")
        assert response.status_code == 401

    # ==================== TESTES DE DIFERENTES TIPOS DE ARQUIVO ====================
    
    def test_load_pdf_file(self):
        """Testa carregamento de arquivo PDF."""
        # Criar um arquivo PDF simulado (apenas para teste)
        test_file = self.create_test_file(".pdf")
        
        load_data = {
            "file_path": test_file,
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/load", json=load_data, headers=ADMIN_HEADERS)
        # Pode falhar se não tiver PyPDF2 instalado, mas deve retornar erro específico
        assert response.status_code in [200, 500]
    
    def test_load_docx_file(self):
        """Testa carregamento de arquivo DOCX."""
        test_file = self.create_test_file(".docx")
        
        load_data = {
            "file_path": test_file,
            "chunk_size": 600,
            "chunk_overlap": 200
        }
        
        response = client.post("/documents/load", json=load_data, headers=ADMIN_HEADERS)
        # Pode falhar se não tiver python-docx instalado, mas deve retornar erro específico
        assert response.status_code in [200, 500]

    # ==================== TESTES DE PERFORMANCE ====================
    
    def test_concurrent_requests(self):
        """Testa requisições concorrentes."""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Todas as requisições devem ter sucesso
        assert all(status == 200 for status in results)
        assert len(results) == 10

    # ==================== TESTES DE CORS ====================
    
    def test_cors_headers(self):
        """Testa headers CORS."""
        response = client.options("/health")
        assert response.status_code == 200
        # Verificar se os headers CORS estão presentes
        assert "access-control-allow-origin" in response.headers


def run_tests():
    """Executa todos os testes."""
    print("🧪 Iniciando testes abrangentes da API...")
    print("=" * 60)
    
    # Criar instância da classe de testes
    test_instance = TestAPIEndpoints()
    
    # Lista de todos os métodos de teste
    test_methods = [
        # Health Check
        test_instance.test_root_endpoint,
        test_instance.test_health_check,
        
        # Autenticação
        test_instance.test_login_success,
        test_instance.test_login_invalid_credentials,
        test_instance.test_register_success,
        test_instance.test_register_duplicate_email,
        test_instance.test_logout_success,
        test_instance.test_get_current_user,
        test_instance.test_get_current_user_unauthorized,
        
        # Permissões
        test_instance.test_admin_tokens_endpoint,
        test_instance.test_admin_tokens_unauthorized,
        test_instance.test_user_me_endpoint,
        
        # Documentos
        test_instance.test_documents_status,
        test_instance.test_documents_status_unauthorized,
        test_instance.test_load_document_success,
        test_instance.test_load_document_file_not_found,
        test_instance.test_load_document_unauthorized,
        test_instance.test_upload_document_success,
        test_instance.test_upload_document_invalid_extension,
        test_instance.test_upload_document_no_file,
        test_instance.test_test_upload_endpoint,
        
        # Consultas
        test_instance.test_query_documents_success,
        test_instance.test_query_documents_no_documents,
        test_instance.test_query_documents_unauthorized,
        
        # Gerenciamento de usuários
        test_instance.test_list_users_admin,
        test_instance.test_list_users_unauthorized,
        test_instance.test_update_user_admin,
        test_instance.test_delete_user_admin,
        
        # Validação
        test_instance.test_invalid_token,
        test_instance.test_malformed_token,
        test_instance.test_missing_token,
        
        # Tipos de arquivo
        test_instance.test_load_pdf_file,
        test_instance.test_load_docx_file,
        
        # Performance
        test_instance.test_concurrent_requests,
        
        # CORS
        test_instance.test_cors_headers,
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
    print(f"📊 Resultados dos Testes:")
    print(f"✅ Passou: {passed}")
    print(f"❌ Falhou: {failed}")
    print(f"📈 Taxa de Sucesso: {(passed/(passed+failed)*100):.1f}%")
    
    if errors:
        print("\n🔍 Erros Encontrados:")
        for error in errors:
            print(f"  - {error}")
    
    return passed, failed, errors


if __name__ == "__main__":
    run_tests()
