from flask import Blueprint, request, jsonify
from ..services.feishu import FeishuService
from ..services.bilibili import BilibiliService
from ..services.minimax import MinimaxService

webhook_bp = Blueprint("webhook", __name__)

feishu = FeishuService()
bilibili = BilibiliService()
minimax = MinimaxService()

processed_events = set()


@webhook_bp.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})
    
    if "header" in data and data["header"].get("event_type") == "im.message.receive_v1":
        event_id = data["header"].get("event_id", "")
        
        if event_id in processed_events:
            return jsonify({"code": 0})
        processed_events.add(event_id)
        
        if len(processed_events) > 1000:
            processed_events.clear()
        
        event = data["event"]
        message = event.get("message", {})
        chat_id = message.get("chat_id", "")
        content = __import__("json").loads(message.get("content", "{}"))
        text = content.get("text", "")
        
        bvid = bilibili.extract_bvid(text)
        if bvid:
            token = feishu.get_token()
            result, error = bilibili.get_subtitle(bvid)
            
            if error:
                feishu.send_message(token, chat_id, f"提取失败: {error}")
            else:
                summary = minimax.summarize(result["subtitle"], "请总结这段字幕的核心观点，用简洁的中文回答，不超过100字")
                
                from datetime import datetime
                now = datetime.now()
                timestamp_ms = int(now.timestamp() * 1000)
                
                feishu.write_to_base(token, {
                    "视频标题": result["title"],
                    "BV号": bvid,
                    "字幕内容": result["subtitle"][:2000],
                    "抓取时间": timestamp_ms,
                    "创建时间": timestamp_ms,
                    "作者": result["author"],
                    "封面图": result["封面图"],
                    "简介": result["desc"],
                    "minimax总结": summary
                })
                
                feishu.send_message(token, chat_id, f"字幕提取完成\n视频: {result['title']}\n作者: {result['author']}\n\nAI总结:\n{summary}")
    
    return jsonify({"code": 0})
