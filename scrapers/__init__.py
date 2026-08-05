"""Scrapers Selenium du projet (aucun usage de BeautifulSoup)."""

from .books_scraper import scraper_livres
from .gaaraas_scraper import scraper_vehicules

__all__ = ["scraper_livres", "scraper_vehicules"]
