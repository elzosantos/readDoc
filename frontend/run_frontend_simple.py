"""
Script simplificado para executar o frontend Streamlit.
"""

import subprocess
import sys

def main():
    print("🚀 Iniciando Frontend Streamlit...")
    print("📱 Interface disponível em: http://localhost:8501")
    print("🔗 Certifique-se de que a API está rodando em: http://localhost:8000")
    print("=" * 60)
    
    try:
        # Executar Streamlit diretamente
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro ao executar frontend: {e}")

if __name__ == "__main__":
    main()
