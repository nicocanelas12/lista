@echo off
chcp 65001 > nul
echo ========================================
echo    ACTUALIZADOR Y SUBIDA A GITHUB - NICO
echo ========================================
echo.
set /p nuevo_token="Pega el token nuevo aqui y presiona Enter: "

REM 1. Modifica el archivo base y genera el archivo 'nico' correctamente
powershell -Command "$content = Get-Content 'base.m3u' -Encoding UTF8; $content = $content -replace '\{\{TOKEN\}\}', '%nuevo_token%'; Set-Content 'nico' -Value $content -Encoding UTF8"

echo.
echo [1/2] Archivo 'nico' generado correctamente.
echo [2/2] Subiendo cambios a GitHub...

REM 2. Comandos automáticos de Git (forzando la detección del archivo 'nico')
git add .
git commit -m "Actualizacion automatica de token"
git push

echo.
echo ========================================
echo ¡Listo! Actualizado en PC y en GitHub.
echo ========================================
pause