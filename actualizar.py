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
    # Cambiamos a headless=False por un momento si quieres ver qué hace, 
    # o déjalo en True para que corra invisible. Usaremos True para automatización.
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/prelogin", wait_until="networkidle")

    # Hacer clic en el botón de ingresar con usuario y contraseña
    try:
        page.click("text=Ingresar con usuario y contraseña", timeout=5000)
    except:
        print("El botón de usuario/contraseña no apareció o ya estaba visible.")

    print("Esperando campos de texto...")
    # Esperamos explícitamente a que aparezca cualquier campo de entrada
    page.wait_for_selector("input", timeout=10000)

    print("Rellenando credenciales...")
    # Buscamos los inputs de forma más general por su tipo o posición si fallan los nombres
    inputs = page.locator("input")
    
    # Rellenar usuario (usualmente el primer input o el que tenga type email/text)
    page.locator("input[type='email'], input[type='text']").first.fill(username)
    # Rellenar contraseña
    page.locator("input[type='password']").first.fill(password)
    
    print("Enviando formulario...")
    # Hacer clic en el botón de login
    page.locator("button[type='submit'], button:has-text('Ingresar'), button:has-text('Iniciar sesión')").first.click()

    print("Esperando inicio de sesión y redirección...")
    try:
        page.wait_for_url("**/inicio**", timeout=35000)
    except Exception as e:
        print(f"Aviso en la redirección (continuando de todos modos): {e}")

    # Dar un pequeño respiro para que se escriba el LocalStorage
    page.wait_for_timeout(3000)

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
