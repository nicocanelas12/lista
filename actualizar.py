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
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    
    page = context.new_page()

    print("Entrando al portal de Flow...")
    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("Esperando acceso a la plataforma...")
    print("ATENCION: Si la ventana te pide iniciar sesion o verificar por codigo, hazlo manualmente en esa ventana.")
    
    try:
        page.wait_for_url("**/inicio**", timeout=120000)
        print("Sesion detectada con exito!")
    except Exception as e:
        print(f"Tiempo de espera agotado: {e}")

    page.wait_for_timeout(6000)

    # Obtenemos las llaves del Local Storage y Session Storage
    keys_in_storage = page.evaluate("() => Object.keys(window.localStorage)")
    session_keys = page.evaluate("() => Object.keys(window.sessionStorage)")
    print(f"Local Storage: {keys_in_storage}")
    print(f"Session Storage: {session_keys}")

    nuevo_token = None

    js_code = """
    () => {
        let allData = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            allData[key] = localStorage.getItem(key);
        }
        for (let i = 0; i < sessionStorage.length; i++) {
            let key = sessionStorage.key(i);
            allData[key] = sessionStorage.getItem(key);
        }
        return allData;
    }
    """
    storage_data = page.evaluate(js_code)

    # Buscamos en todo el almacenamiento algo que parezca un token (JWT o clave larga)
    for k, val in storage_data.items():
        if val:
            # Si el valor es largo o contiene estructura de token
            if isinstance(val, str) and (len(val) > 40 or "eyJ" in val or "tok_" in val):
                print(f"Revisando clave candidata '{k}': {val[:60]}...")
                try:
                    parsed = json.loads(val)
                    if isinstance(parsed, dict):
                        # Buscamos recursivamente o por campos comunes
                        possible = parsed.get("idToken") or parsed.get("accessToken") or parsed.get("token") or parsed.get("access_token")
                        if possible:
                            nuevo_token = possible
                            print(f"¡Token encontrado dentro del JSON de '{k}'!")
                            break
                except:
                    # Si no es JSON pero tiene pinta de token directo
                    if "eyJ" in val or val.startswith("tok_"):
                        nuevo_token = val
                        print(f"¡Token directo encontrado en '{k}'!")
                        break

    # Si aún no lo encontramos, buscamos en cookies de sesión
    if not nuevo_token:
        print("Buscando en cookies de sesión...")
        cookies = context.cookies()
        for cookie in cookies:
            val = cookie['value']
            if len(val) > 40 and ('token' in cookie['name'].lower() or 'auth' in cookie['name'].lower() or 'session' in cookie['name'].lower()):
                print(f"Encontrada cookie candidata: {cookie['name']}")
                nuevo_token = val
                break

    context.close()

if not nuevo_token:
    print("No se pudo extraer el token automáticamente.")
    exit(1)

print("¡Token extraido con éxito!")

carpeta_nico = "nico"
modificados = 0

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                # Reemplazamos los tokens viejos por el nuevo encontrado
                contenido_actualizado = re.sub(r'(tok_|eyJ0eXAiO)[a-zA-Z0-9_\-\.]+', f"{nuevo_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
