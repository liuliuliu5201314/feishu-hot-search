import requests
from ..config import Config


class ZhihuHotService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://www.zhihu.com/"
        }
        self.proxies = Config.PROXY
    
    def get_hot_list(self):
        try:
            url = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            data = res.json()
            
            if data.get("error"):
                return [], "获取失败"
            
            items = []
            for i, item in enumerate(data.get("data", [])[:30], 1):
                target = item.get("target", {})
                title = target.get("title", "")
                question_id = target.get("id", "")
                excerpt = target.get("excerpt", "")
                heat = item.get("detail_text", "")
                
                items.append({
                    "rank": i,
                    "keyword": title,
                    "heat": heat,
                    "excerpt": excerpt[:50] + "..." if len(excerpt) > 50 else excerpt,
                    "url": f"https://www.zhihu.com/question/{question_id}"
                })
            
            return items, None
        except Exception as e:
            return [], str(e)
