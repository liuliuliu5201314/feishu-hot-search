import requests
import re
from datetime import datetime
from flask import Flask, jsonify

app = Flask(__name__)

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

def get_tophub_data():
    try:
        res = requests.get("https://tophub.today/", headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}, timeout=15)
        html = res.text
        
        weibo = []
        zhihu = []
        bilibili = []
        
        weibo_pattern = re.findall(r'<a href="https://s\.weibo\.com[^"]*"[^>]*>\s*<span[^>]*>\d+</span>\s*<span[^>]*>(.*?)</span>', html)
        for item in weibo_pattern[:10]:
            weibo.append(item.strip())
        
        zhihu_pattern = re.findall(r'<a href="https://www\.zhihu\.com/question[^"]*"[^>]*>\s*<span[^>]*>\d+</span>\s*<span[^>]*>(.*?)</span>', html)
        for item in zhihu_pattern[:10]:
            zhihu.append(item.strip())
        
        bilibili_pattern = re.findall(r'<a href="https://www\.bilibili\.com/video[^"]*"[^>]*>\s*<span[^>]*>\d+</span>\s*<span[^>]*>(.*?)</span>', html)
        for item in bilibili_pattern[:10]:
            bilibili.append(item.strip())
        
        return weibo, zhihu, bilibili
    except Exception as e:
        return [], [], []

def build_card(weibo, zhihu, bilibili):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    weibo_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(weibo[:10])]) if weibo else "获取失败"
    zhihu_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(zhihu[:10])]) if zhihu else "获取失败"
    bilibili_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(bilibili[:10])]) if bilibili else "获取失败"
    
    return {
        "header": {"title": {"tag": "plain_text", "content": f"每日热搜推送 - {now}"}, "template": "red"},
        "elements": [
            {"tag": "markdown", "content": f"**微博热搜**\n{weibo_text}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**知乎热榜**\n{zhihu_text}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**哔哩哔哩热榜**\n{bilibili_text}"},
        ]
    }

@app.route("/")
def index():
    return jsonify({"status": "ok", "message": "热搜推送服务运行中"})

@app.route("/push")
def push():
    try:
        weibo, zhihu, bilibili = get_tophub_data()
        token = get_tenant_token()
        card = build_card(weibo, zhihu, bilibili)
        result = send_feishu_message(token, card)
        if result.get("code") == 0:
            return jsonify({"status": "ok", "message": "发送成功"})
        else:
            return jsonify({"status": "error", "message": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
