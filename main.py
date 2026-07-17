import os
from scrapers.banco_provincia import BancoProvinciaScraper
from scrapers.banco_macro import BancoMacroScraper
from scrapers.generic import GenericScraper
from utils.display import display_promotions

# Mapa para agrupar los resultados legibles por banco/entidad en la terminal
ENTITY_DISPLAY_NAMES = {
    "banco_provincia": "Banco Provincia (Cuenta DNI)",
    "banco_nacion": "Banco Nación (BNA+)",
    "banco_macro": "Banco Macro",
    "banco_ciudad": "Banco Ciudad (BUEPP)",
    "modo": "MODO",
    "red_sube": "Red SUBE (Descuento por Combinaciones)",
    "tarifa_social": "Tarifa Social Federal",
    "boleto_estudiantil": "Boleto Estudiantil",
    "generico": "Otros Canales Oficiales"
}

def resolve_scraper(url: str):
    """
    Asocia la URL con el scraper correspondiente.
    """
    if "bancoprovincia.com.ar" in url:
        return BancoProvinciaScraper(url)
    elif "macro.com.ar" in url:
        return BancoMacroScraper(url)
    else:
        return GenericScraper(url)

def main():
    links_file = os.path.join("bancos", "links_scraper_transporte.txt")
    if not os.path.exists(links_file):
        print(f"Error: El archivo de enlaces {links_file} no existe.")
        return

    # Leer enlaces ignorando líneas vacías y comentarios
    urls = []
    with open(links_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)

    results_by_entity = {}

    print("Iniciando scraper de promociones de transporte...")
    print(f"Procesando {len(urls)} enlaces de origen...")

    for url in urls:
        scraper = resolve_scraper(url)
        # Obtenemos la clave de entidad (si es genérico, la determina por URL)
        if isinstance(scraper, GenericScraper):
            key = scraper._get_key()
        elif isinstance(scraper, BancoProvinciaScraper):
            key = "banco_provincia"
        elif isinstance(scraper, BancoMacroScraper):
            key = "banco_macro"
        else:
            key = "generico"

        display_name = ENTITY_DISPLAY_NAMES.get(key, "Otros")
        
        if display_name not in results_by_entity:
            results_by_entity[display_name] = []

        try:
            print(f"-> Analizando: {url} ...")
            promos = scraper.scrape()
            if promos:
                # Filtrar duplicados
                existing_titles = {p["titulo"] for p in results_by_entity[display_name]}
                for promo in promos:
                    if promo["titulo"] not in existing_titles:
                        results_by_entity[display_name].append(promo)
        except Exception as e:
            print(f"Error al procesar {url}: {e}")

    print("\nProceso finalizado. Mostrando reporte en pantalla:\n")
    display_promotions(results_by_entity)

if __name__ == "__main__":
    main()
