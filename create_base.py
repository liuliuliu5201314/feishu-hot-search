import requests
import json

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def create_base(token):
    url = "https://open.feishu.cn/open-apis/bitable/v1/apps"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"name": "B站字幕采集"}
    res = requests.post(url, headers=headers, json=data)
    return res.json()

token = get_token()
result = create_base(token)
print(json.dumps(result, indent=2, ensure_ascii=False))
