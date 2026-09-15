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
            # Capturamos cualquier petición que lleve un token o parámetro de autenticación
            if 'token=' in url or 'access_token=' in url or 'auth=' in url:
                match = re.search(r'(?:token|access_token|auth)=([a-zA-Z0-9_\-\.]+)', url)
                if match:
                    val = match.group(1)
                    if len(val) > 20: # Aseguramos que sea un token largo válido
                        encontrado_token = val
                        print(f"\n¡Token capturado con éxito: {encontrado_token[:30]}...!")

    page.on("request", intercept_request)

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("\n----------------------------------------------------")
    print("¡Navegador abierto! Haz clic en la guía o en un canal.")
    print("----------------------------------------------------\n")

    # Damos tiempo para que cargue y capture el token al navegar
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 90:
        page.wait_for_timeout(1000)

    if encontrado_token:
        page.wait_for_timeout(2000)

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token. Asegúrate de navegar un segundo.")
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

                # Reemplazo universal: busca 'token=' y actualiza todo el valor posterior hasta el próximo '&' o comilla
                contenido_actualizado = re.sub(r'(token=)[^&\s"\']+', rf'\1{encontrado_token}', contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"¡Proceso finalizado con éxito! Archivos modificados: {modificados}")
