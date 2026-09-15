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
            # Buscamos si el token viaja en los parámetros de la URL
            if 'token=' in url or 'access_token=' in url or 'auth=' in url:
                match = re.search(r'(?:token|access_token|auth)=([a-zA-Z0-9_\-\.]+)', url)
                if match:
                    encontrado_token = match.group(1)
                    print(f"¡Token capturado desde la URL: {encontrado_token[:30]}...!")
            
            # Revisamos las cabeceras por si viaja en la autorización
            for header_name, header_val in request.headers.items():
                if 'authorization' in header_name.lower() or 'token' in header_name.lower():
                    if len(header_val) > 20:
                        encontrado_token = header_val.replace("Bearer ", "").replace("bearer ", "")
                        print(f"¡Token capturado desde cabecera '{header_name}': {encontrado_token[:30]}...!")

    page.on("request", intercept_request)

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Esperando acceso y actividad en la plataforma...")
    print("Navega un momento por la página o haz clic en algún canal para disparar las peticiones de red...")
    
    start_time = time.time()
    while not encontrado_token and (time.time() - start_time) < 90:
        page.wait_for_timeout(1000)

    context.close()

if not encontrado_token:
    print("No se pudo capturar el token por la red. Asegúrate de hacer clic en un canal.")
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

                # Reemplazamos el token en las URLs de tus listas
                # (Actualiza esta línea si tus listas usan otro parámetro, por defecto busca token= o reemplaza cadenas anteriores que empiecen con bklk)
                contenido_actualizado = re.sub(r'(token=)[a-zA-Z0-9_\-\.]+', rf'\1{encontrado_token}', contenido)
                
                # Si tus enlaces usan otra estructura para el token, puedes usar esta alternativa para barrer el token viejo:
                contenido_actualizado = re.sub(r'bklk[a-zA-Z0-9_\-\.]+', encontrado_token, contenido_actualizado)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
