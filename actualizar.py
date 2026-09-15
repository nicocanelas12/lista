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

    # Volcamos todo el contenido de Local Storage a la consola para identificar la clave exacta
    js_code = """
    () => {
        let allData = {};
        for (let i = 0; i < localStorage.length; i++) {
            let key = localStorage.key(i);
            allData[key] = localStorage.getItem(key);
        }
        return allData;
    }
    """
    storage_data = page.evaluate(js_code)
    print("--- CONTENIDO COMPLETO DE LOCAL STORAGE ---")
    for k, v in storage_data.items():
        print(f"CLAVE: {k} --> VALOR: {v[:150]}...")
    print("-------------------------------------------")

    # Buscamos de forma amplia cualquier coincidencia que parezca token o credencial
    nuevo_token = None
    for k, val in storage_data.items():
        if val:
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    # Buscamos cualquier campo clave dentro de objetos JSON almacenados
                    for sub_k, sub_v in parsed.items():
                        if isinstance(sub_v, str) and (len(sub_v) > 30 and ('token' in sub_k.lower() or 'auth' in sub_k.lower() or 'id' in sub_k.lower())):
                            print(f"¡Candidato encontrado en JSON de '{k}' -> '{sub_k}': {sub_v}")
                            nuevo_token = sub_v
                            break
            except:
                pass
            if nuevo_token:
                break

    context.close()

if not nuevo_token:
    print("No se pudo extraer el token automáticamente con el escaneo profundo.")
    exit(1)

print(f"¡Token extraído con éxito: {nuevo_token[:30]}...!")

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
