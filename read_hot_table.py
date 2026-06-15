import requests
import json

APP_ID = 'cli_aa913ad0d7389cb6'
APP_SECRET = '7JOAZJEanZMAweftGNorxc2QqhaahuBS'
BASE_TOKEN = 'YoZQbG6KpakTEjsJa01c4xOZnMe'
TABLE_ID = 'tblLv11iIPrg93ls'

token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={'app_id': APP_ID, 'app_secret': APP_SECRET}).json().get('tenant_access_token')

# 读取表格字段
url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields'
headers = {'Authorization': f'Bearer {token}'}
res = requests.get(url, headers=headers)
data = res.json()
print('表格字段:')
for item in data.get('data', {}).get('items', []):
    print(f"{item.get('field_name')} - type: {item.get('type')}")
