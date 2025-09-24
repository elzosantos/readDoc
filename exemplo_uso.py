"""
Exemplo de uso da API para demonstrar as funcionalidades.
"""

import requests
import json
import time

# Configurações
API_BASE_URL = "http://localhost:8000"
TOKEN = "seu_token_secreto_aqui"

def make_request(endpoint, method="GET", data=None):
    """Faz requisição para a API"""
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"❌ Erro {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("❌ Não foi possível conectar à API. Verifique se está rodando.")
        return None

def main():
    print("🤖 Exemplo de Uso da API LLMChat")
    print("=" * 50)
    
    # 1. Verificar saúde da API
    print("\n1. 🔍 Verificando saúde da API...")
    health = make_request("/health")
    if health:
        print(f"✅ API funcionando: {health['message']}")
    else:
        print("❌ API não está funcionando")
        return
    
    # 2. Verificar status dos documentos
    print("\n2. 📊 Verificando status dos documentos...")
    status = make_request("/documents/status")
    if status:
        print(f"✅ Documentos carregados: {status.get('documents_count', 0)}")
        print(f"✅ Sistema ativo: {status.get('has_documents', False)}")
    else:
        print("❌ Não foi possível obter status")
    
    # 3. Carregar um documento (se não houver)
    if not status or not status.get('has_documents'):
        print("\n3. 📤 Carregando documento de exemplo...")
        load_result = make_request("/documents/load", "POST", {
            "file_path": "historia.txt",
            "chunk_size": 600,
            "chunk_overlap": 200
        })
        
        if load_result:
            print(f"✅ {load_result['message']}")
            print(f"📊 {load_result['documents_count']} documentos processados")
        else:
            print("❌ Falha ao carregar documento")
            return
    
    # 4. Fazer algumas consultas
    print("\n4. 💬 Fazendo consultas de exemplo...")
    
    queries = [
        "Quem descobriu o Brasil?",
        "Qual foi a primeira capital do Brasil?",
        "Quem foi Pedro Álvares Cabral?",
        "Quando o Brasil foi descoberto?"
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n   Consulta {i}: {query}")
        result = make_request("/query", "POST", {"query": query})
        
        if result and result.get('success'):
            answer = result.get('answer', 'Sem resposta')
            print(f"   🤖 Resposta: {answer[:100]}...")
            
            documents_used = result.get('documents_used', [])
            if documents_used:
                print(f"   📄 Documentos utilizados: {len(documents_used)}")
        else:
            print("   ❌ Falha na consulta")
        
        time.sleep(1)  # Pausa entre consultas
    
    # 5. Obter informações do usuário
    print("\n5. 👤 Informações do usuário...")
    user_info = make_request("/user/me")
    if user_info:
        user = user_info.get('user', {})
        print(f"✅ Token: {user.get('token', 'N/A')}")
        print(f"✅ Role: {user.get('role', 'N/A')}")
        print(f"✅ Permissões: {user.get('permissions', [])}")
    
    print("\n" + "=" * 50)
    print("🎉 Exemplo concluído com sucesso!")
    print("💡 Agora você pode usar a interface web em: http://localhost:8501")

if __name__ == "__main__":
    main()
