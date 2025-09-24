"""
Script para executar o sistema completo (Backend + Frontend).
"""

import subprocess
import sys
import time
import threading
import os
from pathlib import Path

def run_backend():
    """Executa o backend API"""
    print("🚀 Iniciando Backend API...")
    try:
        subprocess.run([sys.executable, "run_api.py"])
    except KeyboardInterrupt:
        print("🛑 Backend interrompido")

def run_frontend():
    """Executa o frontend Streamlit"""
    print("🖥️ Iniciando Frontend Streamlit...")
    try:
        subprocess.run([sys.executable, "run_frontend.py"])
    except KeyboardInterrupt:
        print("🛑 Frontend interrompido")

def main():
    print("=" * 60)
    print("🤖 LLMChat - Sistema de Busca de Documentos com IA")
    print("=" * 60)
    print()
    print("📋 Este script irá iniciar:")
    print("   • Backend API (FastAPI) - http://localhost:8000")
    print("   • Frontend Web (Streamlit) - http://localhost:8501")
    print()
    print("🔐 Tokens disponíveis:")
    print("   • seu_token_secreto_aqui (Admin)")
    print("   • admin_token_123 (Admin)")
    print("   • user_token_456 (User)")
    print()
    print("⏳ Aguarde alguns segundos para inicialização...")
    print("=" * 60)
    
    # Verificar se os arquivos existem
    if not Path("run_api.py").exists():
        print("❌ Arquivo run_api.py não encontrado!")
        return
    
    if not Path("run_frontend.py").exists():
        print("❌ Arquivo run_frontend.py não encontrado!")
        return
    
    try:
        # Iniciar backend em thread separada
        backend_thread = threading.Thread(target=run_backend, daemon=True)
        backend_thread.start()
        
        # Aguardar um pouco para o backend inicializar
        print("⏳ Aguardando backend inicializar...")
        time.sleep(5)
        
        # Iniciar frontend
        run_frontend()
        
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar sistema: {e}")

if __name__ == "__main__":
    main()
