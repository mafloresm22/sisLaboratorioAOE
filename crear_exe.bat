@echo off
echo ======================================================
echo   GENERADOR DE EJECUTABLE - SISTEMA LABORATORIO AOE
echo ======================================================
echo.

echo [1/4] Borrando versiones antiguas (build y dist)...
if exist build rd /s /q build
if exist dist rd /s /q dist

echo.
echo [2/4] Iniciando compilacion con PyInstaller...
echo (Esto puede tardar unos minutos...)
echo.

pyinstaller --noconfirm --onedir --windowed --name "SistemaLaboratorioAOE" ^
 --paths "src" ^
 --exclude-module "torch" ^
 --exclude-module "tensorflow" ^
 --exclude-module "matplotlib" ^
 --exclude-module "plotly" ^
 --exclude-module "tkinterweb" ^
 --add-data "assets;assets" ^
 --add-data "src;src" ^
 --add-data ".env;." ^
 --collect-all "customtkinter" ^
 --icon "assets/icons/dashboard/8916436_Reportes.png" ^
 src/main.py

echo.
echo [3/4] Verificando resultado...
if exist dist\SistemaLaboratorioAOE (
    echo.
    echo ¡LISTO! El ejecutado se ha creado correctamente.
    echo Ruta: dist\SistemaLaboratorioAOE\SistemaLaboratorioAOE.exe
) else (
    echo.
    echo Error: No se pudo generar el ejecutable. Revisa los mensajes de arriba.
)

echo.
echo [4/4] Proceso terminado.
pause
