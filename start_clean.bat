@echo off
echo ========================================
echo    Reiniciando Sistema TasqAI
echo ========================================

echo.
echo Parando processos Python existentes...
taskkill /F /IM python.exe 2>nul

echo.
echo Limpando caches...
if exist __pycache__ rmdir /s /q __pycache__
if exist backend\__pycache__ rmdir /s /q backend\__pycache__
if exist frontend\__pycache__ rmdir /s /q frontend\__pycache__
if exist .streamlit rmdir /s /q .streamlit
if exist frontend\.streamlit rmdir /s /q frontend\.streamlit

echo.
echo Iniciando Backend...
start "Backend TasqAI" cmd /k "cd backend && python run_api.py"

echo.
echo Aguardando 5 segundos...
timeout /t 5 /nobreak >nul

echo.
echo Iniciando Frontend...
start "Frontend TasqAI" cmd /k "cd frontend && python -m streamlit run streamlit_app.py --server.port 8501 --server.address localhost"

echo.
echo ========================================
echo    Sistema iniciado com sucesso!
echo ========================================
echo.
echo Frontend: http://localhost:8501
echo Backend:  http://localhost:8000
echo.
echo Pressione qualquer tecla para sair...
pause >nul
