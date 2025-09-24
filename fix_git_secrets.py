"""
Script para ajudar a resolver problemas de secrets no Git.
"""

import subprocess
import os
import sys

def run_command(command):
    """Executa um comando e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def main():
    print("🔧 Script para Resolver Problemas de Secrets no Git")
    print("=" * 60)
    
    print("\n📋 Opções disponíveis:")
    print("1. Permitir secret temporariamente (usar link do GitHub)")
    print("2. Remover secret do histórico (recomendado)")
    print("3. Criar novo repositório limpo")
    print("4. Verificar status atual")
    
    choice = input("\nEscolha uma opção (1-4): ").strip()
    
    if choice == "1":
        print("\n🔗 Para permitir o secret temporariamente:")
        print("1. Acesse este link:")
        print("   https://github.com/elzosantos/readDoc/security/secret-scanning/unblock-secret/337oloCKAh95IRdIhOYCiAu0eot")
        print("2. Clique em 'Allow secret'")
        print("3. Execute: git push origin main")
        
    elif choice == "2":
        print("\n🗑️ Removendo secret do histórico...")
        
        # Verificar se há mudanças não commitadas
        success, stdout, stderr = run_command("git status --porcelain")
        if stdout.strip():
            print("⚠️ Há mudanças não commitadas. Fazendo commit...")
            run_command("git add .")
            run_command('git commit -m "temp: commit before cleaning history"')
        
        # Remover .env do histórico
        print("Removendo .env do histórico...")
        success, stdout, stderr = run_command('git filter-branch --force --index-filter "git rm --cached --ignore-unmatch .env" --prune-empty --tag-name-filter cat -- --all')
        
        if success:
            print("✅ Secret removido do histórico!")
            print("Agora execute: git push origin main --force")
        else:
            print("❌ Erro ao remover secret:", stderr)
            
    elif choice == "3":
        print("\n🆕 Criando novo repositório limpo...")
        
        # Fazer backup dos arquivos importantes
        print("Fazendo backup dos arquivos...")
        run_command("mkdir -p backup")
        run_command("cp -r *.py *.md *.txt backup/ 2>/dev/null || true")
        run_command("cp -r .streamlit backup/ 2>/dev/null || true")
        
        # Remover .git
        print("Removendo histórico Git...")
        run_command("rm -rf .git")
        
        # Inicializar novo repositório
        print("Inicializando novo repositório...")
        run_command("git init")
        run_command("git add .")
        run_command('git commit -m "Initial commit: Sistema LLMChat completo"')
        
        print("✅ Novo repositório criado!")
        print("Agora adicione o remote: git remote add origin https://github.com/elzosantos/readDoc.git")
        print("E faça o push: git push origin main --force")
        
    elif choice == "4":
        print("\n📊 Status atual do Git:")
        success, stdout, stderr = run_command("git status")
        print(stdout)
        
        print("\n📝 Últimos commits:")
        success, stdout, stderr = run_command("git log --oneline -5")
        print(stdout)
        
    else:
        print("❌ Opção inválida!")
        return
    
    print("\n" + "=" * 60)
    print("💡 Dicas importantes:")
    print("• Sempre use .gitignore para arquivos sensíveis")
    print("• Nunca commite arquivos .env com chaves reais")
    print("• Use variáveis de ambiente ou arquivos de configuração separados")
    print("• Considere usar GitHub Secrets para chaves de API")

if __name__ == "__main__":
    main()
