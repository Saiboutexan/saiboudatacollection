"""Scrapers Selenium du projet."""

from .books_scraper import scraper_livres
from .gaaraas_scraper import scraper_vehicules

__all__ = ["scraper_livres", "scraper_vehicules"]
