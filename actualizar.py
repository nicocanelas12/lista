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

    # Damos unos segundos extra para que termine de cargar todos los datos internos de la sesión
    page.wait_for_timeout(6000)

    # Diagnóstico: Inspeccionamos todas las llaves del Local Storage para ver dónde guarda Flow el token
    keys_in_storage = page.evaluate("() => Object.keys(window.localStorage)")
    print(f"Llaves disponibles en Local Storage: {keys_in_storage}")

    nuevo_token = None
    
    # Intentamos buscar en la llave anterior u otras comunes de Flow
    for key_name in ['fenix_flow/accessToken', 'access_token', 'token', 'auth', 'user']:
        if key_name in keys_in_storage:
            val = page.evaluate(f"() => window.localStorage.getItem('{key_name}')")
            print(f"Revisando llave '{key_name}': {val[:100] if val else 'Vacío'}")
            if val:
                try:
                    # Si es un JSON, intentamos extraer el idToken o token
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        nuevo_token = parsed.get("idToken") or parsed.get("accessToken") or parsed.get("token")
                    else:
                        nuevo_token = val
                except:
                    # Si no es JSON, asumimos que el valor mismo es el token
                    nuevo_token = val
                if nuevo_token:
                    break

    # Si aún no lo encontramos, buscamos en las cookies por si acaso
    if not nuevo_token:
        print("Buscando en cookies de sesión...")
        cookies = context.cookies()
        for cookie in cookies:
            if 'token' in cookie['name'].lower() or 'auth' in cookie['name'].lower():
                print(f"Encontrada cookie relevante: {cookie['name']}")
                nuevo_token = cookie['value']
                break

    context.close()

if not nuevo_token:
    print("No se pudo extraer el token automáticamente con las llaves conocidas.")
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
