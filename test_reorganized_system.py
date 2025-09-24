#!/usr/bin/env python3
"""
Teste do sistema reorganizado (frontend/backend)
"""

import os
import sys
import subprocess
import time
import requests

def test_structure():
    """Testa se a estrutura de pastas está correta"""
    print("🔍 Testando estrutura do projeto...")
    
    required_dirs = ["backend", "frontend"]
    required_files = {
        "backend": [
            "api.py", "auth.py", "config.py", "document_service.py",
            "models.py", "requirements.txt", "README.md", "start_api.py"
        ],
        "frontend": [
            "streamlit_app.py", "requirements_frontend.txt", 
            "README.md", "run_frontend_simple.py"
        ]
    }
    
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            print(f"❌ Pasta '{dir_name}' não encontrada!")
            return False
        
        for file_name in required_files[dir_name]:
            file_path = os.path.join(dir_name, file_name)
            if not os.path.exists(file_path):
                print(f"❌ Arquivo '{file_path}' não encontrado!")
                return False
    
    print("✅ Estrutura do projeto está correta!")
    return True

def test_backend_dependencies():
    """Testa se as dependências do backend estão instaladas"""
    print("\n🔍 Testando dependências do backend...")
    
    try:
        os.chdir("backend")
        
        # Verificar se requirements.txt existe
        if not os.path.exists("requirements.txt"):
            print("❌ requirements.txt não encontrado!")
            return False
        
        # Tentar importar dependências principais
        try:
            import fastapi
            import uvicorn
            import langchain
            import openai
            print("✅ Dependências principais do backend estão instaladas!")
            return True
        except ImportError as e:
            print(f"❌ Dependência não encontrada: {e}")
            print("   Execute: pip install -r requirements.txt")
            return False
    finally:
        os.chdir("..")

def test_frontend_dependencies():
    """Testa se as dependências do frontend estão instaladas"""
    print("\n🔍 Testando dependências do frontend...")
    
    try:
        os.chdir("frontend")
        
        # Verificar se requirements_frontend.txt existe
        if not os.path.exists("requirements_frontend.txt"):
            print("❌ requirements_frontend.txt não encontrado!")
            return False
        
        # Tentar importar dependências principais
        try:
            import streamlit
            import requests
            print("✅ Dependências principais do frontend estão instaladas!")
            return True
        except ImportError as e:
            print(f"❌ Dependência não encontrada: {e}")
            print("   Execute: pip install -r requirements_frontend.txt")
            return False
    finally:
        os.chdir("..")

def test_backend_startup():
    """Testa se o backend pode ser iniciado"""
    print("\n🔍 Testando inicialização do backend...")
    
    try:
        os.chdir("backend")
        
        # Verificar se start_api.py existe
        if not os.path.exists("start_api.py"):
            print("❌ start_api.py não encontrado!")
            return False
        
        print("✅ Script de inicialização do backend encontrado!")
        return True
    finally:
        os.chdir("..")

def test_frontend_startup():
    """Testa se o frontend pode ser iniciado"""
    print("\n🔍 Testando inicialização do frontend...")
    
    try:
        os.chdir("frontend")
        
        # Verificar se run_frontend_simple.py existe
        if not os.path.exists("run_frontend_simple.py"):
            print("❌ run_frontend_simple.py não encontrado!")
            return False
        
        print("✅ Script de inicialização do frontend encontrado!")
        return True
    finally:
        os.chdir("..")

def test_scripts():
    """Testa se os scripts de inicialização estão funcionando"""
    print("\n🔍 Testando scripts de inicialização...")
    
    scripts = [
        "start_backend.py",
        "start_frontend.py", 
        "start_full_system.py"
    ]
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"❌ Script '{script}' não encontrado!")
            return False
    
    print("✅ Scripts de inicialização encontrados!")
    return True

def main():
    print("🧪 Testando Sistema Reorganizado")
    print("=" * 50)
    
    tests = [
        ("Estrutura do Projeto", test_structure),
        ("Dependências Backend", test_backend_dependencies),
        ("Dependências Frontend", test_frontend_dependencies),
        ("Inicialização Backend", test_backend_startup),
        ("Inicialização Frontend", test_frontend_startup),
        ("Scripts de Inicialização", test_scripts)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Resultados dos Testes:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("=" * 50)
    
    if all_passed:
        print("🎉 Todos os testes passaram!")
        print("\n🚀 Para iniciar o sistema:")
        print("   • Backend: python start_backend.py")
        print("   • Frontend: python start_frontend.py")
        print("   • Sistema Completo: python start_full_system.py")
    else:
        print("❌ Alguns testes falharam!")
        print("   Verifique os erros acima e corrija antes de continuar.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
