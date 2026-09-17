@echo off
chcp 65001 > nul
echo ========================================
echo    ACTUALIZADOR Y SUBIDA A GITHUB - NICO
echo ========================================
echo.

echo [1/4] Sincronizando con GitHub (Trayendo cambios previos)...
git pull origin main

echo.
set /p nuevo_servidor="1. Pega la parte del servidor (ej: https://edge-live01-hr.cvattv.com.ar): "
echo.
set /p nuevo_token="2. Pega el token nuevo aqui y presiona Enter: "

REM 1. Modifica el archivo base reemplazando servidor y token
powershell -Command "$content = Get-Content 'base.m3u' -Encoding UTF8; $content = $content -replace '\{\{SERVIDOR\}\}', '%nuevo_servidor%'; $content = $content -replace '\{\{TOKEN\}\}', '%nuevo_token%'; Set-Content 'nico' -Value $content -Encoding UTF8"

echo.
echo [2/4] Archivo 'nico' generado correctamente.
echo [3/4] Preparando commit local...

REM 2. Comandos de Git para empaquetar
git add .
git commit -m "Actualizacion automatica de servidor y token"

echo [4/4] Subiendo cambios a GitHub...
git push origin main

echo.
echo ========================================
echo ¡Listo! Actualizado en PC y en GitHub.
echo ========================================
pause