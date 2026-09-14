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
    browser = p.chromium.launch(headless=False, slow_mo=1000)
    context = browser.new_context()
    page = context.new_page()

    print("Entrando al portal de Flow...")
    page.goto("https://portal.app.flow.com.ar/prelogin", wait_until="networkidle")

    print("Buscando enlace de usuario y contraseña...")
    try:
        page.click("text=Ingresar con usuario y contraseña", timeout=5000)
    except Exception as e:
        print(f"Aviso: {e}")

    print("Esperando campo de texto e ingresando usuario...")
    page.wait_for_selector("input", timeout=10000)
    
    # Escribir usuario en el primer campo
    input_usuario = page.locator("input").first
    input_usuario.fill(username)
    
    print("Avanzando al siguiente paso (presionando Enter y buscando botón)...")
    # Presionamos Enter sobre el input del usuario para disparar la transición
    input_usuario.press("Enter")
    
    # Opcional: intentamos hacer clic en cualquier botón visible que diga Continuar, Siguiente o similar
    try:
        page.locator("button:has-text('Continuar'), button:has-text('Siguiente'), button:has-text('Ingresar'), button[type='submit']").first.click(timeout=3000)
    except:
        pass

    print("Esperando campo de contraseña...")
    # Damos un respiro y esperamos que aparezca el input de contraseña
    page.wait_for_selector("input[type='password']", timeout=12000)
    page.locator("input[type='password']").first.fill(password)
    
    print("Enviando formulario de acceso...")
    try:
        page.locator("button[type='submit'], button:has-text('Ingresar'), button:has-text('Iniciar sesión')").last.click()
    except:
        page.keyboard.press("Enter")

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
