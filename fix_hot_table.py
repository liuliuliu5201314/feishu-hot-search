import requests
import json

APP_ID = 'cli_aa913ad0d7389cb6'
APP_SECRET = '7JOAZJEanZMAweftGNorxc2QqhaahuBS'
BASE_TOKEN = 'YoZQbG6KpakTEjsJa01c4xOZnMe'
TABLE_ID = 'tblLv11iIPrg93ls'

token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', json={'app_id': APP_ID, 'app_secret': APP_SECRET}).json().get('tenant_access_token')
headers = {'Authorization': f'Bearer {token}'}

# 获取所有字段
url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields'
res = requests.get(url, headers=headers)
data = res.json()

print('当前字段:')
for item in data.get('data', {}).get('items', []):
    print(f"  {item.get('field_name')} (id: {item.get('field_id')})")

# 删除多余的字段，只保留：文本、单选、日期、附件、抓取时间、B站热搜、微博热搜、知乎热搜
fields_to_keep = ['文本', '单选', '日期', '附件', '抓取时间', 'B站热搜', '微博热搜', '知乎热搜']
fields_to_delete = [item for item in data.get('data', {}).get('items', []) if item.get('field_name') not in fields_to_keep]

print(f'\n需要删除 {len(fields_to_delete)} 个字段:')
for item in fields_to_delete:
    print(f"  删除: {item.get('field_name')} (id: {item.get('field_id')})")

# 删除字段
for item in fields_to_delete:
    field_id = item.get('field_id')
    del_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields/{field_id}'
    res = requests.delete(del_url, headers=headers)
    print(f"  删除 {item.get('field_name')}: {res.json().get('msg')}")

# 检查是否已有热搜字段，没有则添加
current_fields = [item.get('field_name') for item in data.get('data', {}).get('items', [])]
fields_to_add = []
if 'B站热搜' not in current_fields:
    fields_to_add.append(('B站热搜', 1))
if '微博热搜' not in current_fields:
    fields_to_add.append(('微博热搜', 1))
if '知乎热搜' not in current_fields:
    fields_to_add.append(('知乎热搜', 1))

if fields_to_add:
    print(f'\n需要添加 {len(fields_to_add)} 个字段:')
    fields_url = f'https://open.feishu.cn/open-apis/bitable/v1/apps/{BASE_TOKEN}/tables/{TABLE_ID}/fields'
    headers_post = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    for name, ftype in fields_to_add:
        res = requests.post(fields_url, headers=headers_post, json={'field_name': name, 'type': ftype})
        print(f"  添加 {name}: {res.json().get('msg')}")
