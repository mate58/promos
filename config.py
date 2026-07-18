import os
import json

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    "Connection": "keep-alive"
}

# Carga dinámica de promociones fallback desde JSON
FALLBACK_PROMOTIONS = {}
fallback_path = os.path.join(os.path.dirname(__file__), "bancos", "fallbacks.json")

try:
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            FALLBACK_PROMOTIONS = json.load(f)
    else:
        # Fallback al directorio de trabajo actual por si se ejecuta en otra estructura
        fallback_path_alt = os.path.join("bancos", "fallbacks.json")
        if os.path.exists(fallback_path_alt):
            with open(fallback_path_alt, "r", encoding="utf-8") as f:
                FALLBACK_PROMOTIONS = json.load(f)
except Exception as e:
    # Registra advertencia si el archivo no puede leerse, permitiendo continuar
    import sys
    print(f"Advertencia: No se pudo cargar fallbacks.json ({e}).", file=sys.stderr)
