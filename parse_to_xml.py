import sys
import os
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import urljoin

HTML_FILES = [
    "opinion_bangladesherkhabor.html",
    "uposompadokio_protidinersangbad.html",
]

XML_FILE = "articles.xml"
MAX_ITEMS = 500

articles = []

# ======================================================
# LOAD & PARSE ALL HTML FILES
# ======================================================
for html_file in HTML_FILES:
    if not os.path.exists(html_file):
        continue

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")

    # --------------------------------------------------
    # BANGLADESHERKHABOR.NET — OPINION
    # --------------------------------------------------
    if "bangladesherkhabor" in html_file:
        for a in soup.select("a[href^='https://www.bangladesherkhabor.net/opinion/']"):
            url = a.get("href")

            title = None
            title_tag = a.select_one("p[class*='title'], h1, h2, h3")
            if title_tag:
                title = title_tag.get_text(strip=True)

            if not title:
                img = a.select_one("img")
                title = img.get("alt", "").strip() if img else None

            if not title:
                continue

            img_tag = a.select_one("img")
            img = img_tag.get("src", "") if img_tag else ""

            desc_tag = a.find_next("p", class_="desktopSummary")
            desc = desc_tag.get_text(strip=True) if desc_tag else ""

            articles.append({
                "url": url,
                "title": title,
                "desc": desc,
                "pub": "",
                "img": img
            })

    # --------------------------------------------------
    # PROTIDINER SANGBAD — UPOSOMPADOKIO
    # --------------------------------------------------
    if "protidinersangbad" in html_file:
        for a in soup.select("a[href*='/todays-newspaper/uposompadokio/']"):
            url = urljoin("https://www.protidinersangbad.com", a.get("href"))

            h = a.select_one("h2, h5")
            title = h.get_text(strip=True) if h else None
            if not title:
                continue

            img_tag = a.select_one("img")
            img = urljoin("https://www.protidinersangbad.com", img_tag["src"]) if img_tag and img_tag.get("src") else ""

            articles.append({
                "url": url,
                "title": title,
                "desc": "",
                "pub": "",
                "img": img
            })

# ======================================================
# LOAD OR CREATE XML
# ======================================================
if os.path.exists(XML_FILE):
    try:
        tree = ET.parse(XML_FILE)
        root = tree.getroot()
    except ET.ParseError:
        root = ET.Element("rss", version="2.0")
else:
    root = ET.Element("rss", version="2.0")

channel = root.find("channel")
if channel is None:
    channel = ET.SubElement(root, "channel")
    ET.SubElement(channel, "title").text = "Opinion Articles"
    ET.SubElement(channel, "link").text = ""
    ET.SubElement(channel, "description").text = "Combined opinion feeds"

# ======================================================
# DEDUPLICATION
# ======================================================
existing = set()
for item in channel.findall("item"):
    link = item.find("link")
    if link is not None and link.text:
        existing.add(link.text.strip())

# ======================================================
# APPEND NEW ARTICLES
# ======================================================
for art in articles:
    if art["url"] in existing:
        continue

    item = ET.SubElement(channel, "item")
    ET.SubElement(item, "title").text = art["title"]
    ET.SubElement(item, "link").text = art["url"]
    ET.SubElement(item, "description").text = art["desc"]
    ET.SubElement(item, "pubDate").text = (
        art["pub"] if art["pub"]
        else datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
    )

    if art["img"]:
        ET.SubElement(item, "enclosure", url=art["img"], type="image/jpeg")

# ======================================================
# TRIM XML
# ======================================================
items = channel.findall("item")
if len(items) > MAX_ITEMS:
    for old in items[:-MAX_ITEMS]:
        channel.remove(old)

# ======================================================
# SAVE XML
# ======================================================
tree = ET.ElementTree(root)
tree.write(XML_FILE, encoding="utf-8", xml_declaration=True)
