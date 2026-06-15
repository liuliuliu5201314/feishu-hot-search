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
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

# 删除没用的字段
fields_to_delete = ["fldH4XvM7g", "fld8KJ7wpd", "fldZ5SSurE", "fldyU3xsfg"]
for field_id in fields_to_delete:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields/{field_id}"
    res = requests.delete(url, headers=headers)
    print(f"删除字段 {field_id}: {res.json().get('msg')}")

# 添加新字段
new_fields = [
    ("作者", 1),
    ("封面图", 15),
    ("简介", 1),
]
for field_name, field_type in new_fields:
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields"
    res = requests.post(url, headers=headers, json={"field_name": field_name, "type": field_type})
    print(f"添加字段 {field_name}: {res.json().get('msg')}")
