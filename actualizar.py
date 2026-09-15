import os
import re
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

    # Interceptamos las peticiones de red para cazar el token al vuelo
    def intercept_request(request):
        global encontrado_token
        if not encontrado_token:
            headers = request.headers
            # Buscamos en las cabeceras comunes de autorización
            for header_name, header_val in headers.items():
                if 'authorization' in header_name.lower() or 'token' in header_name.lower() or 'apikey' in header_name.lower():
                    if len(header_val) > 20:
                        encontrado_token = header_val.replace("Bearer ", "").replace("bearer ", "")
                        print(f"¡Token capturado desde cabecera '{header_name}': {encontrado_token[:30]}...!")
            
            # También revisamos si viaja en la URL de la petición
            url = request.url
            if 'token=' in url or 'access_token=' in url:
                match = re.search(r'(?:token|access_token)=([a-zA-Z0-9_\-\.]+)', url)
                if match:
                    encontrado_token = match.group(1)
                    print(f"¡Token capturado desde la URL: {encontrado_token[:30]}...!")

    page.on("request", intercept_request)

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Esperando acceso y actividad en la plataforma...")
    print("Navega un segundo por la página o haz clic en algún canal para que el navegador genere peticiones...")
    
    # Esperamos hasta 60 segundos o hasta que capturemos el token por la red
    import time
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 60:
        page.wait_for_timeout(1000)

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token por la red. Asegúrate de hacer clic en un canal mientras corre.")
    exit(1)

print("¡Token obtenido con éxito!")

carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                contenido_actualizado = re.sub(r'(tok_|eyJ0eXAiO)[a-zA-Z0-9_\-\.]+', f"{encontrado_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
