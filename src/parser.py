"""HTML parsing and content extraction."""

import re
import logging
from bs4 import BeautifulSoup
from typing import Optional


class HTMLParser:
    """Handles HTML parsing and content extraction.

    Uses BeautifulSoup for parsing and provides methods for
    extracting links and content based on CSS selectors.
    """

    def __init__(self, logger: logging.Logger):
        """Initialize the HTML parser.

        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger

    def parse_html(self, html_content: bytes | str) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object.

        Args:
            html_content: HTML content as bytes or string

        Returns:
            BeautifulSoup object for parsing
        """
        if isinstance(html_content, bytes):
            html_content = html_content.decode("utf-8")

        return BeautifulSoup(html_content, "html.parser")

    def extract_links(self, soup: BeautifulSoup) -> list[str]:
        """Extract all links from HTML.

        Args:
            soup: BeautifulSoup object to extract links from

        Returns:
            List of href values from all anchor tags
        """
        links = [href for link in soup.find_all("a") if (href := link.get("href"))]
        self.logger.debug(f"Extracted {len(links)} links from HTML")
        return links

    def get_selector_type(self, selector: str) -> str:
        """Determine the type of CSS selector.

        Args:
            selector: CSS selector string

        Returns:
            Selector type: 'class', 'id', or 'tag'
        """
        if selector.startswith("."):
            return "class"
        elif selector.startswith("#"):
            return "id"
        else:
            return "tag"

    def extract_by_selector(self, soup: BeautifulSoup, selector: str) -> Optional[str]:
        """Extract text content using CSS selector.

        Handles special cases like 'main' elements where navigation
        should be excluded.

        Args:
            soup: BeautifulSoup object to extract from
            selector: CSS selector to use

        Returns:
            Extracted text content or None if not found
        """
        selector_type = self.get_selector_type(selector)
        data = ""

        try:
            if selector_type == "class":
                elements = soup.find_all(class_=selector.replace(".", ""))
                data = "\n".join(
                    [elem.get_text(separator=" ", strip=True) for elem in elements]
                )
            elif selector_type == "id":
                element = soup.find(id=selector.replace("#", ""))
                if element:
                    data = element.get_text(separator=" ", strip=True)
            else:
                element = soup.find(selector)
                if element:
                    self.logger.debug(
                        f"Found element: {element.name} with "
                        f"{len(element.get_text())} chars of text"
                    )

                    # Special handling for 'main' elements - exclude navigation
                    if selector == "main":
                        data = self._extract_from_main(element)
                    else:
                        data = element.get_text(separator=" ", strip=True)

                    # Clean up excessive whitespace
                    data = re.sub(r"\s+", " ", data).strip()

                    self.logger.debug(f"Extracted {len(data)} chars after cleaning")
                else:
                    self.logger.warning(f"No element found for selector: {selector}")

        except Exception as e:
            self.logger.error(
                f"Error extracting data with selector '{selector}': {str(e)}"
            )
            return None

        return data if data else None

    def _extract_from_main(self, main_element) -> str:
        """Extract content from main element, excluding navigation.

        Args:
            main_element: BeautifulSoup element representing <main>

        Returns:
            Extracted text content
        """
        # Try to find td-content div which contains actual page content
        content_div = main_element.find("div", class_="td-content")

        if content_div:
            self.logger.debug("Found td-content div, extracting from there")
            return content_div.get_text(separator=" ", strip=True)

        # Fallback: remove breadcrumb navigation
        breadcrumb = main_element.find("nav", attrs={"aria-label": "breadcrumb"})
        if breadcrumb:
            breadcrumb.decompose()

        return main_element.get_text(separator=" ", strip=True)
