import re
from bs4 import BeautifulSoup
from scrapers.base import BaseScraper
from config import FALLBACK_PROMOTIONS

# Mapeo de subcadenas de URL a claves de promociones fallback
URL_MAP = {
    "bancoprovincia.com.ar": "banco_provincia",
    "bna.com.ar": "banco_nacion",
    "macro.com.ar": "banco_macro",
    "bancociudad.com.ar": "banco_ciudad",
    "modo.com.ar": "modo",
    "beneficios-vigentes-en-red-sube": "red_sube",
    "tarifa-social-federal-de-transporte": "tarifa_social",
    "boleto-estudiantil": "boleto_estudiantil",
    "gba.gob.ar/transporte/boleto": "boleto_estudiantil"
}

class GenericScraper(BaseScraper):
    def _get_key(self) -> str:
        """Determina la clave de fallback en base a la URL"""
        for pattern, key in URL_MAP.items():
            if pattern in self.url:
                return key
        return "generico"

    def scrape(self) -> list:
        key = self._get_key()
        promos = []

        try:
            # Intentamos obtener y buscar semánticamente en el texto
            html = self.fetch()
            soup = BeautifulSoup(html, "html.parser")
            
            # Limpiamos tags innecesarios
            for tag in soup(["script", "style", "nav", "footer", "header"]):
                tag.decompose()
                
            text = soup.get_text(separator=" ")
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            
            # Buscar coincidencias semánticas con SUBE / Transporte
            keywords = re.compile(r"(sube|transporte|colectivo|subte|pasajes|descuento|reintegro|boleto)", re.IGNORECASE)
            
            seen_sentences = set()
            for line in lines:
                sentences = re.split(r'[.!?•-]\s*', line)
                for sentence in sentences:
                    sentence = re.sub(r'\s+', ' ', sentence).strip()
                    if len(sentence) > 30 and keywords.search(sentence) and ("%" in sentence or "$" in sentence or "gratis" in sentence.lower() or "descuento" in sentence.lower()):
                        if sentence not in seen_sentences and len(seen_sentences) < 5:
                            seen_sentences.add(sentence)
                            
                            # Intentamos estructurar algo básico a partir de la línea
                            m_pct = re.search(r"(\d+%\s*(?:de)?\s*(?:ahorro|reintegro|descuento|devolución))", sentence, re.IGNORECASE)
                            pct = m_pct.group(1) if m_pct else "Descuento de Transporte"
                            
                            m_tope = re.search(r"(tope\s*(?:de\s*)?\$\s*[\d\.]+)", sentence, re.IGNORECASE)
                            tope = m_tope.group(1) if m_tope else "Consultar bases"

                            promos.append({
                                "titulo": f"Promo Detectada: {pct}",
                                "descripcion": sentence if len(sentence) <= 240 else sentence[:237] + "...",
                                "tope": tope,
                                "dias": "Consultar enlace",
                                "requisitos": "Verificar bases y condiciones oficiales",
                                "tipo": "Transporte / SUBE",
                                "enlace": self.url,
                                "fuente": "En Vivo (Web)"
                            })
            
            if promos:
                return promos
        except Exception:
            pass # Si falla, usamos el fallback directo

        # Fallback local para esta clave si existe
        fallback = FALLBACK_PROMOTIONS.get(key, {}).get("promociones", [])
        result = []
        for p in fallback:
            p_copy = p.copy()
            p_copy["fuente"] = "Local (Estable)"
            result.append(p_copy)
        
        return result
