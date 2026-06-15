import requests


class BilibiliHotService:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
    
    def get_hot_list(self):
        try:
            url = "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all"
            res = requests.get(url, headers=self.headers, timeout=10)
            data = res.json()
            
            if data["code"] != 0:
                return [], "获取失败"
            
            items = []
            for i, item in enumerate(data.get("data", {}).get("list", [])[:20], 1):
                items.append({
                    "rank": i,
                    "title": item.get("title", ""),
                    "author": item.get("owner", {}).get("name", ""),
                    "play": item.get("stat", {}).get("view", 0),
                    "bvid": item.get("bvid", ""),
                    "url": f"https://www.bilibili.com/video/{item.get('bvid', '')}"
                })
            
            return items, None
        except Exception as e:
            return [], str(e)
