#!/usr/bin/env python3
"""
Script para iniciar o sistema completo (backend + frontend)
"""

import os
import sys
import subprocess
import time
import threading
import signal

def start_backend():
    """Inicia o backend em uma thread separada"""
    try:
        os.chdir("backend")
        subprocess.run([sys.executable, "start_api.py"])
    except Exception as e:
        print(f"❌ Erro no backend: {e}")

def start_frontend():
    """Inicia o frontend em uma thread separada"""
    try:
        time.sleep(5)  # Aguardar backend iniciar
        os.chdir("frontend")
        subprocess.run([sys.executable, "run_frontend_simple.py"])
    except Exception as e:
        print(f"❌ Erro no frontend: {e}")

def signal_handler(sig, frame):
    """Handler para interrupção"""
    print("\n🛑 Parando sistema completo...")
    sys.exit(0)

def main():
    print("🚀 Iniciando Sistema Completo - Busca de Documentos com IA")
    print("=" * 70)
    
    # Verificar estrutura
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Erro: Estrutura de pastas não encontrada!")
        print("   Certifique-se de que as pastas 'backend' e 'frontend' existem.")
        sys.exit(1)
    
    # Configurar handler de sinal
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🔧 Iniciando backend...")
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    print("⏳ Aguardando backend inicializar...")
    time.sleep(8)
    
    print("🎨 Iniciando frontend...")
    frontend_thread = threading.Thread(target=start_frontend, daemon=True)
    frontend_thread.start()
    
    print("=" * 70)
    print("✅ Sistema iniciado com sucesso!")
    print("📖 Backend: http://localhost:8000/docs")
    print("🎨 Frontend: http://localhost:8501")
    print("=" * 70)
    print("💡 Pressione Ctrl+C para parar o sistema")
    
    try:
        # Manter o script rodando
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Sistema interrompido pelo usuário")
        sys.exit(0)

if __name__ == "__main__":
    main()
