"""
Script principal para executar todos os testes do sistema.
"""

import os
import sys
import time
import subprocess
from typing import Dict, List, Tuple

def print_header(title: str):
    """Imprime cabeçalho formatado."""
    print("\n" + "=" * 80)
    print(f"🧪 {title}")
    print("=" * 80)

def print_section(title: str):
    """Imprime seção formatada."""
    print(f"\n📋 {title}")
    print("-" * 60)

def run_backend_tests() -> Tuple[int, int, List[str]]:
    """Executa testes do backend."""
    print_section("Executando Testes do Backend")
    
    try:
        # Mudar para o diretório backend
        os.chdir("backend")
        
        # Executar testes do backend
        result = subprocess.run([
            sys.executable, "test_comprehensive_api.py"
        ], capture_output=True, text=True, timeout=300)
        
        # Voltar para o diretório raiz
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Testes do Backend executados com sucesso!")
            print(result.stdout)
            return 0, 0, []
        else:
            print("❌ Erros nos testes do Backend:")
            print(result.stderr)
            return 0, 1, [result.stderr]
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout nos testes do Backend")
        return 0, 1, ["Timeout nos testes do Backend"]
    except Exception as e:
        print(f"❌ Erro ao executar testes do Backend: {str(e)}")
        return 0, 1, [str(e)]

def run_frontend_tests() -> Tuple[int, int, List[str]]:
    """Executa testes do frontend."""
    print_section("Executando Testes do Frontend")
    
    try:
        # Mudar para o diretório frontend
        os.chdir("frontend")
        
        # Executar testes do frontend
        result = subprocess.run([
            sys.executable, "test_frontend_comprehensive.py"
        ], capture_output=True, text=True, timeout=300)
        
        # Voltar para o diretório raiz
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Testes do Frontend executados com sucesso!")
            print(result.stdout)
            return 0, 0, []
        else:
            print("❌ Erros nos testes do Frontend:")
            print(result.stderr)
            return 0, 1, [result.stderr]
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout nos testes do Frontend")
        return 0, 1, ["Timeout nos testes do Frontend"]
    except Exception as e:
        print(f"❌ Erro ao executar testes do Frontend: {str(e)}")
        return 0, 1, [str(e)]

def run_session_tests() -> Tuple[int, int, List[str]]:
    """Executa testes de persistência de sessão."""
    print_section("Executando Testes de Persistência de Sessão")
    
    try:
        # Mudar para o diretório frontend
        os.chdir("frontend")
        
        # Executar testes de sessão
        result = subprocess.run([
            sys.executable, "test_session_persistence.py"
        ], capture_output=True, text=True, timeout=300)
        
        # Voltar para o diretório raiz
        os.chdir("..")
        
        if result.returncode == 0:
            print("✅ Testes de Sessão executados com sucesso!")
            print(result.stdout)
            return 0, 0, []
        else:
            print("❌ Erros nos testes de Sessão:")
            print(result.stderr)
            return 0, 1, [result.stderr]
            
    except subprocess.TimeoutExpired:
        print("⏰ Timeout nos testes de Sessão")
        return 0, 1, ["Timeout nos testes de Sessão"]
    except Exception as e:
        print(f"❌ Erro ao executar testes de Sessão: {str(e)}")
        return 0, 1, [str(e)]

def check_system_health() -> bool:
    """Verifica se o sistema está funcionando."""
    print_section("Verificando Saúde do Sistema")
    
    try:
        import requests
        
        # Verificar se a API está rodando
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ API Backend está funcionando")
                api_health = True
            else:
                print("❌ API Backend retornou erro")
                api_health = False
        except requests.exceptions.RequestException:
            print("❌ API Backend não está acessível")
            api_health = False
        
        # Verificar se o Frontend está rodando
        try:
            response = requests.get("http://localhost:8501", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend está funcionando")
                frontend_health = True
            else:
                print("❌ Frontend retornou erro")
                frontend_health = False
        except requests.exceptions.RequestException:
            print("❌ Frontend não está acessível")
            frontend_health = False
        
        return api_health and frontend_health
        
    except ImportError:
        print("⚠️ requests não está instalado, pulando verificação de saúde")
        return True

def test_api_endpoints() -> Tuple[int, int, List[str]]:
    """Testa endpoints da API diretamente."""
    print_section("Testando Endpoints da API")
    
    try:
        import requests
        
        # Testar endpoint de health
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ GET /health - OK")
                health_ok = True
            else:
                print(f"❌ GET /health - Erro {response.status_code}")
                health_ok = False
        except Exception as e:
            print(f"❌ GET /health - Erro: {str(e)}")
            health_ok = False
        
        # Testar endpoint de login
        try:
            login_data = {
                "email": "admin@test.com",
                "password": "admin123"
            }
            response = requests.post("http://localhost:8000/auth/login", json=login_data, timeout=5)
            if response.status_code == 200:
                print("✅ POST /auth/login - OK")
                login_ok = True
            else:
                print(f"❌ POST /auth/login - Erro {response.status_code}")
                login_ok = False
        except Exception as e:
            print(f"❌ POST /auth/login - Erro: {str(e)}")
            login_ok = False
        
        # Testar endpoint de status de documentos
        try:
            headers = {"Authorization": "Bearer seu_token_secreto_aqui"}
            response = requests.get("http://localhost:8000/documents/status", headers=headers, timeout=5)
            if response.status_code == 200:
                print("✅ GET /documents/status - OK")
                status_ok = True
            else:
                print(f"❌ GET /documents/status - Erro {response.status_code}")
                status_ok = False
        except Exception as e:
            print(f"❌ GET /documents/status - Erro: {str(e)}")
            status_ok = False
        
        if health_ok and login_ok and status_ok:
            return 3, 0, []
        else:
            return 0, 3, ["Alguns endpoints falharam"]
            
    except ImportError:
        print("⚠️ requests não está instalado, pulando testes de endpoints")
        return 0, 0, []

def generate_test_report(total_passed: int, total_failed: int, all_errors: List[str]):
    """Gera relatório final dos testes."""
    print_header("RELATÓRIO FINAL DOS TESTES")
    
    print(f"📊 Resumo Geral:")
    print(f"   ✅ Testes que passaram: {total_passed}")
    print(f"   ❌ Testes que falharam: {total_failed}")
    print(f"   📈 Taxa de sucesso: {(total_passed/(total_passed+total_failed)*100):.1f}%")
    
    if all_errors:
        print(f"\n🔍 Erros Encontrados ({len(all_errors)}):")
        for i, error in enumerate(all_errors, 1):
            print(f"   {i}. {error}")
    
    print(f"\n📋 Recomendações:")
    if total_failed == 0:
        print("   🎉 Todos os testes passaram! O sistema está funcionando perfeitamente.")
    elif total_failed <= 2:
        print("   ⚠️ Poucos erros encontrados. Sistema está funcionando bem com pequenos ajustes necessários.")
    else:
        print("   🚨 Múltiplos erros encontrados. Revisão e correção necessárias.")
    
    print(f"\n⏰ Testes executados em: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Função principal."""
    print_header("SISTEMA DE TESTES ABRANGENTES - TasqAI")
    print("Este script executa todos os testes do sistema para validar funcionalidades.")
    
    # Verificar se estamos no diretório correto
    if not os.path.exists("backend") or not os.path.exists("frontend"):
        print("❌ Erro: Execute este script no diretório raiz do projeto")
        return
    
    total_passed = 0
    total_failed = 0
    all_errors = []
    
    # 1. Verificar saúde do sistema
    system_healthy = check_system_health()
    if not system_healthy:
        print("⚠️ Sistema não está totalmente funcional, mas continuando com os testes...")
    
    # 2. Testar endpoints da API
    passed, failed, errors = test_api_endpoints()
    total_passed += passed
    total_failed += failed
    all_errors.extend(errors)
    
    # 3. Executar testes do backend
    passed, failed, errors = run_backend_tests()
    total_passed += passed
    total_failed += failed
    all_errors.extend(errors)
    
    # 4. Executar testes do frontend
    passed, failed, errors = run_frontend_tests()
    total_passed += passed
    total_failed += failed
    all_errors.extend(errors)
    
    # 5. Executar testes de sessão
    passed, failed, errors = run_session_tests()
    total_passed += passed
    total_failed += failed
    all_errors.extend(errors)
    
    # 6. Gerar relatório final
    generate_test_report(total_passed, total_failed, all_errors)
    
    # 7. Retornar código de saída
    if total_failed == 0:
        print("\n🎉 Todos os testes passaram com sucesso!")
        return 0
    else:
        print(f"\n⚠️ {total_failed} testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
