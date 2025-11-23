# Web Scraper

A modular Python web scraper that recursively fetches HTML content from web pages, extracts links, and optionally extracts specific content based on CSS selectors.

## Features

### Core Scraping
- **URL Fetching with pycurl**: HTTP/HTTPS request handling with SSL certificate verification
- **HTML Parsing & Link Extraction**: Extract all anchor tag links from pages using BeautifulSoup
- **Recursive Web Crawling**: Depth-controlled recursive crawling with visited URL tracking
- **Domain Restriction**: Automatic filtering to stay on the same domain (configurable)
- **Boilerplate Content Removal**: Intelligently removes navigation, headers, footers, and sidebars

### Content Extraction & Filtering
- **CSS Selector-Based Data Extraction**: Extract content by class (`.classname`), ID (`#id`), or HTML tag selectors
- **Sublink Pattern Filtering**: Filter links by comma-separated patterns for fine-grained crawling control
- **Custom Starting Path**: Specify a sub_path to begin scraping from specific subdirectories
- **Fallback Content Selection**: Automatically falls back to body content if target selector not found

### Output & Conversion
- **Dual Output Modes**:
  - Always saves cleaned HTML content to file
  - Optionally extracts specific content using CSS selectors to separate data files
- **HTML to Markdown Conversion**: Automatically converts collected HTML to Markdown format using MarkItDown
- **Data Extraction to Separate Files**: Save extracted content to selector-specific files with URL source tracking
- **UTF-8 Encoding Support**: Proper handling of character encoding in all output files

### Logging & Monitoring
- **Configurable Logging Levels**: DEBUG, INFO, WARNING, ERROR levels with formatted timestamps
- **Progress Reporting**: Real-time progress updates and final summary statistics
- **Component-Specific Logging**: Detailed logging from all modules for debugging

### Architecture & Code Quality
- **Modular Architecture**: Clean separation of concerns with dedicated modules for fetching, parsing, file operations, and link management
- **Multi-Module Design**: Fetcher, Parser, FileHandler, LinkManager, Config, and WebScraper modules
- **Error Handling & Recovery**: Graceful error handling without stopping the entire crawl
- **Memory-Efficient Processing**: Set-based storage and stream-based file operations

## Advanced Features

- **Smart Content Detection**: Special handling for Kubernetes/td-content div layouts and common content patterns
- **Navigation Removal**: Automatic detection and removal of breadcrumb navigation and header elements
- **Deep Element Copying**: Preserves original DOM structure while extracting content
- **Whitespace Normalization**: Cleans up extracted text by normalizing whitespace
- **Output Directory Management**: Organize scrape results in customizable output directories
- **Selector Fallback Chain**: Intelligently falls back to alternative selectors if primary extraction fails
- **Main Element Optimization**: Special optimized handling for `<main>` element extraction

## Architecture

```
scraper/
├── src/
│   ├── __init__.py         # Package initialization
│   ├── config.py           # Configuration management and CLI parsing
│   ├── scraper.py          # Main orchestrator class
│   ├── fetcher.py          # HTTP fetching with pycurl
│   ├── parser.py           # HTML parsing with BeautifulSoup
│   ├── file_handler.py     # File I/O operations
│   └── link_manager.py     # Link queue and filtering
├── main.py                 # Entry point
├── pyproject.toml          # Project dependencies
└── README.md               # This file
```

## Requirements

- Python >= 3.13
- Dependencies listed in `pyproject.toml`:
  - `beautifulsoup4>=4.14.2` - HTML parsing
  - `certifi>=2025.11.12` - SSL certificate verification
  - `pycurl>=7.45.7` - HTTP requests
  - `markitdown>=0.0.1a2` - Markdown conversion

## Installation

Install dependencies using `uv`:

```bash
uv sync
```

Or using pip:

```bash
pip install beautifulsoup4 certifi pycurl markitdown
```

## Usage

```bash
python main.py --url <BASE_URL> [OPTIONS]
```

Or with uv:

```bash
uv run python main.py --url <BASE_URL> [OPTIONS]
```

### Arguments

- `--url` (required): The base URL to start scraping from
- `--file_name` (optional): Output HTML file name (default: `output.html`)
- `--sublinks` (optional): Comma-separated list of sublink patterns to filter links
- `--sub_path` (optional): Initial path to start scraping from
- `--max_depth` (optional): Maximum depth for recursive scraping (default: 10)
- `--target_selector` (optional): CSS selector for extracting specific content
- `--log_level` (optional): Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
- `--strict_url` (optional): Enforce strict URL matching (default: True)

### Examples

**Basic scraping (HTML + Markdown output):**

```bash
python main.py --url https://example.com
```

**Scrape with link filtering:**

```bash
python main.py --url https://example.com --sublinks /docs,/api
```

**Extract specific content using CSS selector:**

```bash
python main.py --url https://kubernetes.io \
  --file_name kubernetes.html \
  --sublinks documents,docs \
  --sub_path /docs/home/ \
  --target_selector main
```

This creates:
- `kubernetes.html` - Complete HTML content
- `kubernetes.md` - Markdown conversion
- `data_main.txt` - Extracted content from `<main>` elements

**Debug mode with custom depth:**

```bash
python main.py --url https://example.com \
  --max_depth 5 \
  --log_level DEBUG
```

## How It Works

### Architecture Overview

1. **Configuration** (`config.py`): Parses CLI arguments and validates configuration
2. **Scraper** (`scraper.py`): Orchestrates all components and manages the scraping loop
3. **Fetcher** (`fetcher.py`): Handles HTTP requests using pycurl with SSL verification
4. **Parser** (`parser.py`): Parses HTML and extracts links and content using BeautifulSoup
5. **Link Manager** (`link_manager.py`): Manages URL queue, filtering, and visited tracking
6. **File Handler** (`file_handler.py`): Handles all file I/O operations

### Scraping Process

1. **Initialization**: Parse arguments, create configuration, initialize components
2. **URL Processing**: 
   - Fetch HTML content from URL
   - Write HTML to output file (always)
   - Parse HTML and extract links
   - Add filtered links to queue
   - If target_selector is provided, extract and save specific content
3. **Recursive Processing**: Continue until max depth reached or queue is empty
4. **Markdown Conversion**: Convert final HTML file to Markdown format

### Content Extraction

When `--target_selector` is provided:

- **Class selectors** (`.classname`): Extracts from all elements with that class
- **ID selectors** (`#id`): Extracts from element with that ID
- **Tag selectors** (`main`, `article`, etc.): Extracts from first matching tag
- **Special handling for `main`**: Automatically excludes navigation and breadcrumbs

Extracted content is saved to `data_{selector}.txt` with page separators for easy reading.

## Output Files

### Always Created

- **HTML file** (e.g., `output.html`): Complete HTML content from all visited pages
- **Markdown file** (e.g., `output.md`): Markdown conversion of HTML content

### Optional (with --target_selector)

- **Data file** (e.g., `data_main.txt`): Extracted text content with page separators

Example data file format:

```
Extracted data for selector 'main'
Started at: 2025-11-22 22:10:27

================================================================================
PAGE: https://example.com/page1
================================================================================

[Extracted content from page 1]

================================================================================
PAGE: https://example.com/page2
================================================================================

[Extracted content from page 2]
```

## Logging

The scraper provides structured logging with timestamps and severity levels:

```
22:09:56 [INFO] Starting web scraper
22:09:56 [INFO] Configuration: URL=https://example.com, File=test.html, Max depth=1
22:09:56 [INFO] Fetching URL: https://example.com/
22:09:56 [INFO] Found 10 links on page
22:09:56 [INFO] Progress: 1 URLs processed, queue=5, visited=6
```

Use `--log_level DEBUG` for detailed debugging information.

## Development

### Project Structure

Each module has a single responsibility:

- **config.py**: Configuration and argument parsing
- **fetcher.py**: HTTP operations
- **parser.py**: HTML parsing and extraction
- **file_handler.py**: File I/O
- **link_manager.py**: URL queue management
- **scraper.py**: Orchestration

This modular design makes the code:
- Easy to test (each component can be tested independently)
- Easy to maintain (changes are localized)
- Easy to extend (new features can be added without affecting other components)

### Adding New Features

To add a new feature:

1. Identify which module it belongs to
2. Add the functionality to that module
3. Update the scraper orchestrator if needed
4. Update configuration if new CLI arguments are needed

## Notes

- The scraper handles both relative and absolute URLs
- SSL certificate verification is enabled by default
- Duplicate URLs are automatically filtered out
- External domains are filtered unless they match the base URL
- The scraper is respectful of server resources (processes one URL at a time)

## License

This project is open source and available for use in documentation and learning.
