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
            # 找到所有知乎热榜链接
            pattern = r'<a href="https://www\.zhihu\.com/question/[^"]+"[^>]*>(.*?)</a>'
            matches = re.findall(pattern, res.text)
            
            for i, title in enumerate(matches[:30], 1):
                title = re.sub(r'<[^>]+>', '', title).strip()  # 去除HTML标签
                if title and len(title) > 5:  # 过滤太短的内容
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
