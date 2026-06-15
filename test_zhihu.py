import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://tophub.today/n/mproPpoq6O'
res = requests.get(url, headers=headers, timeout=15)

print('Status:', res.status_code)
print('Length:', len(res.text))

# 测试不同的正则表达式
pattern1 = r'class="al"[^>]*>(.*?)</span>'
matches1 = re.findall(pattern1, res.text, re.DOTALL)
print('Pattern 1 matches:', len(matches1))

if matches1:
    for m in matches1[:5]:
        print('  -', m.strip()[:60])
