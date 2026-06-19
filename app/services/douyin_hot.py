import requests

from ..config import Config


class DouyinHotService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.douyin.com/",
        }
        self.proxies = Config.PROXY

    def get_hot_list(self):
        try:
            url = "https://www.iesdouyin.com/web/api/v2/hotsearch/billboard/word/"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = res.json()
            word_list = data.get("word_list") or []

            items = []
            for i, item in enumerate(word_list[:30], 1):
                keyword = item.get("word", "")
                if not keyword:
                    continue
                items.append(
                    {
                        "rank": i,
                        "keyword": keyword,
                        "heat": item.get("hot_value", 0),
                        "label": str(item.get("label", "")),
                        "url": "https://www.douyin.com/search/" + requests.utils.quote(keyword),
                    }
                )

            if not items:
                return [], "获取失败"
            return items, None
        except Exception as e:
            return [], str(e)
