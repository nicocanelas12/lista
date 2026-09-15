import os
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

            patron = r'tok_.*?(/live/)'
            contenido_actualizado, count = re.subn(patron, f'{token_nuevo}\\1', contenido)

            if count > 0:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                modificados += 1
                print(f"-> ¡Actualizado con éxito: {file} ({count} enlaces modificados)!")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
