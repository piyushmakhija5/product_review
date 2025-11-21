"""
Base scraper class with common functionality for all retailer scrapers.
"""
import requests
from bs4 import BeautifulSoup
from config import Config
from models.product import Product
from models.requirements import UserRequirements
from typing import List, Optional
import time
import re
import hashlib


class BaseScraper:
    """Base class for all retailer scrapers."""

    def __init__(self, retailer_name: str):
        """
        Initialize scraper.

        Args:
            retailer_name: Name of the retailer (e.g., 'amazon', 'walmart')
        """
        self.retailer_name = retailer_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': Config.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def get(self, url: str, retries: int = None) -> requests.Response:
        """
        Perform GET request with retry logic.

        Args:
            url: URL to fetch
            retries: Number of retries. Defaults to Config.MAX_RETRIES

        Returns:
            Response object

        Raises:
            requests.RequestException: If all retries fail
        """
        retries = retries or Config.MAX_RETRIES

        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=Config.SCRAPING_TIMEOUT)
                response.raise_for_status()

                # Respectful delay
                if attempt < retries - 1:  # Don't delay after last attempt
                    time.sleep(Config.REQUEST_DELAY)

                return response

            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise
                # Exponential backoff
                time.sleep(2 ** attempt)

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content.

        Args:
            html: HTML string

        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')

    def search(self, requirements: UserRequirements) -> List[Product]:
        """
        Search for products based on requirements.
        Must be implemented by subclasses.

        Args:
            requirements: User requirements

        Returns:
            List of Product objects
        """
        raise NotImplementedError("Subclasses must implement search()")

    def build_search_query(self, requirements: UserRequirements) -> str:
        """
        Build search query string from requirements.

        Args:
            requirements: User requirements

        Returns:
            Search query string
        """
        parts = [requirements.product_category]

        # Add key specs to search
        for key, value in list(requirements.must_have_specs.items())[:3]:
            if isinstance(value, (str, int, float)):
                parts.append(str(value))

        return " ".join(parts)

    def extract_price(self, price_text: str) -> Optional[float]:
        """
        Extract numeric price from text.

        Args:
            price_text: Text containing price

        Returns:
            Price as float or None if not found
        """
        if not price_text:
            return None

        # Remove currency symbols and commas
        cleaned = re.sub(r'[,$]', '', price_text)

        # Extract first number
        match = re.search(r'(\d+\.?\d*)', cleaned)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None

        return None

    def extract_rating(self, rating_text: str) -> Optional[float]:
        """
        Extract numeric rating from text.

        Args:
            rating_text: Text containing rating

        Returns:
            Rating as float (0-5) or None
        """
        if not rating_text:
            return None

        # Extract number
        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            try:
                rating = float(match.group(1))
                # Clamp to 0-5 range
                return max(0.0, min(5.0, rating))
            except ValueError:
                return None

        return None

    def generate_product_id(self, name: str, retailer: str = None) -> str:
        """
        Generate a unique product ID.

        Args:
            name: Product name
            retailer: Retailer name

        Returns:
            Unique ID string
        """
        retailer = retailer or self.retailer_name
        text = f"{retailer}:{name}".lower()
        return hashlib.md5(text.encode()).hexdigest()[:16]

    def extract_brand(self, product_name: str) -> str:
        """
        Extract brand name from product name.
        Simple implementation - usually first word.

        Args:
            product_name: Full product name

        Returns:
            Extracted brand name
        """
        if not product_name:
            return ""

        # Common brand patterns
        parts = product_name.split()
        if parts:
            return parts[0]

        return ""

    def clean_text(self, text: str) -> str:
        """
        Clean extracted text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        if not text:
            return ""

        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()

        return text

    def is_within_budget(self, price: float, requirements: UserRequirements) -> bool:
        """
        Check if price is within budget.

        Args:
            price: Product price
            requirements: User requirements

        Returns:
            True if within budget
        """
        if not requirements.budget:
            return True

        max_price = requirements.budget.get_effective_max()

        if requirements.budget.min:
            return requirements.budget.min <= price <= max_price

        return price <= max_price

    def log_scrape_error(self, error: Exception, context: str = ""):
        """Log scraping error if debug is enabled."""
        if Config.DEBUG:
            print(f"[{self.retailer_name}] Scrape error {context}: {error}")
