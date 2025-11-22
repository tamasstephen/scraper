"""HTTP fetching operations using pycurl."""

import logging
import pycurl
import certifi
from io import BytesIO


class URLFetcher:
    """Handles HTTP requests using pycurl.

    Manages fetching URLs with proper certificate verification.
    """

    def __init__(self, logger: logging.Logger):
        """Initialize the URL fetcher.

        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger

    def fetch(self, url: str) -> bytes:
        """Fetch content from a URL.

        Args:
            url: URL to fetch

        Returns:
            Raw bytes content from the URL

        Raises:
            Exception: If fetching fails
        """
        self.logger.info(f"Fetching URL: {url}")

        buffer = BytesIO()

        try:
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, url)
            curl.setopt(pycurl.CAINFO, certifi.where())
            curl.setopt(pycurl.WRITEDATA, buffer)
            curl.perform()
            curl.close()

            content = buffer.getvalue()
            self.logger.debug(f"Successfully fetched {len(content)} bytes from {url}")
            return content

        except Exception as e:
            self.logger.error(f"Failed to fetch URL {url}: {str(e)}")
            raise
        finally:
            buffer.close()
