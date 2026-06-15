import requests
from ..config import Config


class BilibiliHotService:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
        self.proxies = Config.PROXY
    
    def get_hot_list(self):
        try:
            url = "https://api.bilibili.com/x/web-interface/wbi/search/square?limit=50"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = res.json()
            
            if data["code"] != 0:
                return [], "获取失败"
            
            items = []
            for i, item in enumerate(data.get("data", {}).get("trending", {}).get("list", [])[:30], 1):
                keyword = item.get("keyword", "")
                show_name = item.get("show_name", "")
                heat = item.get("heat_score", 0)
                
                items.append({
                    "rank": i,
                    "keyword": keyword,
                    "show_name": show_name,
                    "heat": heat,
                    "url": f"https://search.bilibili.com/all?keyword={keyword}"
                })
            
            return items, None
        except Exception as e:
            return [], str(e)
