"""File I/O operations for the web scraper."""

import logging
from datetime import datetime
from pathlib import Path
from markitdown import MarkItDown


class FileHandler:
    """Handles all file operations for the scraper.

    Manages writing HTML content, extracted data, and markdown conversion.
    """

    def __init__(self, html_file: str, logger: logging.Logger):
        """Initialize the file handler.

        Args:
            html_file: Path to the HTML output file
            logger: Logger instance for logging operations
        """
        self.html_file = html_file
        self.logger = logger
        self._ensure_html_file_exists()

    def _ensure_html_file_exists(self) -> None:
        """Ensure the HTML file exists and is empty at start."""
        try:
            Path(self.html_file).write_text("", encoding="utf-8")
            self.logger.debug(f"Initialized HTML file: {self.html_file}")
        except Exception as e:
            self.logger.warning(f"Could not initialize HTML file: {e}")

    def write_html(self, data: bytes | str) -> None:
        """Write HTML data to the main HTML file.

        Args:
            data: HTML content as bytes or string
        """
        try:
            with open(self.html_file, "a", encoding="utf-8") as f:
                if isinstance(data, bytes):
                    f.write(data.decode("utf-8"))
                else:
                    f.write(str(data))
            self.logger.debug(f"Wrote HTML data to {self.html_file}")
        except Exception as e:
            self.logger.error(f"Failed to write HTML: {e}")
            raise

    def initialize_data_file(self, selector: str) -> None:
        """Initialize the data extraction file with header.

        Args:
            selector: CSS selector being used for extraction
        """
        data_file = f"data_{selector}.txt"
        try:
            with open(data_file, "w", encoding="utf-8") as f:
                f.write(f"Extracted data for selector '{selector}'\n")
                f.write(
                    f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                )
            self.logger.debug(f"Initialized data file: {data_file}")
        except Exception as e:
            self.logger.warning(f"Could not initialize data file: {e}")

    def write_extracted_data(self, selector: str, url: str, data: str) -> None:
        """Write extracted data to selector-specific file.

        Args:
            selector: CSS selector used for extraction
            url: URL the data was extracted from
            data: Extracted text content
        """
        data_file = f"data_{selector}.txt"

        try:
            equals_line = "=" * 80
            separator = f"\n{equals_line}\nPAGE: {url}\n{equals_line}\n\n"

            with open(data_file, "a", encoding="utf-8") as f:
                f.write(separator + data + "\n")

            self.logger.debug(
                f"Wrote {len(data)} chars of extracted data to {data_file}"
            )
        except Exception as e:
            self.logger.error(f"Failed to write extracted data: {e}")
            raise

    def convert_to_markdown(self) -> None:
        """Convert the HTML file to markdown format.

        Creates a .md file with the same base name as the HTML file.
        """
        self.logger.info(f"Converting {self.html_file} to markdown")

        try:
            md = MarkItDown()
            result = md.convert(self.html_file)
            text_result = result.text_content

            output_file = self.html_file.replace(".html", ".md")

            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text_result)

            self.logger.info(f"Markdown conversion saved to {output_file}")
        except Exception as e:
            self.logger.error(f"Failed to convert {self.html_file} to markdown: {e}")
            raise
