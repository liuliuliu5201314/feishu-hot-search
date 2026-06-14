import requests

# 测试知乎
print("=== 知乎热榜 ===")
try:
    res = requests.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=5", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = res.json()
    for i, item in enumerate(data.get("data", [])[:5], 1):
        title = item.get("target", {}).get("title", "")
        print(f"{i}. {title}")
except Exception as e:
    print(f"失败: {e}")

# 测试B站
print("\n=== B站热榜 ===")
try:
    res = requests.get("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = res.json()
    for i, item in enumerate(data.get("data", {}).get("list", [])[:5], 1):
        title = item.get("title", "")
        print(f"{i}. {title}")
except Exception as e:
    print(f"失败: {e}")

# 测试微博
print("\n=== 微博热搜 ===")
try:
    res = requests.get("https://weibo.com/ajax/side/hotSearch", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    data = res.json()
    for i, item in enumerate(data.get("data", {}).get("realtime", [])[:5], 1):
        word = item.get("word", "")
        print(f"{i}. {word}")
except Exception as e:
    print(f"失败: {e}")
