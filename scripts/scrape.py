import sys
import os
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def save_text_to_file(text, filename):
    with open(filename, 'w') as f:
        f.write(text)

def download_page(url):
    try:
        with urllib.request.urlopen(url) as response:
            html = response.read()
    except Exception as e:
        print(f"Failed to download {url}")
        print(e)
        return None
    return html

def get_links_from_html(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for a in soup.find_all('a', href=True):
        link = a['href']
        if not is_valid(link):
            link = urljoin(base_url, link)
        # store both the URL and the link text
        links.append((link, a.text))
    return links

def remove_html_markup(text):
    soup = BeautifulSoup(text, 'html.parser')
    return soup.get_text()

def download_and_save_pages(url):
    html = download_page(url)
    if html is None:
        return
    links = get_links_from_html(html, url)
    print(f"Found {len(links)} links")
    for i, (link, link_text) in enumerate(links):
        html = download_page(link)
        if html is None:
            continue
        text = remove_html_markup(html)
        save_text_to_file(text, f'{i+1}-{link_text.lower().replace(" ", "-")}.txt')

if __name__ == '__main__':
    # Download and save pages linked from the given URL
    download_and_save_pages(sys.argv[1])
