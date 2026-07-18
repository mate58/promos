from scrapers.base import BaseScraper, SCRAPER_REGISTRY, register_scraper
from scrapers.banco_provincia import BancoProvinciaScraper
from scrapers.banco_macro import BancoMacroScraper
from scrapers.generic import GenericScraper

__all__ = [
    "BaseScraper",
    "SCRAPER_REGISTRY",
    "register_scraper",
    "BancoProvinciaScraper",
    "BancoMacroScraper",
    "GenericScraper"
]
