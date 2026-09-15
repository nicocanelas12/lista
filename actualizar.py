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

    def intercept_request(request):
        global encontrado_token
        if not encontrado_token:
            url = request.url
            if 'token=' in url or 'access_token=' in url or 'auth=' in url:
                match = re.search(r'(?:token|access_token|auth)=([a-zA-Z0-9_\-\.]+)', url)
                if match:
                    val = match.group(1)
                    if len(val) > 20:
                        encontrado_token = val
                        print(f"\n¡Token capturado desde la red: {encontrado_token[:30]}...!")

    page.on("request", intercept_request)

    print("Entrando al portal...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Esperando sesión (si pide iniciar sesión, hazlo en la ventana que se abrió)...")
    
    # Damos 40 segundos. Si no estás logueado, tienes tiempo de iniciar sesión y el script lo detectará solo al entrar.
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 40:
        page.wait_for_timeout(1000)
        
        # Búsqueda dinámica de respaldo en cookies cada pocos segundos
        if not encontrado_token:
            for cookie in context.cookies():
                if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                    val = cookie['value']
                    if len(val) > 20:
                        encontrado_token = val
                        print(f"¡Token capturado desde la cookie '{cookie['name']}': {encontrado_token[:30]}...!")
                        break

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token. Asegúrate de iniciar sesión en la ventana que se abre.")
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

                # Reemplazo robusto
                contenido_actualizado = re.sub(r'(token=)[^&\s"\']+', rf'\1{encontrado_token}', contenido)
                
                if contenido_actualizado == contenido:
                    contenido_actualizado = re.sub(r'bklk[a-zA-Z0-9_\-\.]+', encontrado_token, contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"¡Proceso finalizado con éxito! Archivos modificados: {modificados}")
