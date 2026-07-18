import re
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper, register_scraper
from config import FALLBACK_PROMOTIONS

@register_scraper
class BancoMacroScraper(BaseScraper):
    @classmethod
    def matches(cls, url: str) -> bool:
        return "macro.com.ar" in url
    def scrape(self) -> list:
        promos = []
        try:
            html = self.fetch()
            soup = BeautifulSoup(html, "html.parser")
            
            # Buscamos nodos que contengan texto como "Colectivos y subtes" o "Colectivos y Subtes"
            text_nodes = soup.find_all(string=re.compile(r"Colectivos\s+y\s+subtes", re.IGNORECASE))
            
            for node in text_nodes:
                parent = node.find_parent()
                if not parent:
                    continue
                
                title = parent.get_text(strip=True)
                # Normalizamos título
                title = re.sub(r'\s+', ' ', title)
                
                # Buscamos el texto descriptivo/legal asociado que suele ser un hermano o estar cerca
                desc = ""
                # Heurística: buscar en hermanos siguientes
                sibling = parent.find_next_sibling()
                if sibling:
                    desc = sibling.get_text(strip=True)
                
                # Si no se encuentra en el hermano inmediato, buscamos en el contenedor padre
                if not desc or len(desc) < 30:
                    sibling_parent = parent.parent.find_next_sibling()
                    if sibling_parent:
                        desc = sibling_parent.get_text(strip=True)
                
                # Si aún está vacío, subimos otro nivel o usamos el texto del padre
                if not desc:
                    desc = parent.parent.get_text(strip=True)
                
                desc = re.sub(r'\s+', ' ', desc)
                
                # Validamos si es una promoción relevante (por ejemplo, contiene porcentaje o pesos)
                if "%" in desc or "$" in desc or "reintegro" in desc.lower():
                    m_pct = re.search(r"(\d+%\s*(?:de)?\s*(?:ahorro|reintegro|descuento|devolución))", desc, re.IGNORECASE)
                    pct = m_pct.group(1) if m_pct else "Ahorro / Reintegro"
                    
                    m_tope = re.search(r"(tope\s*(?:de\s*(?:reintegro\s*de\s*)?)?\$\s*[\d\.]+)", desc, re.IGNORECASE)
                    tope = m_tope.group(1) if m_tope else "$10.000 mensual"
                    
                    # Limpiamos texto legal de excesos
                    display_title = title if "|" in title else f"{title} | {pct}"
                    
                    promos.append({
                        "titulo": f"Banco Macro - {display_title}",
                        "descripcion": desc,
                        "tope": tope,
                        "dias": "Todos los días",
                        "requisitos": "Pagar mediante la app Macro / MODO QR o tarjetas de Débito NFC.",
                        "tipo": "Colectivos / Subtes",
                        "enlace": self.url,
                        "fuente": "En Vivo (Web)"
                    })
                    
            if promos:
                return promos
        except Exception:
            pass
            
        # Fallback local
        fallback = FALLBACK_PROMOTIONS.get("banco_macro", {}).get("promociones", [])
        result = []
        for p in fallback:
            p_copy = p.copy()
            p_copy["fuente"] = "Local (Estable)"
            result.append(p_copy)
        return result
