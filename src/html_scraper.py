import requests  # HTTP requests
from bs4 import BeautifulSoup  # HTML parsing
from urllib.parse import urljoin  # To build absolute URLs
from config import BASE_URL, PRESS_RELEASE_URL  # URLs config


def fetch_press_releases():
    r = requests.get(PRESS_RELEASE_URL, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
    r.raise_for_status()  # Check for request success
    r.encoding = 'utf-8'  # Ensure proper encoding for Japanese text

    soup = BeautifulSoup(r.text, "html.parser")
    dl = soup.find("dl")  # Locate the container holding releases
    if not dl:
        raise Exception("Could not find <dl> element on the page")

    dts = dl.find_all("dt")  # Dates
    dds = dl.find_all("dd")  # Corresponding release info

    press_list = []
    for dt, dd in zip(dts, dds):
        date = dt.get_text(strip=True)
        a = dd.find("a")
        if a:
            link = urljoin(BASE_URL, a['href'])  # Convert to full URL
            title = a.get_text(strip=True)
            press_list.append({"date": date, "title_jp": title, "pdf_link": link})

    return press_list
