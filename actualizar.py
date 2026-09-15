import os
import re
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./flow_profile"
encontrado_token = None

print("Iniciando automatización de Flow...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        channel="chrome",
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    
    page = context.new_page()

    print("Entrando al portal...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Buscando las credenciales de sesión activas...")
    
    # Damos hasta 25 segundos para revisar las cookies de forma continua mientras la página se estabiliza
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 25:
        page.wait_for_timeout(1000)
        
        # Revisamos directamente el almacenamiento de cookies del navegador
        for cookie in context.cookies():
            # Buscamos la cookie exacta que maneja Flow para el token de sesión
            if 'idtoken' in cookie['name'].lower() or 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                val = cookie['value']
                if len(val) > 20:
                    encontrado_token = val
                    break

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token. Asegúrate de estar logueado.")
    exit(1)

print(f"\n¡Token capturado con éxito: {encontrado_token[:30]}...!")

# Verificamos y actualizamos la carpeta nico
ruta_actual = os.getcwd()
carpeta_nico = os.path.join(ruta_actual, "nico")
modificados = 0

if os.path.exists(carpeta_nico):
    archivos = os.listdir(carpeta_nico)
    for file in archivos:
        if file.endswith((".m3u", ".m3u8", ".txt")):
            ruta_archivo = os.path.join(carpeta_nico, file)
            with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read()

            # Reemplazo ultra preciso de tok_ hasta la barra /
            contenido_actualizado, count = re.subn(r'tok_[^/]+', f'tok_{encontrado_token}', contenido)

            if count > 0:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                modificados += 1
                print(f"-> ¡Actualizado con éxito: {file} ({count} cambios)!")
else:
    print("No se encontró la carpeta 'nico'.")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
