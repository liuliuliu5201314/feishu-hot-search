import requests
import json

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"
BASE_TOKEN = "O87ebAsOKaDlsQst6nccQp2InTd"
TABLE_ID = "tblsRVZOdBJQndkM"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

token = get_token()

fields = [("视频标题", 1), ("BV号", 1), ("字幕内容", 1), ("抓取时间", 5)]

for name, ftype in fields:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json={"field_name": name, "type": ftype})
    print(f"{name}: {res.json().get('msg')}")
