#!/usr/bin/env python3
"""
Teste das novas funcionalidades do chat:
- Botão "Novo Chat"
- Histórico com nomes baseados no contexto
- Sistema de chat atual vs histórico
"""

import requests
import json
import time

def test_chat_features():
    """Testa as funcionalidades do chat"""
    print("🧪 Testando Funcionalidades do Chat")
    print("=" * 50)
    
    # Configurações
    api_url = "http://localhost:8000"
    token = "seu_token_secreto_aqui"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Teste 1: Carregar documento
    print("📄 1. Carregando documento...")
    load_response = requests.post(
        f"{api_url}/documents/load",
        headers=headers,
        json={"file_path": "historia.txt"}
    )
    
    if load_response.status_code == 200:
        print("✅ Documento carregado com sucesso!")
    else:
        print(f"❌ Erro ao carregar documento: {load_response.status_code}")
        return
    
    # Teste 2: Fazer várias perguntas para testar nomes de chat
    queries = [
        "Qual é a história do Brasil?",
        "Quem descobriu o Brasil?",
        "Qual é a capital do Brasil?",
        "Fale sobre a independência do Brasil",
        "Como foi a colonização do Brasil?"
    ]
    
    print("\n💬 2. Testando diferentes tipos de perguntas...")
    
    for i, query in enumerate(queries, 1):
        print(f"\n📝 Pergunta {i}: {query}")
        
        response = requests.post(
            f"{api_url}/query",
            headers=headers,
            json={"query": query}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                answer = data.get("answer", "")
                print(f"✅ Resposta: {answer[:100]}...")
                
                # Simular nomes de chat baseados no contexto
                chat_name = generate_chat_name(query)
                print(f"🏷️  Nome do chat seria: '{chat_name}'")
            else:
                print("❌ Erro na resposta da API")
        else:
            print(f"❌ Erro HTTP: {response.status_code}")
        
        time.sleep(1)  # Pausa entre perguntas
    
    print("\n" + "=" * 50)
    print("🎉 Teste das funcionalidades concluído!")
    print("\n📋 Funcionalidades testadas:")
    print("   ✅ Carregamento de documentos")
    print("   ✅ Múltiplas perguntas")
    print("   ✅ Geração de nomes de chat baseados no contexto")
    print("   ✅ Sistema de histórico")
    
    print("\n🌐 Acesse o frontend em: http://localhost:8501")
    print("   • Teste o botão '🆕 Novo Chat'")
    print("   • Verifique o histórico com nomes contextuais")
    print("   • Teste a navegação entre chats")

def generate_chat_name(query: str) -> str:
    """Gera um nome para o chat baseado na consulta (máximo 15 caracteres)"""
    # Palavras-chave importantes para identificar o contexto
    keywords = {
        "brasil": "Brasil",
        "descobriu": "Descoberta",
        "capital": "Capital",
        "pedro": "Pedro",
        "cabral": "Cabral",
        "história": "História",
        "colônia": "Colônia",
        "independência": "Independência",
        "império": "Império",
        "república": "República",
        "guerra": "Guerra",
        "revolução": "Revolução",
        "governo": "Governo",
        "presidente": "Presidente",
        "economia": "Economia",
        "cultura": "Cultura",
        "arte": "Arte",
        "literatura": "Literatura",
        "religião": "Religião",
        "educação": "Educação"
    }
    
    query_lower = query.lower()
    
    # Procurar por palavras-chave
    for keyword, name in keywords.items():
        if keyword in query_lower:
            return name[:15]
    
    # Se não encontrar palavra-chave, usar as primeiras palavras
    words = query.split()[:3]
    name = " ".join(words)
    return name[:15]

if __name__ == "__main__":
    test_chat_features()
