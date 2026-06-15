import requests
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
url = 'https://tophub.today/n/mproPpoq6O'
res = requests.get(url, headers=headers, timeout=15)

pattern = r'<a href="https://www\.zhihu\.com/question/[^"]+"[^>]*>(.*?)</a>'
matches = re.findall(pattern, res.text)

print('Found', len(matches), 'items')
for i, m in enumerate(matches[:10], 1):
    clean = re.sub(r'<[^>]+>', '', m).strip()
    print(f'{i}. [{len(clean)}] {clean[:60]}')
