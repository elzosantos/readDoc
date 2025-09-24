#!/usr/bin/env python3
"""
Script para iniciar o backend do sistema de busca de documentos
"""

import os
import sys
import subprocess

def main():
    print("🚀 Iniciando Backend - Sistema de Busca de Documentos")
    print("=" * 60)
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("backend"):
        print("❌ Erro: Pasta 'backend' não encontrada!")
        print("   Execute este script a partir da raiz do projeto.")
        sys.exit(1)
    
    # Mudar para o diretório backend
    os.chdir("backend")
    
    # Verificar se o arquivo de configuração existe
    if not os.path.exists(".env"):
        if os.path.exists("env_example.txt"):
            print("⚠️  Arquivo .env não encontrado!")
            print("   Copiando env_example.txt para .env...")
            subprocess.run(["cp", "env_example.txt", ".env"], shell=True)
            print("   ✅ Arquivo .env criado!")
            print("   📝 Edite o arquivo .env com suas configurações antes de continuar.")
            print("   🔑 Especialmente a OPENAI_API_KEY!")
            sys.exit(1)
        else:
            print("❌ Erro: Arquivo env_example.txt não encontrado!")
            sys.exit(1)
    
    # Verificar se as dependências estão instaladas
    try:
        import fastapi
        import uvicorn
        import langchain
        print("✅ Dependências verificadas!")
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("   Execute: pip install -r requirements.txt")
        sys.exit(1)
    
    print("🔧 Iniciando servidor...")
    print("📖 Documentação: http://localhost:8000/docs")
    print("🔍 API: http://localhost:8000")
    print("=" * 60)
    
    # Iniciar o servidor
    try:
        subprocess.run([sys.executable, "start_api.py"])
    except KeyboardInterrupt:
        print("\n🛑 Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
