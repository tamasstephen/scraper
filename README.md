# Web Scraper

A Python web scraper that recursively fetches HTML content from web pages and extracts links, following them based on specified criteria.

## Features

- Recursively scrapes web pages starting from a base URL
- Extracts all links from HTML pages using BeautifulSoup
- Filters links based on sublink patterns
- Appends all fetched HTML content to a single output file
- Tracks visited URLs to avoid duplicate requests
- Uses pycurl for efficient HTTP requests with SSL certificate verification

## Requirements

- Python >= 3.13
- Dependencies listed in `pyproject.toml`:
  - `beautifulsoup4>=4.14.2`
  - `certifi>=2025.11.12`
  - `pycurl>=7.45.7`

## Installation

Install dependencies using `uv`:

```bash
uv sync
```

Or using pip:

```bash
pip install beautifulsoup4 certifi pycurl
```

## Usage

```bash
python main.py --url <BASE_URL> [OPTIONS]
```

### Arguments

- `--url` (required): The base URL to start scraping from
- `--file_name` (optional): Output file name for scraped HTML content (default: `output.html`)
- `--sublinks` (optional): Comma-separated list of sublink patterns to filter links. Only links containing these patterns will be followed
- `--sub_path` (optional): Initial path to add to the processing stack

### Examples

Scrape a website starting from a base URL:

```bash
python main.py --url https://example.com
```

Scrape and filter links containing specific patterns:

```bash
python main.py --url https://example.com --sublinks /docs,/api
```

Scrape with a custom output file:

```bash
python main.py --url https://example.com --file_name scraped_content.html
```

Scrape with an initial sub-path:

```bash
python main.py --url https://example.com --sub_path /about
```

## How It Works

1. **Initialization**: The scraper starts with a base URL and optional sub-path
2. **URL Fetching**: Uses pycurl to fetch HTML content from URLs
3. **HTML Parsing**: Parses HTML using BeautifulSoup to extract all anchor tags
4. **Link Extraction**: Extracts `href` attributes from all anchor tags (filters out `None` values)
5. **Link Filtering**: If `--sublinks` is provided, only links containing the specified patterns are processed
6. **Recursive Processing**: Follows links in a breadth-first manner using a stack data structure
7. **Duplicate Prevention**: Maintains a set of visited URLs to avoid processing the same URL twice
8. **Output**: Appends all fetched HTML content to the specified output file

## Output

All scraped HTML content is appended to a single file (default: `output.html`). The file accumulates content from all visited pages.

## Notes

- The scraper handles relative URLs by prepending the base URL when necessary
- Links with missing `href` attributes are automatically filtered out
- The scraper uses SSL certificate verification via certifi
- All print statements include two empty lines after the output for readability

