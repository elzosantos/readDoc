"""
Script simples para iniciar a API.
"""

import uvicorn
import os
import sys

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🚀 Iniciando API de busca de documentos...")
    print("📖 Documentação disponível em: http://localhost:8000/docs")
    print("🔍 API disponível em: http://localhost:8000")
    
    try:
        uvicorn.run(
            "api:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n🛑 API interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar API: {e}")
