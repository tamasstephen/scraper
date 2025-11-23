#!/usr/bin/env python3
"""Web scraper entry point."""

from src.config import parse_arguments, ScraperConfig
from src.scraper import WebScraper

def main():
    """Main entry point for the web scraper."""
    # Parse command-line arguments
    args = parse_arguments()

    # Create configuration
    config = ScraperConfig.from_args(args)

    # Validate configuration
    config.validate()

    # Create and run scraper
    scraper = WebScraper(config)
    scraper.run()

if __name__ == "__main__":
    main()
