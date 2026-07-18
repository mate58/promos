import requests
from abc import ABC, abstractmethod
from config import DEFAULT_HEADERS

# Registro global de scrapers
SCRAPER_REGISTRY = []

def register_scraper(cls):
    """Decorador para registrar automáticamente un scraper en el sistema."""
    if cls not in SCRAPER_REGISTRY:
        SCRAPER_REGISTRY.append(cls)
    return cls

class BaseScraper(ABC):
    def __init__(self, url: str, headers: dict = None):
        self.url = url
        self.headers = headers or DEFAULT_HEADERS

    def fetch(self) -> str:
        """
        Realiza la petición HTTP GET y retorna el HTML como texto.
        Si falla, levanta una excepción.
        """
        try:
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise RuntimeError(f"Error al realizar la petición a {self.url}: {str(e)}")

    @classmethod
    def matches(cls, url: str) -> bool:
        """
        Retorna True si este scraper es adecuado para procesar la URL.
        Debe ser implementado por las subclases.
        """
        return False

    @abstractmethod
    def scrape(self) -> list:
        """
        Método abstracto a implementar por cada scraper específico.
        Debe retornar una lista de diccionarios con la estructura de las promociones.
        """
        pass
