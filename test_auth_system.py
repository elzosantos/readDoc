#!/usr/bin/env python3
"""
Teste do sistema de autenticação completo
"""

import requests
import json
import time

def test_auth_system():
    """Testa o sistema de autenticação"""
    print("🧪 Testando Sistema de Autenticação")
    print("=" * 50)
    
    # Configurações
    api_url = "http://localhost:8000"
    
    # Teste 1: Health Check
    print("1. 🔍 Testando Health Check...")
    try:
        response = requests.get(f"{api_url}/health")
        if response.status_code == 200:
            print("✅ API está funcionando!")
        else:
            print(f"❌ Erro no health check: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # Teste 2: Cadastro de usuário
    print("\n2. 📝 Testando cadastro de usuário...")
    register_data = {
        "name": "Usuário Teste",
        "email": "teste@exemplo.com",
        "password": "senha123",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/register", json=register_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Usuário cadastrado com sucesso!")
            else:
                print(f"⚠️ Usuário já existe: {result.get('message')}")
        else:
            print(f"❌ Erro no cadastro: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no cadastro: {e}")
    
    # Teste 3: Login
    print("\n3. 🔐 Testando login...")
    login_data = {
        "email": "teste@exemplo.com",
        "password": "senha123"
    }
    
    auth_token = None
    try:
        response = requests.post(f"{api_url}/auth/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                auth_token = result.get("token")
                user = result.get("user")
                print("✅ Login realizado com sucesso!")
                print(f"   Usuário: {user.get('name')} ({user.get('email')})")
                print(f"   Perfil: {user.get('role')}")
            else:
                print(f"❌ Erro no login: {result.get('message')}")
                return
        else:
            print(f"❌ Erro no login: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro no login: {e}")
        return
    
    # Teste 4: Verificar informações do usuário
    print("\n4. 👤 Testando informações do usuário...")
    headers = {"Authorization": f"Bearer {auth_token}"}
    
    try:
        response = requests.get(f"{api_url}/auth/me", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                user = result.get("user")
                print("✅ Informações do usuário obtidas!")
                print(f"   ID: {user.get('id')}")
                print(f"   Nome: {user.get('name')}")
                print(f"   Email: {user.get('email')}")
                print(f"   Perfil: {user.get('role')}")
            else:
                print(f"❌ Erro ao obter informações: {result.get('message')}")
        else:
            print(f"❌ Erro ao obter informações: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao obter informações: {e}")
    
    # Teste 5: Testar permissões
    print("\n5. 🔒 Testando permissões...")
    
    # Testar acesso a documentos (deve funcionar para usuário comum)
    try:
        response = requests.get(f"{api_url}/documents/status", headers=headers)
        if response.status_code == 200:
            print("✅ Acesso a documentos permitido!")
        else:
            print(f"❌ Acesso a documentos negado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar acesso a documentos: {e}")
    
    # Testar acesso a gestão de usuários (deve ser negado para usuário comum)
    try:
        response = requests.get(f"{api_url}/admin/users", headers=headers)
        if response.status_code == 403:
            print("✅ Acesso a gestão de usuários corretamente negado!")
        else:
            print(f"⚠️ Acesso inesperado à gestão de usuários: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar acesso à gestão de usuários: {e}")
    
    # Teste 6: Login como admin
    print("\n6. 👑 Testando login como admin...")
    admin_login_data = {
        "email": "admin@system.com",
        "password": "admin123"
    }
    
    admin_token = None
    try:
        response = requests.post(f"{api_url}/auth/login", json=admin_login_data)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                admin_token = result.get("token")
                user = result.get("user")
                print("✅ Login de admin realizado com sucesso!")
                print(f"   Usuário: {user.get('name')} ({user.get('email')})")
                print(f"   Perfil: {user.get('role')}")
            else:
                print(f"❌ Erro no login de admin: {result.get('message')}")
                return
        else:
            print(f"❌ Erro no login de admin: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro no login de admin: {e}")
        return
    
    # Teste 7: Testar permissões de admin
    print("\n7. 🔒 Testando permissões de admin...")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Testar acesso à gestão de usuários (deve funcionar para admin)
    try:
        response = requests.get(f"{api_url}/admin/users", headers=admin_headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                users = result.get("users", [])
                print("✅ Acesso à gestão de usuários permitido!")
                print(f"   Total de usuários: {len(users)}")
            else:
                print(f"❌ Erro ao acessar gestão de usuários: {result.get('message')}")
        else:
            print(f"❌ Acesso à gestão de usuários negado: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao testar acesso à gestão de usuários: {e}")
    
    # Teste 8: Logout
    print("\n8. 🚪 Testando logout...")
    try:
        response = requests.post(f"{api_url}/auth/logout", headers=headers)
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Logout realizado com sucesso!")
            else:
                print(f"❌ Erro no logout: {result.get('message')}")
        else:
            print(f"❌ Erro no logout: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro no logout: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Teste do sistema de autenticação concluído!")
    print("\n📋 Funcionalidades testadas:")
    print("   ✅ Health Check da API")
    print("   ✅ Cadastro de usuários")
    print("   ✅ Login de usuários")
    print("   ✅ Verificação de informações")
    print("   ✅ Sistema de permissões")
    print("   ✅ Login de administrador")
    print("   ✅ Permissões de administrador")
    print("   ✅ Logout de usuários")
    
    print("\n🌐 Acesse o frontend em: http://localhost:8501")
    print("   • Faça login com: teste@exemplo.com / senha123")
    print("   • Ou use o admin: admin@system.com / admin123")

if __name__ == "__main__":
    test_auth_system()
