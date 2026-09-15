import os
import re
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_DATA_DIR = os.path.join(BASE_DIR, "flow_profile")
CARPETA_NICO = os.path.join(BASE_DIR, "nico")

print("--- DIAGNÓSTICO DE COOKIES FLOW ---")

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=USER_DATA_DIR,
        channel="chrome",
        headless=False,
        args=["--start-maximized", "--disable-blink-features=AutomationControlled"]
    )
    
    page = context.new_page()

    try:
        page.goto("https://portal.app.flow.com.ar/inicio", wait_until="domcontentloaded", timeout=60000)
    except Exception as e:
        print(f"Aviso en carga: {e}")

    print("\n" + "="*50)
    print(" Inicia sesión en la ventana de Flow.")
    print(" Cuando ya estés viendo la tele, ven aquí y presiona ENTER.")
    print("="*50 + "\n")
    
    input("Presiona ENTER en la terminal cuando estés logueado...")

    print("\nBuscando cookies disponibles...")
    todas_las_cookies = context.cookies()
    
    encontrado_token = None

    for cookie in todas_las_cookies:
        nombre = cookie['name']
        valor = cookie['value']
        # Imprimimos todas las cookies largas para encontrarlas rápido
        if len(valor) > 20:
            print(f"-> Cookie encontrada: [{nombre}] (Largo: {len(valor)})")
        
        # Buscamos coincidencias amplias
        if any(k in nombre.lower() for k in ['token', 'auth', 'session', 'jwt', 'id']):
            if len(valor) > 20:
                encontrado_token = valor

    context.close()

if not encontrado_token:
    print("\nNo se pudo identificar un token largo en las cookies.")
    print("Por favor, mira en la lista de arriba cuál fue la cookie que apareció cuando estabas logueado.")
    exit(1)

print(f"\n¡Token detectado con éxito: {encontrado_token[:30]}...!")
print(f"Buscando carpeta 'nico' en: {CARPETA_NICO}")

modificados = 0

if os.path.exists(CARPETA_NICO):
    for root, dirs, files in os.walk(CARPETA_NICO):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                
                with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                    contenido = f.read()

                contenido_actualizado, count = re.subn(r'tok_[^/]+', f'tok_{encontrado_token}', contenido)

                if count > 0:
                    with open(ruta_archivo, "w", encoding="utf-8") as f:
                        f.write(contenido_actualizado)
                    modificados += 1
                    print(f"-> ¡Actualizado con éxito: {file} ({count} cambios)!")
                else:
                    print(f"-> El archivo {file} no tenía la estructura 'tok_' para actualizar.")
else:
    print(f"¡Error! No se encontró la carpeta 'nico' en la ruta: {CARPETA_NICO}")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
