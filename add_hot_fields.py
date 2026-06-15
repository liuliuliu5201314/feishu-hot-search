import requests
import json

APP_ID = 'cli_aa913ad0d7389cb6'
APP_SECRET = '7JOAZJEanZMAweftGNorxc2QqhaahuBS'
BASE_TOKEN = 'YoZQbG6KpakTEjsJa01c4xOZnMe'
TABLE_ID = 'tblLv11iIPrg93ls'

token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={'app_id': APP_ID, 'app_secret': APP_SECRET}).json().get('tenant_access_token')

# 添加热搜字段
fields_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields'
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

fields = [
    ('抓取时间', 5),
    ('B站热搜1', 1),
    ('B站热搜2', 1),
    ('B站热搜3', 1),
    ('B站热搜4', 1),
    ('B站热搜5', 1),
    ('微博热搜1', 1),
    ('微博热搜2', 1),
    ('微博热搜3', 1),
    ('微博热搜4', 1),
    ('微博热搜5', 1),
    ('知乎热搜1', 1),
    ('知乎热搜2', 1),
    ('知乎热搜3', 1),
    ('知乎热搜4', 1),
    ('知乎热搜5', 1),
]

for name, ftype in fields:
    res = requests.post(fields_url, headers=headers, json={'field_name': name, 'type': ftype})
    print(name + ': ' + res.json().get('msg'))
