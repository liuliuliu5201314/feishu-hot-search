import requests
import json

# 飞书应用凭证
APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    data = {"app_id": APP_ID, "app_secret": APP_SECRET}
    res = requests.post(url, json=data)
    return res.json().get("tenant_access_token")

def get_bot_chats(token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats"
    headers = {"Authorization": f"Bearer {token}"}
    res = requests.get(url, headers=headers)
    return res.json()

token = get_tenant_token()
print(f"Token: {token[:20]}...")

chats = get_bot_chats(token)
print(json.dumps(chats, indent=2, ensure_ascii=False))
