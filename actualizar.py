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
    # Ponemos headless=False para que veas la ventana abrirse en tu PC 
    # y sepas exactamente qué está haciendo el script.
    browser = p.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context()
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/prelogin", wait_until="networkidle")

    print("Buscando enlace de usuario y contraseña...")
    try:
        # Intentamos hacer clic en el texto exacto del botón izquierdo
        page.click("text=Ingresar con usuario y contraseña", timeout=8000)
    except Exception as e:
        print(f"No se requirió clic previo o no se encontró el texto: {e}")

    print("Rellenando credenciales...")
    # Buscamos directamente cualquier campo de entrada disponible en pantalla
    page.wait_for_selector("input", timeout=10000)
    
    # Escribimos usuario y contraseña en los inputs que encuentre
    inputs = page.locator("input")
    inputs.nth(0).fill(username)
    inputs.nth(1).fill(password)
    
    print("Enviando formulario...")
    # Hacemos clic en el botón de ingresar/enviar
    page.locator("button[type='submit'], button").last.click()

    print("Esperando redirección al inicio...")
    try:
        page.wait_for_url("**/inicio**", timeout=40000)
    except Exception as e:
        print(f"Aviso de espera: {e}")

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

                contenido_actualizado = re.sub(r'(tok_|eyJ0eXAiO)[a-zA-Z0-9_\-\.]+', f"{nuevo_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                modificados += 1
                print(f"Actualizado: {ruta_archivo}")

print(f"Proceso finalizado. Archivos modificados: {modificados}")
