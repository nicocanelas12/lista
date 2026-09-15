import os
import re
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./flow_profile"

print("Abriendo Google Chrome...")
with sync_playwright() as p:
    # Usamos channel="chrome" para utilizar tu navegador principal con tu sesión ya iniciada
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        channel="chrome",
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    
    page = context.new_page()

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("\n----------------------------------------------------")
    print("Si te pide iniciar sesión, hazlo en esta ventana.")
    print("Presiona ENTER en esta terminal una vez que estés adentro.")
    print("----------------------------------------------------\n")

    # Esperamos a que el usuario presione ENTER en la terminal cuando ya esté logueado
    input("👉 Presiona ENTER aquí en la terminal cuando ya hayas iniciado sesión en Flow...")

    # Extraemos el token o los datos de autenticación del LocalStorage / SessionStorage
    print("Extrayendo credenciales de la sesión...")
    
    # Buscamos en localStorage
    local_storage = page.evaluate("() => JSON.stringify(window.localStorage)")
    session_storage = page.evaluate("() => JSON.stringify(window.sessionStorage)")
    
    encontrado_token = None
    
    # Buscamos patrones de token dentro del almacenamiento local
    match_token = re.search(r'(?:token|access_token|auth|idToken)[":\s]+([a-zA-Z0-9_\-\.]{20,})', local_storage + session_storage)
    if match_token:
        encontrado_token = match_token.group(1)
        print(f"¡Token extraído del almacenamiento: {encontrado_token[:30]}...!")
    else:
        # Si no está en el storage, revisamos las cookies activas
        cookies = context.cookies()
        for cookie in cookies:
            if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                encontrado_token = cookie['value']
                print(f"¡Token extraído de la cookie '{cookie['name']}': {encontrado_token[:30]}...!")
                break

    context.close()

if not encontrado_token:
    print("No se pudo extraer el token automáticamente. Asegúrate de haber iniciado sesión.")
    exit(1)

print("Actualizando listas M3U...")

carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                # Reemplazo universal en las rutas con token=
                contenido_actualizado = re.sub(r'(token=)[^&\s"\']+', rf'\1{encontrado_token}', contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"¡Proceso finalizado con éxito! Archivos modificados: {modificados}")
