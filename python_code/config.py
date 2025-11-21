"""
Configuration management for the product review agent.
Loads environment variables from .env file using python-dotenv.
"""
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Project paths
    BASE_DIR = Path(__file__).parent
    CACHE_DIR = BASE_DIR / "cache"
    REPORTS_DIR = BASE_DIR / "reports"
    PROMPTS_DIR = BASE_DIR / "prompts"

    # LLM Configuration
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'claude').lower()
    LLM_MODEL = os.getenv('LLM_MODEL', 'claude-sonnet-4.5-20250929')

    # Search API Configuration
    SEARCH_PROVIDER = os.getenv('SEARCH_PROVIDER', 'serpapi').lower()
    SERPAPI_API_KEY = os.getenv('SERPAPI_API_KEY')
    PERPLEXITY_API_KEY = os.getenv('PERPLEXITY_API_KEY')

    # Web Scraping Configuration
    USER_AGENT = os.getenv(
        'USER_AGENT',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.5'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    SCRAPING_TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '10'))

    # Application Settings
    DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'true').lower() == 'true'
    CACHE_TTL_HOURS = int(os.getenv('CACHE_TTL_HOURS', '4'))
    MAX_PRODUCTS_PER_RETAILER = int(os.getenv('MAX_PRODUCTS_PER_RETAILER', '10'))

    # Report Settings
    SAVE_REPORTS = os.getenv('SAVE_REPORTS', 'true').lower() == 'true'

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        errors = []

        # Check LLM configuration
        if cls.LLM_PROVIDER == 'claude' and not cls.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required when LLM_PROVIDER is 'claude'")

        if cls.LLM_PROVIDER == 'gemini' and not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is required when LLM_PROVIDER is 'gemini'")

        if cls.LLM_PROVIDER not in ['claude', 'gemini']:
            errors.append(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'claude' or 'gemini'")

        # Check Search API configuration
        if cls.SEARCH_PROVIDER == 'serpapi' and not cls.SERPAPI_API_KEY:
            errors.append(
                "SERPAPI_API_KEY is required when SEARCH_PROVIDER is 'serpapi'\n"
                "  Get a free API key at: https://serpapi.com/manage-api-key"
            )

        if cls.SEARCH_PROVIDER == 'perplexity' and not cls.PERPLEXITY_API_KEY:
            errors.append(
                "PERPLEXITY_API_KEY is required when SEARCH_PROVIDER is 'perplexity'\n"
                "  Get an API key at: https://www.perplexity.ai/settings/api"
            )

        if cls.SEARCH_PROVIDER not in ['serpapi', 'perplexity']:
            errors.append(
                f"Invalid SEARCH_PROVIDER: {cls.SEARCH_PROVIDER}. Must be 'serpapi' or 'perplexity'"
            )

        if errors:
            raise ValueError("Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    @classmethod
    def setup_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.CACHE_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)
        cls.PROMPTS_DIR.mkdir(exist_ok=True)


# Validate configuration on import
Config.validate()
Config.setup_directories()
