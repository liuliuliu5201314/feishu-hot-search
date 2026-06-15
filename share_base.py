import requests
import json

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"
APP_TOKEN = "Zt1RboEwoatgaYsN9Hwcpgm6nYc"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def share_base(token):
    url = f"https://open.feishu.cn/open-apis/drive/v1/permissions/{APP_TOKEN}/members"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "member_type": "openchat",
        "member_id": "oc_e6c00175d7bf047de0f647d4c31db4f2",
        "perm": "full_access"
    }
    res = requests.post(url, headers=headers, params={"type": "bitable"}, json=data)
    return res.json()

token = get_token()
result = share_base(token)
print(json.dumps(result, indent=2, ensure_ascii=False))
