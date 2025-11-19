from bs4 import BeautifulSoup
import pycurl
import certifi
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str)
    parser.add_argument("--file_name", type=str, default="output.html")
    parser.add_argument("--sublinks", type=str, default="")
    parser.add_argument("--sub_path", type=str, default="")
    return parser.parse_args()


def process_sublinks(sublinks):
    return [link.strip() for link in sublinks.split(",")]


def fetch_url(url, writer_function):
    print(f"Fetching URL: {url}\n\n")
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.CAINFO, certifi.where())
    curl.setopt(pycurl.WRITEFUNCTION, writer_function)
    curl.perform()


def write_to_file(file_name, data):
    with open(file_name, "a", encoding="utf-8") as f:
        f.write(data.decode("utf-8"))


def create_soup_from_file(file_name):
    data = ""
    with open(file_name, "r", encoding="utf-8") as f:
        data += f.read()
    return BeautifulSoup(data, "html.parser")


def get_all_links(soup):
    return [href for link in soup.find_all("a") if (href := link.get("href"))]


def get_next_url(stack):
    return stack.pop()


def process_next_url(url, file_name, stack, visited, sublinks):
    print(f"Fetching URL: {url}\n\n")
    fetch_url(url, lambda x: write_to_file(file_name, x))
    print(f"Creating soup from file: {file_name}\n\n")
    soup = create_soup_from_file(file_name)
    print("Getting all links from soup\n\n")
    links = get_all_links(soup)
    print("Setting up links\n\n")
    set_up_links(stack, visited, links, sublinks)


def set_up_links(stack, visited, links, sublinks):
    current_link_number = 0
    print(f"Links: {links}\n\n")
    all_links_number = len(links)
    print(f"All links number: {all_links_number}\n\n")
    print(f"Sublinks: {sublinks}\n\n")
    for link in filter_for_sublinks(links, sublinks):
        print(f"Link: {link}\n\n")
        current_link_number += 1
        msg = f"Setting up link {current_link_number} " f"of {all_links_number}: {link}"
        print(f"{msg}\n\n")
        if link not in visited:
            stack.add(link)
            visited.add(link)


def filter_for_sublinks(links, sublinks):
    if not sublinks:
        return links
    return [
        link for link in links if link and any(sublink in link for sublink in sublinks)
    ]


def main():
    stack = set()
    visited = set()
    args = get_args()
    url = args.url
    file_name = args.file_name
    sublinks = process_sublinks(args.sublinks)
    sub_path = args.sub_path
    set_up_links(stack, visited, [sub_path], [])
    print(f"Sublinks: {sublinks}\n\n")
    print(f"Stack: {stack}\n\n")
    print(f"Visited: {visited}\n\n")
    print(f"File name: {file_name}\n\n")
    print(f"URL: {url}\n\n")
    print("stack before loop: ", stack)
    while stack:
        next_path = get_next_url(stack)
        next_url = url + next_path if "https://" not in next_path else next_path
        print(f"Starting to process URL: {next_url}\n\n")
        process_next_url(next_url, file_name, stack, visited, sublinks)


if __name__ == "__main__":
    main()
