import os
import re
from playwright.sync_api import sync_playwright

BASE_DIR = os.path.dirname(os.path.abspath(__file__))import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("--- ACTUALIZADOR DE FLOW (MODO MANUAL SEGURO) ---")
print("1. Entra a Flow en tu navegador habitual (donde te carga bien).")
print("2. Copia el token de tu sesión (o un enlace entero que tenga el token nuevo).")
print("-" * 50)

entrada_usuario = input("Pega aquí el token (o el enlace completo) y presiona ENTER: ").strip()

if not entrada_usuario:
    print("No ingresaste nada. Saliendo...")
    exit(1)

# Si pegaste una URL completa, extraemos automáticamente la parte del token
if "tok_" in entrada_usuario:
    match_token = re.search(r'(tok_[^/\s]+)', entrada_usuario)
    if match_token:
        token_nuevo = match_token.group(1)
    else:
        token_nuevo = entrada_usuario
else:
    # Si pegaste solo el JWT puro (ej: eyJhbGci...), le agregamos el tok_ adelante
    if not entrada_usuario.startswith("tok_"):
        token_nuevo = f"tok_{entrada_usuario}"
    else:
        token_nuevo = entrada_usuario

print(f"\nToken procesado correctamente.")
print(f"Escaneando archivos M3U/TXT en: {BASE_DIR}")

modificados = 0

for root, dirs, files in os.walk(BASE_DIR):
    if "flow_profile" in root:
        continue
        
    for file in files:
        if file.endswith((".m3u", ".m3u8", ".txt")):
            ruta_archivo = os.path.join(root, file)
            
            with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read()

            # Reemplazamos el bloque viejo por el nuevo token manteniendo la ruta /live/
            patron = r'tok_.*?(/live/)'
            contenido_actualizado, count = re.subn(patron, f'{token_nuevo}\\1', contenido)

            if count > 0:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                modificados += 1
                print(f"-> ¡Actualizado con éxito: {file} ({count} enlaces modificados)!")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
USER_DATA_DIR = os.path.join(BASE_DIR, "flow_profile")

print("--- ACTUALIZADOR DE FLOW (BÚSQUEDA TOTAL) ---")

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

    print("\nBuscando el token en la cookie 'flow_idToken'...")
    token_jwt = None
    
    for cookie in context.cookies():
        if cookie['name'] == 'flow_idToken':
            token_jwt = cookie['value']
            break

    context.close()

if not token_jwt:
    print("\nNo se encontró la cookie 'flow_idToken'. Asegúrate de haber iniciado sesión.")
    exit(1)

token_nuevo = f"tok_{token_jwt}"

print(f"\n¡Token listo! Escaneando todas las carpetas en: {BASE_DIR}")
modificados = 0

# Recorremos todas las subcarpetas y archivos desde la raíz
for root, dirs, files in os.walk(BASE_DIR):
    # Ignoramos la carpeta de perfil de Chrome
    if "flow_profile" in root:
        continue
        
    for file in files:
        if file.endswith((".m3u", ".m3u8", ".txt")):
            ruta_archivo = os.path.join(root, file)
            
            with open(ruta_archivo, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read()

            patron = r'tok_.*?(/live/)'
            contenido_actualizado, count = re.subn(patron, f'{token_nuevo}\\1', contenido)

            if count > 0:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                modificados += 1
                print(f"-> ¡Actualizado con éxito: {file} (Ruta: {root}) -> ({count} enlaces modificados)!")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
