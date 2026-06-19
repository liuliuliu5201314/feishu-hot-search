import re
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import unquote, parse_qs, urlparse
from xml.etree import ElementTree as ET

import requests

from ..config import Config

CN_TZ = timezone(timedelta(hours=8))


class MrhlwService:
    BASE_URL = "https://mrhlw1.com"

    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        }
        self.proxies = Config.PROXY

    def _get(self, url, timeout=20):
        last_error = None
        for proxies in (self.proxies, None):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    proxies=proxies,
                    timeout=timeout,
                )
                return response
            except requests.RequestException as exc:
                last_error = exc
        raise last_error

    def _today_cn(self):
        return datetime.now(CN_TZ).date()

    def _parse_cn_date(self, text):
        match = re.search(r"(\d{4})年(\d{2})月(\d{2})日", text or "")
        if not match:
            return None
        year, month, day = map(int, match.groups())
        return datetime(year, month, day, tzinfo=CN_TZ).date()

    def _normalize_link(self, href):
        if not href:
            return ""
        if href.startswith("http"):
            return href.rstrip("/") + "/"
        path = href if href.startswith("/") else f"/{href}"
        return f"{self.BASE_URL}{path}".rstrip("/") + "/"

    def _parse_list_page(self, html):
        articles = []
        for match in re.finditer(
            r'<article[^>]*BlogPosting[^>]*>(.*?)</article>', html, re.S
        ):
            block = match.group(1)
            if "videoBox" not in block:
                continue

            link_match = re.search(
                r'class=["\']videoCardLink["\'][^>]*href=["\']([^"\']+)["\']',
                block,
            ) or re.search(
                r'href=["\']([^"\']+)["\'][^>]*class=["\']videoCardLink["\']',
                block,
            )
            cover_match = re.search(
                r'class=["\']videoCover[^"\']*["\'][^>]*data-src=["\']([^"\']+)["\']',
                block,
            )
            title_match = re.search(
                r'class=["\']videoTitle["\'][^>]*>(.*?)</h2>', block, re.S
            )
            info_match = re.search(r'class=["\']videoInfo["\'][^>]*>(.*?)</div>', block, re.S)
            if not link_match or not title_match:
                continue

            info_text = re.sub(r"<[^>]+>", " ", info_match.group(1) if info_match else "")
            info_text = re.sub(r"\s+", " ", info_text).strip()
            author = ""
            author_match = re.search(r"^([^•]+)", info_text)
            if author_match:
                author = author_match.group(1).strip()

            categories = re.findall(r'href=["\']/category/[^"\']+["\'][^>]*>([^<]+)</a>', block)
            articles.append(
                {
                    "link": self._normalize_link(link_match.group(1)),
                    "title": re.sub(r"<[^>]+>", "", title_match.group(1)).strip(),
                    "cover": cover_match.group(1).strip() if cover_match else "",
                    "date": self._parse_cn_date(info_text),
                    "author": author,
                    "categories": ", ".join(categories),
                }
            )
        return articles

    def _fetch_list_pages(self, target_date):
        merged = {}
        page = 1
        while page <= 30:
            url = self.BASE_URL if page == 1 else f"{self.BASE_URL}/home/{page}"
            response = self._get(url)
            if response.status_code != 200:
                break

            items = self._parse_list_page(response.text)
            if not items:
                break

            page_has_target = False
            page_all_older = True
            for item in items:
                merged[item["link"]] = item
                if item["date"] == target_date:
                    page_has_target = True
                if item["date"] and item["date"] >= target_date:
                    page_all_older = False

            if page_all_older and not page_has_target:
                break
            page += 1
        return merged

    def _fetch_rss_items(self, target_date):
        response = self._get(f"{self.BASE_URL}/rss.xml", timeout=30)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        items = []
        for item in root.findall(".//item"):
            link = self._normalize_link(item.findtext("link", ""))
            title = (item.findtext("title") or "").strip()
            pub_text = item.findtext("pubDate", "")
            if not link or not title or not pub_text:
                continue
            pub_date = parsedate_to_datetime(pub_text).astimezone(CN_TZ).date()
            if pub_date != target_date:
                continue
            items.append(
                {
                    "link": link,
                    "title": title,
                    "date": pub_date,
                    "author": "",
                    "categories": "",
                    "cover": "",
                }
            )
        return items

    def _fetch_cover_from_detail(self, link):
        response = self._get(link)
        if response.status_code != 200:
            return ""
        og_match = re.search(
            r'property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']',
            response.text,
            re.I,
        ) or re.search(
            r'content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']',
            response.text,
            re.I,
        )
        if not og_match:
            return ""
        og_url = og_match.group(1)
        parsed = urlparse(og_url)
        if "/img/decrypt" in parsed.path:
            query = parse_qs(parsed.query)
            encoded = query.get("url", [""])[0]
            if encoded:
                return unquote(encoded)
        return og_url

    def fetch_today_articles(self, target_date=None):
        target_date = target_date or self._today_cn()
        rss_items = self._fetch_rss_items(target_date)
        list_map = self._fetch_list_pages(target_date)

        merged = {}
        for item in rss_items:
            merged[item["link"]] = item

        for link, item in list_map.items():
            if item["date"] != target_date:
                continue
            current = merged.get(link, {"link": link})
            current.update(
                {
                    "title": item["title"] or current.get("title", ""),
                    "cover": item["cover"] or current.get("cover", ""),
                    "author": item["author"] or current.get("author", ""),
                    "categories": item["categories"] or current.get("categories", ""),
                    "date": target_date,
                }
            )
            merged[link] = current

        results = []
        for link, item in merged.items():
            if not item.get("cover"):
                item["cover"] = self._fetch_cover_from_detail(link)
            item["date"] = target_date
            if item.get("title") and item.get("link"):
                results.append(item)

        results.sort(key=lambda x: x["link"])
        return results
