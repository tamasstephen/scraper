"""Main web scraper orchestration."""

import logging
from src.config import ScraperConfig
from src.fetcher import URLFetcher
from src.parser import HTMLParser
from src.file_handler import FileHandler
from src.link_manager import LinkManager


class WebScraper:
    """Main web scraper that orchestrates all components.

    Coordinates fetching, parsing, link management, and file operations
    to scrape websites recursively.
    """

    def __init__(self, config: ScraperConfig):
        """Initialize the web scraper with configuration.

        Args:
            config: Scraper configuration
        """
        self.config = config
        self.logger = self._setup_logging()

        # Initialize components
        self.fetcher = URLFetcher(self.logger)
        self.parser = HTMLParser(self.logger)
        self.file_handler = FileHandler(config.file_name, self.logger)
        self.link_manager = LinkManager(config.sublinks, config.url, self.logger)

        self.depth = 0
        self.total_processed = 0

    def _setup_logging(self) -> logging.Logger:
        """Configure logging based on config.

        Returns:
            Configured logger instance
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
        }

        logging.basicConfig(
            level=level_map.get(self.config.log_level, logging.INFO),
            format="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%H:%M:%S",
        )

        return logging.getLogger(__name__)

    def run(self) -> None:
        """Run the web scraper.

        Main entry point that starts the scraping process.
        """
        self.logger.info("Starting web scraper")
        self.logger.info(
            f"Configuration: URL={self.config.url}, "
            f"File={self.config.file_name}, "
            f"Max depth={self.config.max_depth}"
        )
        self.logger.info(f"Sublinks filter: {self.config.sublinks}")
        self.logger.info(f"Starting path: {self.config.sub_path}")
        self.logger.info(f"Target selector: {self.config.target_selector}")

        # Initialize data file if selector is provided
        if self.config.target_selector:
            self.file_handler.initialize_data_file(self.config.target_selector)

        # Add initial path to queue
        self.link_manager.add_links([self.config.sub_path])
        self.logger.info(f"Initial queue size: {len(self.link_manager.queue)}")

        # Main scraping loop
        while self.link_manager.has_links():
            if self.depth >= self.config.max_depth:
                self.logger.info(
                    f"Reached maximum depth ({self.config.max_depth}), stopping"
                )
                break

            next_path = self.link_manager.get_next()
            if not next_path:
                break

            self.logger.debug(f"Next path to process: {next_path}")

            # Filter external domains
            if not self.link_manager.filter_domain(next_path):
                self.logger.info(f"Skipping external domain: {next_path}")
                continue

            # Build full URL
            next_url = self.link_manager.build_full_url(next_path)
            self.logger.info(
                f"Processing URL {self.depth + 1}/{self.config.max_depth + 1}: "
                f"{next_url}"
            )

            # Process the URL
            try:
                self.process_url(next_url)
                self.depth += 1
                self.total_processed += 1

                # Progress update
                if self.total_processed % 5 == 0 or self.depth == 1:
                    self.logger.info(
                        f"Progress: {self.total_processed} URLs processed, "
                        f"queue={len(self.link_manager.queue)}, "
                        f"visited={len(self.link_manager.visited)}"
                    )

            except Exception as e:
                self.logger.error(f"Failed to process {next_url}: {str(e)}")
                continue

        # Convert to markdown
        self.logger.info("Converting HTML to Markdown")
        try:
            self.file_handler.convert_to_markdown()
        except Exception as e:
            self.logger.error(f"Failed to convert to markdown: {str(e)}")

        self.logger.info(
            f"Scraping complete. Processed {len(self.link_manager.visited)} URLs, "
            f"final queue size: {len(self.link_manager.queue)}"
        )

    def process_url(self, url: str) -> None:
        """Process a single URL.

        Fetches HTML, writes to file, extracts links, and optionally
        extracts data based on target selector.

        Args:
            url: URL to process
        """
        self.logger.info(f"Processing URL: {url}")

        # Fetch HTML content
        html_content = self.fetcher.fetch(url)

        # ALWAYS write to HTML file
        self.file_handler.write_html(html_content)

        # Parse HTML
        soup = self.parser.parse_html(html_content)

        # Extract and add links
        links = self.parser.extract_links(soup)
        self.logger.info(f"Found {len(links)} links on page")
        self.link_manager.add_links(links)

        # Extract data if selector is provided
        if self.config.target_selector:
            data = self.parser.extract_by_selector(soup, self.config.target_selector)

            if data and data.strip():
                self.file_handler.write_extracted_data(
                    self.config.target_selector, url, data
                )
            else:
                self.logger.warning(
                    f"No data found for selector: {self.config.target_selector} "
                    f"on {url}"
                )

                # Try body as fallback
                data = self.parser.extract_by_selector(soup, "body")
                if data and data.strip():
                    self.file_handler.write_extracted_data(
                        self.config.target_selector, url, data
                    )
                else:
                    self.logger.warning(f"No data found in body either for {url}")
