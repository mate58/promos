import os
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from scrapers import SCRAPER_REGISTRY, GenericScraper, BancoProvinciaScraper, BancoMacroScraper
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
    Asocia la URL con el scraper correspondiente buscando en el registro dinámico.
    """
    for scraper_cls in SCRAPER_REGISTRY:
        if scraper_cls.matches(url):
            return scraper_cls(url)
    return GenericScraper(url)

def scrape_url(url: str, live_only: bool = False) -> tuple:
    """
    Función auxiliar para ejecutar el scraper en un hilo de ejecución separado.
    """
    scraper = resolve_scraper(url)
    
    # Determinar la clave de la entidad
    if isinstance(scraper, GenericScraper):
        key = scraper._get_key()
    elif isinstance(scraper, BancoProvinciaScraper):
        key = "banco_provincia"
    elif isinstance(scraper, BancoMacroScraper):
        key = "banco_macro"
    else:
        key = "generico"

    try:
        promos = scraper.scrape()
        if promos:
            if live_only:
                # Filtrar solo promociones obtenidas en vivo de la web
                promos = [p for p in promos if p.get("fuente") == "En Vivo (Web)"]
            return key, promos
    except Exception as e:
        # Se retorna una lista vacía y el error será procesado en el hilo principal
        raise e
        
    return key, []

def main():
    parser = argparse.ArgumentParser(description="Scraper concurrente y modular de promociones de transporte (CABA/AMBA).")
    parser.add_argument("--live-only", action="store_true", help="Mostrar únicamente promociones obtenidas de la web (omitir fallbacks locales).")
    parser.add_argument("--verbose", action="store_true", help="Mostrar descripciones y requisitos completos sin truncar en la tabla.")
    parser.add_argument("--entity", type=str, help="Filtrar reporte por nombre o identificador de entidad (ej: 'macro', 'provincia', 'sube').")
    parser.add_argument("--output", "-o", type=str, help="Exportar resultados limpios a un archivo JSON en la ruta indicada.")
    args = parser.parse_args()

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

    from rich.console import Console
    console = Console()

    print("Iniciando scraper de promociones de transporte...")
    print(f"Procesando {len(urls)} enlaces de origen concurrentemente...")

    # Ejecutar scraping concurrente usando ThreadPoolExecutor bajo un spinner de estado de Rich
    with console.status("[bold green]Procesando sitios oficiales...", spinner="dots") as status:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {executor.submit(scrape_url, url, args.live_only): url for url in urls}
            
            for future in as_completed(futures):
                url = futures[future]
                status.update(f"[bold green]Completado: {url}...")
                try:
                    key, promos = future.result()
                    if promos:
                        display_name = ENTITY_DISPLAY_NAMES.get(key, "Otros")
                        
                        # Aplicar filtro por entidad en caso de ser especificado
                        if args.entity:
                            search_term = args.entity.lower()
                            if search_term not in key.lower() and search_term not in display_name.lower():
                                continue
                        
                        if display_name not in results_by_entity:
                            results_by_entity[display_name] = []
                            
                        # Filtrar duplicados por título
                        existing_titles = {p["titulo"] for p in results_by_entity[display_name]}
                        for promo in promos:
                            if promo["titulo"] not in existing_titles:
                                results_by_entity[display_name].append(promo)
                except Exception as e:
                    console.log(f"[bold red]Error al procesar {url}:[/bold red] {e}")

    # Exportar resultados si se especificó --output
    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results_by_entity, f, indent=2, ensure_ascii=False)
            print(f"\nResultados exportados correctamente a: {args.output}")
        except Exception as e:
            print(f"Error al guardar los resultados en {args.output}: {e}")

    print("\nProceso finalizado. Mostrando reporte en pantalla:\n")
    display_promotions(results_by_entity, verbose=args.verbose)

if __name__ == "__main__":
    main()
