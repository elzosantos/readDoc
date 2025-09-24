"""
Script para testar a funcionalidade de chat da API.
"""

import requests
import json

def test_chat():
    """Testa a funcionalidade de chat"""
    print("🧪 Testando Funcionalidade de Chat")
    print("=" * 40)
    
    # Configurações
    api_url = "http://localhost:8000"
    token = "seu_token_secreto_aqui"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Verificar status dos documentos
    print("\n1. 📊 Verificando status dos documentos...")
    try:
        response = requests.get(f"{api_url}/documents/status", headers=headers)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Documentos carregados: {status.get('documents_count', 0)}")
            print(f"✅ Sistema ativo: {status.get('has_documents', False)}")
        else:
            print(f"❌ Erro ao verificar status: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        return
    
    # Teste 2: Fazer uma consulta
    print("\n2. 💬 Testando consulta...")
    query = "Quem descobriu o Brasil?"
    print(f"   Pergunta: {query}")
    
    try:
        response = requests.post(
            f"{api_url}/query",
            headers=headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                answer = result.get("answer", "Sem resposta")
                documents_used = result.get("documents_used", [])
                
                print(f"✅ Resposta recebida: {answer[:100]}...")
                print(f"✅ Documentos utilizados: {len(documents_used) if isinstance(documents_used, list) else 'N/A'}")
                
                # Verificar se documents_used é uma lista
                if isinstance(documents_used, list):
                    print("✅ documents_used é uma lista válida")
                else:
                    print(f"⚠️ documents_used não é uma lista: {type(documents_used)}")
                
            else:
                print("❌ Consulta falhou")
        else:
            print(f"❌ Erro na consulta: {response.status_code}")
            print(f"   Resposta: {response.text}")
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
    
    # Teste 3: Fazer outra consulta
    print("\n3. 💬 Testando segunda consulta...")
    query2 = "Qual foi a primeira capital do Brasil?"
    print(f"   Pergunta: {query2}")
    
    try:
        response = requests.post(
            f"{api_url}/query",
            headers=headers,
            json={"query": query2}
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                answer = result.get("answer", "Sem resposta")
                documents_used = result.get("documents_used", [])
                
                print(f"✅ Resposta recebida: {answer[:100]}...")
                print(f"✅ Documentos utilizados: {len(documents_used) if isinstance(documents_used, list) else 'N/A'}")
                
            else:
                print("❌ Segunda consulta falhou")
        else:
            print(f"❌ Erro na segunda consulta: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Erro na segunda consulta: {e}")
    
    print("\n" + "=" * 40)
    print("🎉 Teste de chat concluído!")
    print("💡 Agora você pode testar no frontend: http://localhost:8501")

if __name__ == "__main__":
    test_chat()
