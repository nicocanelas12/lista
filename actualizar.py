import os
import re
import requests

# 1. Obtener credenciales desde las variables de entorno o Secrets
USERNAME = os.environ.get("FLOW_USER")
PASSWORD = os.environ.get("FLOW_PASS")

if not USERNAME or not PASSWORD:
    raise ValueError("Faltan las credenciales FLOW_USER o FLOW_PASS en el entorno.")

# 2. Autenticación en la API de Flow para obtener el token
login_url = "https://portal.app.flow.com.ar/api/oauth/v2/token"  # (Ajusta si tu endpoint difiere, o usa tu lógica habitual)
# Si usas tu método actual de login, colócalo aquí. Lo importante es extraer el token JWT nuevo:
# Ejemplo genérico de petición:
payload = {"username": USERNAME, "password": PASSWORD, "grant_type": "password"}
# (Si tu script anterior usaba otro método, dime y lo adaptamos exacto).

# Simulamos la obtención del token nuevo (reemplaza esto con tu request real si varía):
print("Conectando a Flow...")
# response = requests.post(login_url, data=payload)
# nuevo_token = response.json().get("access_token")

# Como referencia, aquí usamos la variable donde guardas el token obtenido:
# nuevo_token = "tok_AQUÍ_EL_NUEVO_TOKEN_DEVUELTO_POR_LA_API"

# 3. Buscar y reemplazar el token en los archivos dentro de la carpeta 'nico'
carpeta_nico = "nico"

if os.path.exists(carpeta_nico):
    for root, dirs, files in os.walk(carpeta_nico):
        for file in files:
            if file.endswith((".m3u", ".m3u8", ".txt")):
                ruta_archivo = os.path.join(root, file)
                with open(ruta_archivo, "r", encoding="utf-8") as f:
                    contenido = f.read()

                # Reemplazar cualquier token anterior (tok_...) por el nuevo token
                # Patrón que busca tok_ seguido de caracteres alfanuméricos/puntuación hasta el siguiente espacio o comilla
                contenido_actualizado = re.sub(r'tok_[a-zA-Z0-9_\-\.]+', f"tok_{nuevo_token}", contenido)

                with open(ruta_archivo, "w", encoding="utf-8") as f:
                    f.write(contenido_actualizado)
                
                print(f"Token actualizado en: {ruta_archivo}")
else:
    print("No se encontró la carpeta 'nico'.")
