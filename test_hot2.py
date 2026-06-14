import requests

# 测试B站
print("=== B站热榜 ===")
try:
    res = requests.get("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print("Status:", res.status_code)
    data = res.json()
    for i, item in enumerate(data.get("data", {}).get("list", [])[:5], 1):
        title = item.get("title", "")
        print(str(i) + ". " + title)
except Exception as e:
    print("Error:", e)

# 测试微博
print("\n=== 微博热搜 ===")
try:
    res = requests.get("https://weibo.com/ajax/side/hotSearch", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    print("Status:", res.status_code)
    data = res.json()
    for i, item in enumerate(data.get("data", {}).get("realtime", [])[:5], 1):
        word = item.get("word", "")
        print(str(i) + ". " + word)
except Exception as e:
    print("Error:", e)
