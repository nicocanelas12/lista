import os
import re
import time
from playwright.sync_api import sync_playwright

USER_DATA_DIR = "./flow_profile"
encontrado_token = None

print("Iniciando navegador con sesion persistente...")
with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    
    page = context.new_page()

    def intercept_request(request):
        global encontrado_token
        if not encontrado_token:
            url = request.url
            # Buscamos tokens en las peticiones de streaming o API de Flow
            if 'token=' in url or 'access_token=' in url or 'auth=' in url:
                match = re.search(r'(?:token|access_token|auth)=([a-zA-Z0-9_\-\.]+)', url)
                if match:
                    encontrado_token = match.group(1)
                    print(f"\n¡Token capturado con éxito: {encontrado_token[:30]}...!")

    page.on("request", intercept_request)

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("\n----------------------------------------------------")
    print("¡El navegador está abierto! Haz clic en un canal para reproducirlo.")
    print("El script capturará el token en cuanto empiece a transmitir.")
    print("----------------------------------------------------\n")

    # Esperamos a que capture el token (damos hasta 2 minutos para que elijas el canal con tranquilidad)
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 120:
        page.wait_for_timeout(1000)

    if encontrado_token:
        print("Esperando 3 segundos adicionales para asegurar la captura...")
        page.wait_for_timeout(3000)

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token. Asegúrate de hacer clic en un canal.")
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

                # Reemplazamos el token donde aparezca después de 'token='
                contenido_actualizado = re.sub(r'(token=)[^&\s"]+', rf'\1{encontrado_token}', contenido)
                
                # Si tus listas usan otra estructura, barremos cadenas que empiecen con bklk
                if contenido_actualizado == contenido:
                    contenido_actualizado = re.sub(r'bklk[a-zA-Z0-9_\-\.]+', encontrado_token, contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"¡Proceso finalizado con éxito! Archivos modificados: {modificados}")
