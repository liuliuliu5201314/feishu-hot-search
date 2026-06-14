import requests
import json
import time
from datetime import datetime
from flask import Flask, jsonify, Response

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

def get_hot_searches():
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    weibo = []
    try:
        res = requests.get("https://weibo.com/ajax/side/hotSearch", headers=headers, timeout=10)
        data = res.json()
        for item in data.get("data", {}).get("realtime", [])[:10]:
            weibo.append(item.get("word", ""))
    except:
        weibo = ["获取失败"]
    
    zhihu = []
    try:
        res = requests.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10", headers=headers, timeout=10)
        data = res.json()
        for item in data.get("data", [])[:10]:
            target = item.get("target", {})
            zhihu.append(target.get("title", ""))
    except:
        zhihu = ["获取失败"]
    
    bilibili = []
    try:
        res = requests.get("https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all", headers=headers, timeout=10)
        data = res.json()
        for item in data.get("data", {}).get("list", [])[:10]:
            bilibili.append(item.get("title", ""))
    except:
        bilibili = ["获取失败"]
    
    return weibo, zhihu, bilibili

def build_card(weibo, zhihu, bilibili):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    weibo_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(weibo[:10])])
    zhihu_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(zhihu[:10])])
    bilibili_text = "\n".join([f"{i+1}. {item}" for i, item in enumerate(bilibili[:10])])
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
    weibo, zhihu, bilibili = get_hot_searches()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    weibo_html = "".join([f'<li>{i+1}. {item}</li>' for i, item in enumerate(weibo[:10])])
    zhihu_html = "".join([f'<li>{i+1}. {item}</li>' for i, item in enumerate(zhihu[:10])])
    bilibili_html = "".join([f'<li>{i+1}. {item}</li>' for i, item in enumerate(bilibili[:10])])
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>每日热搜</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px}}
.container{{max-width:1000px;margin:0 auto}}
h1{{text-align:center;color:#fff;margin-bottom:10px;font-size:28px}}
.time{{text-align:center;color:rgba(255,255,255,0.8);margin-bottom:20px}}
.cards{{display:grid;grid-template-columns:repeat(3,1fr);gap:20px}}
.card{{background:#fff;border-radius:12px;padding:20px;box-shadow:0 4px 20px rgba(0,0,0,0.1)}}
.card h2{{color:#333;margin-bottom:15px;font-size:18px;border-bottom:2px solid #667eea;padding-bottom:10px}}
.card ol{{padding-left:20px}}
.card li{{padding:8px 0;border-bottom:1px solid #f0f0f0;font-size:14px;color:#555}}
.card li:last-child{{border-bottom:none}}
.btn{{display:block;margin:30px auto 0;padding:12px 30px;background:#667eea;color:#fff;border:none;border-radius:25px;font-size:16px;cursor:pointer}}
.btn:hover{{background:#5a6fd6}}
@media(max-width:768px){{.cards{{grid-template-columns:1fr}}}}
</style>
</head>
<body>
<div class="container">
<h1>每日热搜</h1>
<p class="time">更新时间: {now}</p>
<div class="cards">
<div class="card">
<h2>微博热搜</h2>
<ol>{weibo_html}</ol>
</div>
<div class="card">
<h2>知乎热榜</h2>
<ol>{zhihu_html}</ol>
</div>
<div class="card">
<h2>哔哩哔哩热榜</h2>
<ol>{bilibili_html}</ol>
</div>
</div>
<button class="btn" onclick="location.reload()">刷新</button>
<button class="btn" onclick="push()">推送到飞书</button>
</div>
<script>
function push(){{
  fetch('/push').then(r=>r.json()).then(d=>alert(d.message)).catch(e=>alert('推送失败'));
}}
</script>
</body>
</html>"""
    return Response(html, content_type="text/html;charset=utf-8")

@app.route("/push")
def push():
    try:
        weibo, zhihu, bilibili = get_hot_searches()
        token = get_tenant_token()
        card = build_card(weibo, zhihu, bilibili)
        result = send_feishu_message(token, card)
        if result.get("code") == 0:
            return jsonify({"status": "ok", "message": "发送成功"})
        else:
            return jsonify({"status": "error", "message": result})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/hot")
def api_hot():
    weibo, zhihu, bilibili = get_hot_searches()
    return jsonify({"weibo": weibo, "zhihu": zhihu, "bilibili": bilibili})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
