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
            # 只匹配标题列 td.al 内的链接，跳过右侧图标链接（&#xe652;）
            pattern = r'<td class="al">\s*<div><a href="(https://www\.zhihu\.com/question/[^"]+)"[^>]*>(.*?)</a></div>'
            matches = re.findall(pattern, res.text, re.DOTALL)
            
            for i, (href, title) in enumerate(matches[:30], 1):
                title = re.sub(r'<[^>]+>', '', title).strip()
                if title:
                    items.append({
                        "rank": i,
                        "keyword": title,
                        "heat": "",
                        "excerpt": "",
                        "url": href
                    })
            
            if not items:
                return [], "获取失败"
            
            return items, None
        except Exception as e:
            return [], str(e)
