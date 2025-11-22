"""Link filtering and queue management."""

import re
import logging
from typing import Optional


class LinkManager:
    """Manages link queue and filtering for the scraper.

    Handles filtering links based on sublink patterns and domain restrictions,
    and maintains a queue of URLs to visit and a set of visited URLs.
    """

    def __init__(self, sublinks: list[str], base_url: str, logger: logging.Logger):
        """Initialize the link manager.

        Args:
            sublinks: List of sublink patterns to filter for
            base_url: Base URL for domain filtering
            logger: Logger instance for logging operations
        """
        self.sublinks = sublinks
        self.base_url = base_url
        self.logger = logger
        self.queue: set[str] = set()
        self.visited: set[str] = set()

    def add_links(self, links: list[str]) -> None:
        """Filter and add links to the queue.

        Args:
            links: List of links to process
        """
        self.logger.debug(f"Processing {len(links)} total links")
        self.logger.debug(f"Sublinks filter: {self.sublinks}")

        filtered_links = self._filter_sublinks(links)
        self.logger.info(f"After filtering: {len(filtered_links)} links match criteria")

        added_count = 0
        for i, link in enumerate(filtered_links, 1):
            self.logger.debug(f"Processing link {i}/{len(filtered_links)}: {link}")

            if link not in self.visited:
                self.queue.add(link)
                self.visited.add(link)
                added_count += 1
                self.logger.debug("Added new link to queue")
            else:
                self.logger.debug("Link already visited")

        self.logger.info(
            f"Added {added_count} new links. "
            f"Queue size: {len(self.queue)}, Total visited: {len(self.visited)}"
        )

    def get_next(self) -> Optional[str]:
        """Get the next URL from the queue.

        Returns:
            Next URL to process, or None if queue is empty
        """
        if not self.queue:
            return None
        return self.queue.pop()

    def has_links(self) -> bool:
        """Check if there are links in the queue.

        Returns:
            True if queue has links, False otherwise
        """
        return len(self.queue) > 0

    def _filter_sublinks(self, links: list[str]) -> list[str]:
        """Filter links based on sublink patterns.

        Args:
            links: List of links to filter

        Returns:
            Filtered list of links
        """
        if not self.sublinks:
            return links

        return [
            link
            for link in links
            if link and any(sublink in link for sublink in self.sublinks)
        ]

    def filter_domain(self, link: str) -> bool:
        """Check if link belongs to the same domain.

        Args:
            link: Link to check

        Returns:
            True if link is from same domain or is relative, False otherwise
        """
        http_pattern = r"^https?://"
        has_http = re.search(http_pattern, link)

        if has_http and self.base_url not in link:
            self.logger.debug(f"Filtering out external domain: {link}")
            return False

        return True

    def build_full_url(self, path: str) -> str:
        """Build full URL from path.

        Args:
            path: Path or full URL

        Returns:
            Full URL
        """
        if "https://" in path or "http://" in path:
            return path
        return self.base_url + path
