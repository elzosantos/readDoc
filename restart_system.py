#!/usr/bin/env python3
"""
Script para reiniciar o sistema TasqAI de forma limpa
"""

import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

def clear_caches():
    """Limpa todos os caches do sistema"""
    print("🧹 Limpando caches...")
    
    # Caches Python
    cache_dirs = [
        "__pycache__",
        "backend/__pycache__",
        "frontend/__pycache__",
        ".pytest_cache",
        "backend/.pytest_cache",
        "frontend/.pytest_cache"
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"  ✅ Removido: {cache_dir}")
    
    # Caches Streamlit
    streamlit_caches = [
        ".streamlit",
        "frontend/.streamlit"
    ]
    
    for cache_dir in streamlit_caches:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir)
            print(f"  ✅ Removido: {cache_dir}")

def kill_processes():
    """Mata processos Python em execução"""
    print("🛑 Finalizando processos Python...")
    
    try:
        # Windows
        if os.name == 'nt':
            subprocess.run(["taskkill", "/F", "/IM", "python.exe"], 
                         capture_output=True, text=True)
            print("  ✅ Processos Python finalizados")
        else:
            # Linux/Mac
            subprocess.run(["pkill", "-f", "python"], 
                         capture_output=True, text=True)
            print("  ✅ Processos Python finalizados")
    except Exception as e:
        print(f"  ⚠️ Erro ao finalizar processos: {e}")

def restart_backend():
    """Reinicia o backend"""
    print("🚀 Iniciando backend...")
    
    try:
        os.chdir("backend")
        
        # Verificar se requirements.txt existe
        if os.path.exists("requirements.txt"):
            print("  📦 Instalando dependências do backend...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                         check=True)
        
        # Iniciar backend
        print("  🔧 Iniciando servidor backend...")
        backend_process = subprocess.Popen([sys.executable, "run_api.py"])
        
        os.chdir("..")
        return backend_process
        
    except Exception as e:
        print(f"  ❌ Erro ao iniciar backend: {e}")
        os.chdir("..")
        return None

def restart_frontend():
    """Reinicia o frontend"""
    print("🎨 Iniciando frontend...")
    
    try:
        os.chdir("frontend")
        
        # Verificar se requirements_frontend.txt existe
        if os.path.exists("requirements_frontend.txt"):
            print("  📦 Instalando dependências do frontend...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_frontend.txt"], 
                         check=True)
        
        # Aguardar backend estar pronto
        print("  ⏳ Aguardando backend estar pronto...")
        time.sleep(5)
        
        # Iniciar frontend
        print("  🎨 Iniciando interface Streamlit...")
        frontend_process = subprocess.Popen([sys.executable, "-m", "streamlit", "run", "streamlit_app.py", 
                                           "--server.port", "8501", "--server.address", "localhost"])
        
        os.chdir("..")
        return frontend_process
        
    except Exception as e:
        print(f"  ❌ Erro ao iniciar frontend: {e}")
        os.chdir("..")
        return None

def main():
    """Função principal"""
    print("🔄 Reiniciando Sistema TasqAI...")
    print("=" * 50)
    
    # 1. Finalizar processos
    kill_processes()
    time.sleep(2)
    
    # 2. Limpar caches
    clear_caches()
    
    # 3. Reiniciar backend
    backend_process = restart_backend()
    if not backend_process:
        print("❌ Falha ao iniciar backend. Abortando.")
        return
    
    # 4. Reiniciar frontend
    frontend_process = restart_frontend()
    if not frontend_process:
        print("❌ Falha ao iniciar frontend. Abortando.")
        backend_process.terminate()
        return
    
    print("=" * 50)
    print("✅ Sistema reiniciado com sucesso!")
    print("🌐 Frontend: http://localhost:8501")
    print("🔧 Backend: http://localhost:8000")
    print("=" * 50)
    print("Pressione Ctrl+C para parar o sistema")
    
    try:
        # Manter processos rodando
        while True:
            time.sleep(1)
            
            # Verificar se processos ainda estão rodando
            if backend_process.poll() is not None:
                print("❌ Backend parou inesperadamente")
                break
                
            if frontend_process.poll() is not None:
                print("❌ Frontend parou inesperadamente")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Parando sistema...")
        backend_process.terminate()
        frontend_process.terminate()
        print("✅ Sistema parado com sucesso!")

if __name__ == "__main__":
    main()
