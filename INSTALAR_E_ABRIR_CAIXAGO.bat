@echo off
title CaixaGo - Instalacao e Execucao
cd /d "%~dp0"

echo ==========================================
echo         CAIXAGO ALPHA 0.0.1
echo ==========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo Python nao foi encontrado neste computador.
    echo.
    echo Instale o Python pelo site oficial e marque:
    echo "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

if not exist ".venv\Scripts\python.exe" (
    echo Criando ambiente virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo Nao foi possivel criar o ambiente virtual.
        pause
        exit /b 1
    )
)

echo Instalando dependencias...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Ocorreu um problema ao instalar as dependencias.
    pause
    exit /b 1
)

echo.
echo Abrindo o CaixaGo...
".venv\Scripts\python.exe" main.py

if errorlevel 1 (
    echo.
    echo O CaixaGo encontrou um erro ao iniciar.
    pause
)
