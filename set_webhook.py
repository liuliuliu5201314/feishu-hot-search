import requests
import json

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def set_webhook(token):
    url = "https://open.feishu.cn/open-apis/application/v6/app_patch"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "app_id": APP_ID,
        "webhook": "https://feishu-hot-search.onrender.com/webhook"
    }
    res = requests.patch(url, headers=headers, json=data)
    return res.json()

def add_event(token):
    url = f"https://open.feishu.cn/open-apis/application/v6/app_patch"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "app_id": APP_ID,
        "events": ["im.message.receive_v1"]
    }
    res = requests.patch(url, headers=headers, json=data)
    return res.json()

token = get_token()
print("设置 webhook:")
print(json.dumps(set_webhook(token), indent=2, ensure_ascii=False))
print("\n添加事件:")
print(json.dumps(add_event(token), indent=2, ensure_ascii=False))
