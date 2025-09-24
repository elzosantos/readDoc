"""
Script para testar se o sistema está funcionando corretamente.
"""

import requests
import time

def test_api():
    """Testa se a API está funcionando"""
    try:
        # Testar health check
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✅ API Health Check: OK")
            return True
        else:
            print(f"❌ API Health Check: Erro {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ API não está rodando em http://localhost:8000")
        return False

def test_frontend():
    """Testa se o frontend está funcionando"""
    try:
        response = requests.get("http://localhost:8501")
        if response.status_code == 200:
            print("✅ Frontend Streamlit: OK")
            return True
        else:
            print(f"❌ Frontend Streamlit: Erro {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Frontend não está rodando em http://localhost:8501")
        return False

def test_api_with_auth():
    """Testa a API com autenticação"""
    try:
        headers = {"Authorization": "Bearer seu_token_secreto_aqui"}
        response = requests.get("http://localhost:8000/user/me", headers=headers)
        if response.status_code == 200:
            print("✅ API com Autenticação: OK")
            return True
        else:
            print(f"❌ API com Autenticação: Erro {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão na API")
        return False

def main():
    print("🧪 Testando Sistema LLMChat")
    print("=" * 40)
    
    # Aguardar um pouco para os serviços iniciarem
    print("⏳ Aguardando serviços iniciarem...")
    time.sleep(5)
    
    # Testar API
    api_ok = test_api()
    
    # Testar Frontend
    frontend_ok = test_frontend()
    
    # Testar autenticação
    auth_ok = test_api_with_auth()
    
    print("\n" + "=" * 40)
    print("📊 Resultado dos Testes:")
    print(f"   API: {'✅ OK' if api_ok else '❌ FALHA'}")
    print(f"   Frontend: {'✅ OK' if frontend_ok else '❌ FALHA'}")
    print(f"   Autenticação: {'✅ OK' if auth_ok else '❌ FALHA'}")
    
    if api_ok and frontend_ok and auth_ok:
        print("\n🎉 Sistema funcionando perfeitamente!")
        print("🌐 Acesse:")
        print("   • Frontend: http://localhost:8501")
        print("   • API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️ Alguns serviços não estão funcionando.")
        print("💡 Verifique se ambos os serviços estão rodando:")
        print("   • API: python run_api_simple.py")
        print("   • Frontend: python run_frontend_simple.py")

if __name__ == "__main__":
    main()
