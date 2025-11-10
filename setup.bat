@echo off
echo ========================================
echo Configurando Ambiente Virtual
echo ========================================
echo.

REM Verifica se o venv já existe
if exist "venv\" (
    echo [OK] Ambiente virtual ja existe
) else (
    echo [*] Criando ambiente virtual...
    python -m venv venv
    echo [OK] Ambiente virtual criado
)

echo.
echo [*] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo [*] Atualizando pip...
python -m pip install --upgrade pip

echo.
echo [*] Instalando dependencias...
pip install -r requirements.txt

echo.
echo ========================================
echo Configuracao concluida!
echo ========================================
echo.
echo Para ativar o ambiente virtual, execute:
echo   venv\Scripts\activate
echo.
echo Para desativar, execute:
echo   deactivate
echo.
pause
