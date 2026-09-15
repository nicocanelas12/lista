import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

print("--- ACTUALIZADOR DE FLOW (REEMPLAZO DIRECTO DE URL) ---")
print("1. Copia la URL completa de un canal que te funcione en Flow.")
print("-" * 50)

url_nueva = input("Pega aquí la URL completa y presiona ENTER: ").strip()

if not url_nueva or "/live/" not in url_nueva:
    print("La URL ingresada no es válida o no contiene '/live/'. Saliendo...")
    exit(1)

# Extraemos la base completa hasta antes de /live/
# Ejemplo: https://edge-mix02-mun.cvattv.com.ar/tok_...
base_nueva_limpia = url_nueva.split("/live/")[0]

print(f"\nNueva base de token detectada correctamente.")
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

            # Reemplazamos cualquier dominio + tok_... antiguo que esté antes de /live/
            # por nuestro nuevo dominio + token fresco completo.
            patron = r'https://[^\s"<>]+?/live/'
            
            contenido_actualizado, count = re.subn(patron, f'{base_nueva_limpia}/live/', contenido)

            if count > 0:
                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                modificados += 1
                print(f"-> ¡Actualizado con éxito: {file} ({count} enlaces modificados)!")

print(f"\n¡Proceso finalizado! Archivos modificados: {modificados}")
