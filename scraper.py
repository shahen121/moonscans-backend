import requests
from bs4 import BeautifulSoup

BASE_URL = "https://moonscans.net"


def get_manga_list():
    url = BASE_URL + "/manga/"
    html = requests.get(url, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    mangas = []

    for item in soup.select(".bsx"):
        a_tag = item.select_one("a")
        img_tag = item.select_one("img")

        if not a_tag or not img_tag:
            continue

        title = img_tag.get("alt", "").strip()
        link = a_tag["href"]
        cover = img_tag["src"]

        mangas.append({
            "title": title,
            "slug": link.rstrip("/").split("/")[-1],
            "cover": cover,
            "url": link
        })

    return mangas


def get_manga_details(slug: str):
    url = f"{BASE_URL}/manga/{slug}/"
    html = requests.get(url, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    title_tag = soup.select_one("h1")
    title = title_tag.text.strip() if title_tag else ""

    summary_tag = soup.select_one(".summary__content")
    summary = summary_tag.text.strip() if summary_tag else ""

    status_tag = soup.find("div", class_="post-status")
    status = status_tag.text.strip() if status_tag else "Unknown"

    chapters = []
    for ch in soup.select(".wp-manga-chapter a"):
        chapters.append({
            "name": ch.text.strip(),
            "url": ch["href"]
        })

    return {
        "title": title,
        "summary": summary,
        "status": status,
        "chapters": chapters
    }


def get_chapter_images(chapter_url: str):
    html = requests.get(chapter_url, timeout=15).text
    soup = BeautifulSoup(html, "html.parser")

    images = []

    for img in soup.select(".reading-content img"):
        src = img.get("data-src") or img.get("src")
        if src:
            images.append(src)

    return images
