#!/usr/bin/env python3
"""
Script para iniciar o frontend do sistema de busca de documentos
"""

import os
import sys
import subprocess
import time

def main():
    print("🎨 Iniciando Frontend - Interface de Chat com IA")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("frontend"):
        print("❌ Erro: Pasta 'frontend' não encontrada!")
        print("   Execute este script a partir da raiz do projeto.")
        sys.exit(1)
    
    # Mudar para o diretório frontend
    os.chdir("frontend")
    
    # Verificar se as dependências estão instaladas
    try:
        import streamlit
        import requests
        print("✅ Dependências verificadas!")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("   Execute: pip install -r requirements_frontend.txt")
        sys.exit(1)
    
    print("🔧 Iniciando interface web...")
    print("📱 Interface: http://localhost:8501")
    print("🔗 Certifique-se de que o backend está rodando em: http://localhost:8000")
    print("=" * 60)
    
    # Iniciar o Streamlit
    try:
        subprocess.run([sys.executable, "run_frontend_simple.py"])
    except KeyboardInterrupt:
        print("\n🛑 Interface interrompida pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
