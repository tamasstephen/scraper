"""Configuration management for the web scraper."""

import argparse
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScraperConfig:
    """Configuration for web scraper operations.

    Attributes:
        url: Base URL to scrape
        file_name: Output HTML file name
        output_dir: Directory to save output files
        sublinks: List of sublink filters
        sub_path: Starting path for scraping
        strict_url: Whether to enforce strict URL matching
        max_depth: Maximum depth for recursive scraping
        target_selector: CSS selector for data extraction
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """

    url: str
    file_name: str
    output_dir: str
    sublinks: list[str]
    sub_path: str
    strict_url: bool
    max_depth: int
    target_selector: Optional[str]
    log_level: str

    @classmethod
    def from_args(cls, args: argparse.Namespace) -> "ScraperConfig":
        """Create configuration from parsed command-line arguments.

        Args:
            args: Parsed arguments from argparse

        Returns:
            ScraperConfig instance
        """
        sublinks = [link.strip() for link in args.sublinks.split(",") if link.strip()]

        return cls(
            url=args.url,
            file_name=args.file_name,
            output_dir=args.output_dir,
            sublinks=sublinks,
            sub_path=args.sub_path,
            strict_url=args.strict_url,
            max_depth=args.max_depth,
            target_selector=args.target_selector,
            log_level=args.log_level,
        )

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.url:
            raise ValueError("URL is required")

        if not self.url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

        if self.max_depth < 1:
            raise ValueError("max_depth must be at least 1")

        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR"):
            raise ValueError(
                f"Invalid log_level: {self.log_level}. "
                "Must be DEBUG, INFO, WARNING, or ERROR"
            )


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description="Web scraper for extracting content from websites"
    )

    parser.add_argument("--url", type=str, required=True, help="Base URL to scrape")

    parser.add_argument(
        "--file_name",
        type=str,
        default="output.html",
        help="Output HTML file name (default: output.html)",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        default="output",
        help="Directory to save output files (default: output)",
    )

    parser.add_argument(
        "--sublinks",
        type=str,
        default="",
        help="Comma-separated list of sublink filters",
    )

    parser.add_argument(
        "--sub_path", type=str, default="", help="Starting path for scraping"
    )

    parser.add_argument(
        "--strict_url",
        type=bool,
        default=True,
        help="Enforce strict URL matching (default: True)",
    )

    parser.add_argument(
        "--max_depth",
        type=int,
        default=10,
        help="Maximum depth for recursive scraping (default: 10)",
    )

    parser.add_argument(
        "--target_selector",
        type=str,
        default=None,
        help="CSS selector for data extraction (optional)",
    )

    parser.add_argument(
        "--log_level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Set logging level (default: INFO)",
    )

    return parser.parse_args()
