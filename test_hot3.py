import requests
import re

# 测试B站 - 用网页抓取
print("=== B站热榜 ===")
try:
    res = requests.get("https://www.bilibili.com/v/popular/rank/all", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'"title":"(.*?)"', res.text)
    for i, title in enumerate(titles[:5], 1):
        print(str(i) + ". " + title)
except Exception as e:
    print("Error:", e)

# 测试微博 - 用网页抓取
print("\n=== 微博热搜 ===")
try:
    res = requests.get("https://s.weibo.com/top/summary", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'<td class="td-02">\s*<a[^>]*>(.*?)</a>', res.text)
    for i, title in enumerate(titles[:5], 1):
        print(str(i) + ". " + title.strip())
except Exception as e:
    print("Error:", e)

# 测试知乎 - 用网页抓取
print("\n=== 知乎热榜 ===")
try:
    res = requests.get("https://www.zhihu.com/hot", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'<h2 class="HotItem-title"[^>]*>(.*?)</h2>', res.text)
    for i, title in enumerate(titles[:5], 1):
        print(str(i) + ". " + title.strip())
except Exception as e:
    print("Error:", e)
