import os
import re
import time
from playwright.sync_api import sync_playwright

# Directorio base del script actual (para evitar problemas de rutas en la terminal)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "flow_profile")
CARPETA_NICO = os.path.join(BASE_DIR, "nico")

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

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Buscando las credenciales de sesión en las cookies...")
    
    # Esperamos hasta 30 segundos a que la cookie de sesión esté disponible
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 30:
        page.wait_for_timeout(1000)
        for cookie in context.cookies():
            if 'idtoken' in cookie['name'].lower() or 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                val = cookie['value']
                if len(val) > 20:
                    encontrado_token = val
                    break

    context.close()

if not encontrado_token:
    print("\nNo se pudo capturar el token automáticamente. Asegúrate de haber iniciado sesión.")
    exit(1)

print(f"\n¡Token capturado con éxito: {encontrado_token[:30]}...!")
print(f"Buscando carpeta 'nico' en: {CARPETA_NICO}")

modificados = 0

if os.path.exists(CARPETA_NICO):
    # Recorremos de forma recursiva por si hay subcarpetas
    for root, dirs, files in os.walk(CARPETA_NICO):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                # Reemplazo robusto para cualquier variante de tok_
                contenido_actualizado, count = re.subn(r'tok_[^/]+', f'tok_{encontrado_token}', contenido)

                if count > 0:
                    with open(ruta_archivo, "w", encoding="utf-8") as f:
                        f.write(contenido_actualizado)
                    modificados += 1
                    print(f"-> ¡Actualizado con éxito: {file} ({count} cambios)!")
                else:
                    print(f"-> El archivo {file} no tenía la estructura 'tok_' para actualizar.")
else:
    print(f"¡Error! No se encontró la carpeta 'nico' en la ruta: {CARPETA_NICO}")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
