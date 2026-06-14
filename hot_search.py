import requests
import json
from datetime import datetime

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"
CHAT_ID = "oc_e6c00175d7bf047de0f647d4c31db4f2"

def get_tenant_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def send_feishu_message(token, content):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"receive_id": CHAT_ID, "msg_type": "interactive", "content": json.dumps(content)}
    res = requests.post(url, headers=headers, params={"receive_id_type": "chat_id"}, json=data)
    return res.json()

def get_zhihu_hot():
    try:
        res = requests.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10", headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        items = []
        for i, item in enumerate(data.get("data", [])[:10], 1):
            target = item.get("target", {})
            title = target.get("title", "")
            url = f"https://www.zhihu.com/question/{target.get('id', '')}"
            items.append(f"{i}. {title}")
        return items
    except:
        return ["获取失败"]

def get_bilibili_hot():
    try:
        res = requests.get("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        items = []
        for i, item in enumerate(data.get("data", {}).get("list", [])[:10], 1):
            title = item.get("title", "")
            items.append(f"{i}. {title}")
        return items
    except:
        return ["获取失败"]

def get_weibo_hot():
    try:
        res = requests.get("https://weibo.com/ajax/side/hotSearch", headers={"User-Agent": "Mozilla/5.0"})
        data = res.json()
        items = []
        for i, item in enumerate(data.get("data", {}).get("realtime", [])[:10], 1):
            word = item.get("word", "")
            items.append(f"{i}. {word}")
        return items
    except:
        return ["获取失败"]

def build_card(zhihu, bilibili, weibo):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return {
        "header": {"title": {"tag": "plain_text", "content": f"🔥 每日热搜推送 - {now}"}, "template": "red"},
        "elements": [
            {"tag": "markdown", "content": f"**📰 知乎热榜**\n" + "\n".join(zhihu)},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**📺 哔哩哔哩热榜**\n" + "\n".join(bilibili)},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**🔥 微博热搜**\n" + "\n".join(weibo)},
        ]
    }

def main():
    print("正在获取热搜...")
    zhihu = get_zhihu_hot()
    bilibili = get_bilibili_hot()
    weibo = get_weibo_hot()
    
    print("正在发送到飞书...")
    token = get_tenant_token()
    card = build_card(zhihu, bilibili, weibo)
    result = send_feishu_message(token, card)
    
    if result.get("code") == 0:
        print("发送成功！")
    else:
        print(f"发送失败: {result}")

if __name__ == "__main__":
    main()
