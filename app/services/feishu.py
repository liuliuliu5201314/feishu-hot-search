import requests
import json
from datetime import datetime
from ..config import Config


class FeishuService:
    def __init__(self):
        self.app_id = Config.FEISHU_APP_ID
        self.app_secret = Config.FEISHU_APP_SECRET
        self.chat_id = Config.FEISHU_CHAT_ID
        self.base_token = Config.BASE_TOKEN
        self.table_id = Config.TABLE_ID
    
    def get_token(self):
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        res = requests.post(url, json={"app_id": self.app_id, "app_secret": self.app_secret})
        return res.json().get("tenant_access_token")
    
    def send_message(self, token, content):
        url = "https://open.feishu.cn/open-apis/im/v1/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        data = {"receive_id": self.chat_id, "msg_type": "text", "content": json.dumps({"text": content})}
        res = requests.post(url, headers=headers, params={"receive_id_type": "chat_id"}, json=data)
        return res.json()
    
    def write_to_base(self, token, data):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        res = requests.post(url, headers=headers, json={"fields": data})
        return res.json()
    
    def update_base_record(self, token, record_id, data):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records/{record_id}"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        res = requests.put(url, headers=headers, json={"fields": data})
        return res.json()
    
    def get_base_records(self, token, filter_str=None):
        url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{self.base_token}/tables/{self.table_id}/records"
        headers = {"Authorization": f"Bearer {token}"}
        params = {}
        if filter_str:
            params["filter"] = filter_str
        res = requests.get(url, headers=headers, params=params)
        return res.json()
