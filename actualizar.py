import os
import re
import json
from playwright.sync_api import sync_playwright

# Carpeta local exclusiva para guardar tu sesión de forma segura
USER_DATA_DIR = "./flow_profile"

print("Iniciando navegador con sesión persistente...")
with sync_playwright() as p:
    # Creamos un contexto persistente local que no interfiere con tu Chrome abierto
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False, # Déjalo en False para la primera vez (luego puedes pasarlo a True si querés)
        args=["--start-maximized"]
    )
    
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/inicio", wait_until="networkidle")

    print("Esperando acceso a la plataforma...")
    print("👉 Si la ventana te pide iniciar sesión o verificar por código, hazlo manualmente en esa ventana.")
    
    # Esperamos hasta que detecte que ya entraste a la página de inicio (hasta 2 minutos para que lo hagas tranquilo la primera vez)
    try:
        page.wait_for_url("**/inicio**", timeout=120000)
        print("¡Sesión detectada con éxito!")
    except Exception as e:
        print(f"Tiempo de espera agotado para el login manual: {e}")

    page.wait_for_timeout(4000)

    # Extraer el token fresco del Local Storage
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

print("¡Token extraído y guardado correctamente!")

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
