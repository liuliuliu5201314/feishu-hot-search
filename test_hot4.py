import requests
import re

results = []

# 测试B站
try:
    res = requests.get("https://www.bilibili.com/v/popular/rank/all", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'"title":"(.*?)"', res.text)
    results.append("=== B站热榜 ===")
    for i, title in enumerate(titles[:5], 1):
        results.append(str(i) + ". " + title)
except Exception as e:
    results.append("B站 Error: " + str(e))

# 测试微博
try:
    res = requests.get("https://s.weibo.com/top/summary", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'<td class="td-02">\s*<a[^>]*>(.*?)</a>', res.text)
    results.append("\n=== 微博热搜 ===")
    for i, title in enumerate(titles[:5], 1):
        results.append(str(i) + ". " + title.strip())
except Exception as e:
    results.append("微博 Error: " + str(e))

# 测试知乎
try:
    res = requests.get("https://www.zhihu.com/hot", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=10)
    titles = re.findall(r'<h2 class="HotItem-title"[^>]*>(.*?)</h2>', res.text)
    results.append("\n=== 知乎热榜 ===")
    for i, title in enumerate(titles[:5], 1):
        results.append(str(i) + ". " + title.strip())
except Exception as e:
    results.append("知乎 Error: " + str(e))

with open("test_result.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(results))

print("Done")
