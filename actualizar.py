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

    # Volcamos Session Storage
    session_data = page.evaluate("() => { let d = {}; for(let i=0; i<sessionStorage.length; i++){ let k=sessionStorage.key(i); d[k]=sessionStorage.getItem(k); } return d; }")
    print("--- SESSION STORAGE ---")
    print(session_data)

    # Volcamos Cookies
    cookies = context.cookies()
    print("--- COOKIES ---")
    for c in cookies:
        if len(c['value']) > 20:
            print(f"Cookie: {c['name']} --> {c['value'][:50]}...")

    print("-------------------------------------------")
    
    # Pausa para que el navegador no se cierre solo y puedas ver todo
    input("Presiona ENTER en esta ventana negra de la terminal cuando quieras cerrar el navegador...")
    context.close()
