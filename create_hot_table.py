import requests
import json

APP_ID = 'cli_aa913ad0d7389cb6'
APP_SECRET = '7JOAZJEanZMAweftGNorxc2QqhaahuBS'
APP_TOKEN = 'XPAcblniKatqfjsw4v7cr5Ain8d'

token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={'app_id': APP_ID, 'app_secret': APP_SECRET}).json().get('tenant_access_token')

# 获取默认表格ID
url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables'
headers = {'Authorization': f'Bearer {token}'}
res = requests.get(url, headers=headers)
table_id = res.json().get('data', {}).get('items', [{}])[0].get('table_id')
print('Table ID:', table_id)

# 添加字段
fields_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{table_id}/fields'
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
