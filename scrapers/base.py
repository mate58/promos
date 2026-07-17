import requests
from abc import ABC, abstractmethod
from config import DEFAULT_HEADERS

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

    @abstractmethod
    def scrape(self) -> list:
        """
        Método abstracto a implementar por cada scraper específico.
        Debe retornar una lista de diccionarios con la estructura de las promociones.
        """
        pass
