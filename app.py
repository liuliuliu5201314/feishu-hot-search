import requests
import json
import re
from datetime import datetime
from flask import Flask, jsonify, Response, request

app = Flask(__name__)

APP_ID = "cli_aa913ad0d7389cb6"
APP_SECRET = "7JOAZJEanZMAweftGNorxc2QqhaahuBS"
CHAT_ID = "oc_e6c00175d7bf047de0f647d4c31db4f2"
APP_TOKEN = "O87ebAsOKaDlsQst6nccQp2InTd"
TABLE_ID = "tblsRVZOdBJQndkM"

def get_token():
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    res = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET})
    return res.json().get("tenant_access_token")

def resolve_short_url(url):
    try:
        res = requests.head(url, allow_redirects=True, timeout=5)
        return res.url
    except:
        return url

def extract_bvid(text):
    bvid_match = re.search(r"BV[a-zA-Z0-9]+", text)
    if bvid_match:
        return bvid_match.group()
    
    url_match = re.search(r"https?://[^\s]+", text)
    if url_match:
        url = url_match.group()
        if "b23.tv" in url or "bilibili.com" in url:
            full_url = resolve_short_url(url)
            bvid_match = re.search(r"BV[a-zA-Z0-9]+", full_url)
            if bvid_match:
                return bvid_match.group()
    return None

def get_bilibili_subtitle(bvid):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
    try:
        video_res = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=headers, timeout=10)
        video_data = video_res.json()
        if video_data["code"] != 0:
            return None, "视频不存在"
        
        cid = video_data["data"]["cid"]
        aid = video_data["data"]["aid"]
        title = video_data["data"]["title"]
        author = video_data["data"]["owner"]["name"]
        
        dm_res = requests.get(f"https://api.bilibili.com/x/v2/dm/view?aid={aid}&type=1&oid={cid}", headers=headers, timeout=10)
        dm_data = dm_res.json()
        
        subtitles = dm_data.get("data", {}).get("subtitle", {}).get("subtitles", [])
        if not subtitles:
            return {"title": title, "author": author, "subtitle": "该视频没有字幕", "hasSubtitle": False}, None
        
        sub = subtitles[0]
        for s in subtitles:
            if s["lan"] == "ai-zh":
                sub = s
                break
        
        sub_url = sub["subtitle_url"]
        if sub_url.startswith("//"):
            sub_url = "https:" + sub_url
        if sub_url.startswith("http://"):
            sub_url = sub_url.replace("http://", "https://")
        
        content_res = requests.get(sub_url, timeout=10)
        content_data = content_res.json()
        subtitle_text = "\n".join([line["content"] for line in content_data["body"]])
        
        return {
            "title": title,
            "author": author,
            "subtitle": subtitle_text,
            "hasSubtitle": True
        }, None
    except Exception as e:
        return None, str(e)

def write_to_base(token, bvid, title, subtitle):
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{APP_TOKEN}/tables/{TABLE_ID}/records"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "fields": {
            "视频标题": title,
            "BV号": bvid,
            "字幕内容": subtitle[:2000],
            "抓取时间": int(datetime.now().timestamp() * 1000)
        }
    }
    res = requests.post(url, headers=headers, json=data)
    return res.json()

def send_feishu_message(token, chat_id, content):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"receive_id": chat_id, "msg_type": "text", "content": json.dumps({"text": content})}
    res = requests.post(url, headers=headers, params={"receive_id_type": "chat_id"}, json=data)
    return res.json()

def build_subtitle_card(bvid, title, author, subtitle):
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    subtitle_preview = subtitle[:500] + "..." if len(subtitle) > 500 else subtitle
    return {
        "header": {"title": {"tag": "plain_text", "content": f"B站字幕提取 - {now}"}, "template": "blue"},
        "elements": [
            {"tag": "markdown", "content": f"**视频标题**: {title}\n**作者**: {author}\n**BV号**: {bvid}"},
            {"tag": "hr"},
            {"tag": "markdown", "content": f"**字幕内容**:\n{subtitle_preview}"},
        ]
    }

@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>B站字幕提取</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,sans-serif;background:linear-gradient(135deg,#00a1d6,#00609c);min-height:100vh;display:flex;justify-content:center;align-items:center;padding:20px}
.container{background:#fff;border-radius:16px;padding:40px;max-width:600px;width:100%;box-shadow:0 20px 60px rgba(0,0,0,0.3)}
h1{text-align:center;color:#00a1d6;margin-bottom:30px}
.input-group{display:flex;gap:10px;margin-bottom:20px}
input{flex:1;padding:12px;border:2px solid #ddd;border-radius:8px;font-size:16px}
input:focus{border-color:#00a1d6;outline:none}
button{padding:12px 24px;background:#00a1d6;color:#fff;border:none;border-radius:8px;font-size:16px;cursor:pointer}
button:hover{background:#0088c6}
.result{margin-top:20px;padding:20px;background:#f5f5f5;border-radius:8px;display:none}
.result h3{color:#333;margin-bottom:10px;font-size:16px}
.result pre{white-space:pre-wrap;word-break:break-all;font-size:14px;line-height:1.6;max-height:400px;overflow-y:auto;background:#fff;padding:15px;border-radius:8px}
.error{color:#e74c3c;text-align:center;margin-top:20px;display:none}
.loading{text-align:center;display:none;margin-top:20px;color:#666}
.btn-group{display:flex;gap:10px;margin-top:15px}
.btn{flex:1;padding:10px;background:#00a1d6;color:#fff;border:none;border-radius:8px;cursor:pointer}
.btn:hover{background:#0088c6}
.btn-secondary{background:#6c757d}
.btn-secondary:hover{background:#5a6268}
</style>
</head>
<body>
<div class="container">
<h1>B站字幕提取</h1>
<div class="input-group">
<input type="text" id="bvid" placeholder="输入BV号，如 BV1DQ7k6JE4P">
<button onclick="fetchSubtitle()">提取</button>
</div>
<div class="loading" id="loading">正在提取...</div>
<div class="error" id="error"></div>
<div class="result" id="result">
<h3 id="title"></h3>
<pre id="subtitle"></pre>
<div class="btn-group">
<button class="btn" onclick="pushToFeishu()">推送到飞书</button>
<button class="btn btn-secondary" onclick="saveToBase()">保存到表格</button>
</div>
</div>
</div>
<script>
var currentData = null;
async function fetchSubtitle() {
  var bvid = document.getElementById('bvid').value.trim();
  if (!bvid) { alert('请输入BV号'); return; }
  document.getElementById('loading').style.display = 'block';
  document.getElementById('error').style.display = 'none';
  document.getElementById('result').style.display = 'none';
  try {
    var res = await fetch('/api/subtitle?bvid=' + encodeURIComponent(bvid));
    var data = await res.json();
    if (data.error) { throw new Error(data.error); }
    currentData = data;
    document.getElementById('title').textContent = data.title + ' - ' + data.author;
    document.getElementById('subtitle').textContent = data.subtitle;
    document.getElementById('result').style.display = 'block';
  } catch (e) {
    document.getElementById('error').textContent = '错误: ' + e.message;
    document.getElementById('error').style.display = 'block';
  }
  document.getElementById('loading').style.display = 'none';
}
async function pushToFeishu() {
  if (!currentData) return;
  var bvid = document.getElementById('bvid').value.trim();
  var res = await fetch('/api/push', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({bvid:bvid, title:currentData.title, author:currentData.author, subtitle:currentData.subtitle})});
  var data = await res.json();
  alert(data.message);
}
async function saveToBase() {
  if (!currentData) return;
  var bvid = document.getElementById('bvid').value.trim();
  var res = await fetch('/api/save', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({bvid:bvid, title:currentData.title, subtitle:currentData.subtitle})});
  var data = await res.json();
  alert(data.message);
}
</script>
</body>
</html>"""
    return Response(html, content_type="text/html;charset=utf-8")

@app.route("/api/subtitle")
def api_subtitle():
    bvid = request.args.get("bvid", "")
    if not bvid:
        return jsonify({"error": "请提供 bvid 参数"})
    data, error = get_bilibili_subtitle(bvid)
    if error:
        return jsonify({"error": error})
    return jsonify(data)

@app.route("/api/push", methods=["POST"])
def api_push():
    try:
        data = request.json
        token = get_token()
        card = build_subtitle_card(data["bvid"], data["title"], data["author"], data["subtitle"])
        result = send_feishu_message(token, CHAT_ID, f"字幕提取完成\n视频: {data['title']}\n作者: {data['author']}\n\n字幕内容:\n{data['subtitle'][:1000]}")
        if result.get("code") == 0:
            return jsonify({"status": "ok", "message": "推送成功"})
        else:
            return jsonify({"status": "error", "message": str(result)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/save", methods=["POST"])
def api_save():
    try:
        data = request.json
        token = get_token()
        result = write_to_base(token, data["bvid"], data["title"], data["subtitle"])
        if result.get("code") == 0:
            return jsonify({"status": "ok", "message": "保存成功"})
        else:
            return jsonify({"status": "error", "message": str(result)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    if "header" in data and data["header"].get("event_type") == "im.message.receive_v1":
        event = data["event"]
        message = event.get("message", {})
        chat_id = message.get("chat_id", "")
        content = json.loads(message.get("content", "{}"))
        text = content.get("text", "")
        
        bvid = extract_bvid(text)
        if bvid:
            token = get_token()
            result, error = get_bilibili_subtitle(bvid)
            if error:
                send_feishu_message(token, chat_id, f"提取失败: {error}")
            else:
                send_feishu_message(token, chat_id, f"字幕提取完成\n视频: {result['title']}\n作者: {result['author']}\n\n字幕内容:\n{result['subtitle'][:1000]}")
                write_to_base(token, bvid, result["title"], result["subtitle"])
    
    return jsonify({"code": 0})

@app.route("/api/hot")
def api_hot():
    return jsonify({"status": "ok", "message": "热搜功能已禁用"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
