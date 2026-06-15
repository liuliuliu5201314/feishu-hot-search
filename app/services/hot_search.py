import requests
from datetime import datetime
from ..config import Config


class HotSearchService:
    def __init__(self):
        self.app_id = Config.FEISHU_APP_ID
        self.app_secret = Config.FEISHU_APP_SECRET
        self.hot_base_token = Config.HOT_BASE_TOKEN
        self.hot_table_id = Config.HOT_TABLE_ID
    
    def get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        res = requests.post(url, json={"app_id": self.app_id, "app_secret": self.app_secret})
        return res.json().get("tenant_access_token")
    
    def write_hot_data(self, bilibili_items, weibo_items, zhihu_items):
        token = self.get_token()
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.hot_base_token}/tables/{self.hot_table_id}/records"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        now = datetime.now()
        timestamp_ms = int(now.timestamp() * 1000)
        
        bilibili_text = "\n".join([f"{i}. {item.get('keyword', '')}" for i, item in enumerate(bilibili_items[:10], 1)])
        weibo_text = "\n".join([f"{i}. {item.get('keyword', '')}" for i, item in enumerate(weibo_items[:10], 1)])
        zhihu_text = "\n".join([f"{i}. {item.get('keyword', '')}" for i, item in enumerate(zhihu_items[:10], 1)])
        
        fields = {
            "抓取时间": timestamp_ms,
            "B站热搜": bilibili_text,
            "微博热搜": weibo_text,
            "知乎热搜": zhihu_text
        }
        
        data = {"fields": fields}
        res = requests.post(url, headers=headers, json=data)
        return res.json()
