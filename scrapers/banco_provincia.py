import re
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, register_scraper
from config import FALLBACK_PROMOTIONS

@register_scraper
class BancoProvinciaScraper(BaseScraper):
    @classmethod
    def matches(cls, url: str) -> bool:
        return "bancoprovincia.com.ar" in url
    def scrape(self) -> list:
        unique_promos = []
        try:
            html = self.fetch()
            soup = BeautifulSoup(html, "html.parser")
            
            promos = []
            # Buscamos elementos de texto que contengan palabras clave relacionadas a SUBE/transporte
            keywords = re.compile(r"(sube|transporte|colectivo|subte|pasajes|viajes|nfc)", re.IGNORECASE)
            
            # Encontrar todas las etiquetas que contengan estas palabras
            for tag in soup.find_all(["p", "span", "div", "h3", "h4", "a"]):
                # Omitir divs contenedores complejos para evitar bloques de texto concatenados
                if tag.name == "div" and tag.find_all(["p", "span", "div", "h3", "h4", "a"]):
                    continue
                
                text = tag.get_text(strip=True)
                # Evitar bloques de texto masivos que unan múltiples ofertas independientes
                if len(text) > 400:
                    continue
                    
                if keywords.search(text) and "%" in text:
                    # Intentar estructurar la promo detectada
                    reintegro_match = re.search(r"(\d+%\s*(?:de)?\s*(?:ahorro|reintegro|descuento|devolución))", text, re.IGNORECASE)
                    titulo = reintegro_match.group(1) if reintegro_match else "Descuento detectado"
                    
                    # Intentar buscar topes de reintegro en el texto
                    tope_match = re.search(r"(\$\s*\d+(?:\.\d+)?(?:\s*de\s*tope)?)", text, re.IGNORECASE)
                    tope = tope_match.group(1) if tope_match else "Consultar bases"

                    promos.append({
                        "titulo": f"Cuenta DNI - {titulo}",
                        "descripcion": text,
                        "tope": tope,
                        "dias": "Todos los días" if "todos" in text.lower() else "Consultar bases",
                        "requisitos": "Uso de la app Cuenta DNI / NFC",
                        "tipo": "Colectivos / Subtes",
                        "enlace": self.url,
                        "fuente": "En Vivo (Web)"
                    })
            
            # Limpiar duplicados si se detectaron varios nodos similares
            unique_promos = []
            seen_titles = set()
            for promo in promos:
                if promo["titulo"] not in seen_titles:
                    seen_titles.add(promo["titulo"])
                    unique_promos.append(promo)
                    
            if unique_promos:
                return unique_promos
        except Exception:
            pass
        
        # Fallback local
        fallback = FALLBACK_PROMOTIONS.get("banco_provincia", {}).get("promociones", [])
        for p in fallback:
            # Hacemos una copia para no alterar el diccionario original de config
            p_copy = p.copy()
            p_copy["fuente"] = "Local (Estable)"
            unique_promos.append(p_copy)
        return unique_promos
