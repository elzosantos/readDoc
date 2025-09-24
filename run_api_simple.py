"""
Script simplificado para executar a API FastAPI sem reload.
"""

import uvicorn

if __name__ == "__main__":
    print("🚀 Iniciando API de busca de documentos...")
    print("📖 Documentação disponível em: http://localhost:8000/docs")
    print("🔍 API disponível em: http://localhost:8000")
    
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Desabilitar reload para evitar problemas
        log_level="info"
    )
