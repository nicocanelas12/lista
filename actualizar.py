import os
import re
import json
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./flow_profile"

print("Iniciando navegador con sesion persistente...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        args=["--start-maximized"]
    )
    
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/inicio", wait_until="networkidle")

    print("Esperando acceso a la plataforma...")
    print("ATENCION: Si la ventana te pide iniciar sesion o verificar por codigo, hazlo manualmente en esa ventana.")
    
    try:
        page.wait_for_url("**/inicio**", timeout=120000)
        print("Sesion detectada con exito!")
    except Exception as e:
        print(f"Tiempo de espera agotado para el login manual: {e}")

    page.wait_for_timeout(4000)

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
    print("No se pudo extraer el token automaticamente.")
    exit(1)

print("Token extraido y guardado correctamente!")

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
