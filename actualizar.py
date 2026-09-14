import os
import re
import json
from playwright.sync_api import sync_playwright

username = os.environ.get("FLOW_USER")
password = os.environ.get("FLOW_PASS")

if not username or not password:
    raise ValueError("Faltan las credenciales FLOW_USER o FLOW_PASS.")

print("Iniciando navegador automatizado...")
with sync_playwright() as p:
    # Usamos headless=True para que corra en segundo plano de forma silenciosa
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/prelogin", wait_until="networkidle")

    # Hacer clic en ingresar con usuario y contraseña si aparece el botón
    try:
        page.get_by_text("Ingresar con usuario y contraseña").click(timeout=5000)
    except:
        pass

    print("Rellenando credenciales...")
    # Selectores para los campos de usuario y contraseña
    page.fill("input[type='email'], input[name='username'], input[id='username']", username)
    page.fill("input[type='password'], input[name='password'], input[id='password']", password)
    
    # Click en el botón de enviar
    page.click("button[type='submit'], button:has-text('Ingresar'), button:has-text('Iniciar sesión')")

    print("Esperando inicio de sesión y redirección...")
    try:
        page.wait_for_url("**/inicio**", timeout=30000)
    except Exception as e:
        print(f"Advertencia en la redirección: {e}")

    # Extraer el objeto de sesión del Local Storage
    local_storage_data = page.evaluate("() => window.localStorage.getItem('fenix_flow/accessToken')")
    
    nuevo_token = None
    if local_storage_data:
        try:
            token_obj = json.loads(local_storage_data)
            nuevo_token = token_obj.get("idToken")
        except Exception as err:
            print(f"Error al parsear el JSON del token: {err}")

    browser.close()

if not nuevo_token:
    print("No se pudo extraer el token automáticamente del navegador.")
    exit(1)

print("¡Token extraído con éxito por el navegador!")

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

                # Reemplazar tokens anteriores por el nuevo token extraído
                contenido_actualizado = re.sub(r'(tok_|eyJ0eXAiO)[a-zA-Z0-9_\-\.]+', f"{nuevo_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
