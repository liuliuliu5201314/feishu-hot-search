import requests
import re
from ..config import Config


class ZhihuHotService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        self.proxies = Config.PROXY
    
    def get_hot_list(self):
        try:
            url = "https://tophub.today/n/mproPpoq6O"
            res = requests.get(url, headers=self.headers, proxies=self.proxies, timeout=15)
            
            items = []
            pattern = r'<span class="al">\s*<a[^>]*>(.*?)</a>'
            matches = re.findall(pattern, res.text, re.DOTALL)
            
            for i, title in enumerate(matches[:30], 1):
                title = title.strip()
                if title:
                    items.append({
                        "rank": i,
                        "keyword": title,
                        "heat": "",
                        "excerpt": "",
                        "url": f"https://www.zhihu.com/search?type=content&q={title}"
                    })
            
            if not items:
                return [], "获取失败"
            
            return items, None
        except Exception as e:
            return [], str(e)
