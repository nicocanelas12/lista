import os
import re
import json
from playwright.sync_api import sync_playwright

print("Iniciando navegador con tu perfil de usuario real...")
with sync_playwright() as p:
    # Apuntamos a la ruta estándar de Chrome en Windows para usar tu sesión existente
    user_data_dir = os.path.expanduser("~") + r"\AppData\Local\Google\Chrome\User Data"
    
    try:
        # Abrimos el navegador persistente usando tu propio perfil (evita 2FA/bloqueos)
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            channel="chrome",
            headless=False,
            args=["--profile-directory=Default"]
        )
    except Exception as e:
        print(f"No se pudo abrir el perfil de Chrome predeterminado ({e}), usando navegador limpio...")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()

    page = context.new_page()

    print("Entrando directamente a Flow...")
    page.goto("https://portal.app.flow.com.ar/inicio", wait_until="networkidle")

    print("Esperando a que cargue la sesión y el Local Storage...")
    try:
        page.wait_for_url("**/inicio**", timeout=20000)
    except:
        print("Verifica si estás logueado en esta ventana del navegador.")

    page.wait_for_timeout(4000)

    # Extraer el token fresco directamente del Local Storage de tu sesión activa
    local_storage_data = page.evaluate("() => window.localStorage.getItem('fenix_flow/accessToken')")
    
    nuevo_token = None
    if local_storage_data:
        try:
            token_obj = json.loads(local_storage_data)
            nuevo_token = token_obj.get("idToken")
        except Exception as err:
            print(f"Error al parsear el JSON del token: {err}")

    context.close()

if not nuevo_token:
    print("No se pudo extraer el token automáticamente.")
    exit(1)

print("¡Token extraído con éxito desde tu sesión!")

# Actualizar archivos M3U en la carpeta nico
carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                contenido_actualizado = re.sub(r'(tok_|eyJ0eXAiO)[a-zA-Z0-9_\-\.]+', f"{nuevo_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
