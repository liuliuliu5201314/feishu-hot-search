import requests

from ..config import Config


class ZhihuSearchHotService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/",
        }
        self.proxies = Config.PROXY

    def get_hot_list(self):
        try:
            url = "https://www.zhihu.com/api/v4/search/recommend_query/v2"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = res.json()
            queries = (data.get("recommend_queries") or {}).get("queries") or []

            items = []
            for i, item in enumerate(queries[:30], 1):
                keyword = item.get("query_display") or item.get("query") or ""
                if not keyword:
                    continue
                items.append(
                    {
                        "rank": i,
                        "keyword": keyword,
                        "heat": "",
                        "label": item.get("label", ""),
                        "url": "https://www.zhihu.com/search?q=" + requests.utils.quote(keyword),
                    }
                )

            if not items:
                return [], "获取失败"
            return items, None
        except Exception as e:
            return [], str(e)
