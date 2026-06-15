import requests
import json

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"
APP_TOKEN = "Zt1RboEwoatgaYsN9Hwcpgm6nYc"
TABLE_ID = "tbltiy9UgipbJSZY"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def add_field(token, field_name, field_type):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"field_name": field_name, "type": field_type}
    res = requests.post(url, headers=headers, json=data)
    return res.json()

token = get_token()

fields = [
    ("视频标题", 1),
    ("BV号", 1),
    ("字幕内容", 1),
    ("抓取时间", 5),
]

for name, ftype in fields:
    result = add_field(token, name, ftype)
    print(f"添加字段 {name}: {result.get('msg')}")
