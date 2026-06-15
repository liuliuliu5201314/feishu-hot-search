import requests
from ..config import Config


class WeiboHotService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://weibo.com/"
        }
        self.proxies = Config.PROXY
    
    def get_hot_list(self):
        try:
            url = "https://weibo.com/ajax/side/hotSearch"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = res.json()
            
            if data.get("ok") != 1:
                return [], "获取失败"
            
            items = []
            for i, item in enumerate(data.get("data", {}).get("realtime", [])[:30], 1):
                word = item.get("word", "")
                num = item.get("num", 0)
                label_name = item.get("label_name", "")
                
                items.append({
                    "rank": i,
                    "keyword": word,
                    "heat": num,
                    "label": label_name,
                    "url": f"https://s.weibo.com/weibo?q={word}"
                })
            
            return items, None
        except Exception as e:
            return [], str(e)
