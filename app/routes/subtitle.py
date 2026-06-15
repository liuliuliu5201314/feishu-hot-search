from flask import Blueprint, request, jsonify
from ..services.feishu import FeishuService
from ..services.bilibili import BilibiliService
from ..services.minimax import MinimaxService
from datetime import datetime

subtitle_bp = Blueprint("subtitle", __name__)

feishu = FeishuService()
bilibili = BilibiliService()
minimax = MinimaxService()


@subtitle_bp.route("/api/subtitle")
def api_subtitle():
    bvid = request.args.get("bvid", "")
    if not bvid:
        return jsonify({"error": "请提供 bvid 参数"})
    data, error = bilibili.get_subtitle(bvid)
    if error:
        return jsonify({"error": error})
    return jsonify(data)


@subtitle_bp.route("/api/push", methods=["POST"])
def api_push():
    try:
        data = request.json
        token = feishu.get_token()
        feishu.send_message(token, f"字幕提取完成\n视频: {data['title']}\n作者: {data['author']}\n\n字幕内容:\n{data['subtitle'][:1000]}")
        return jsonify({"status": "ok", "message": "推送成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@subtitle_bp.route("/api/save", methods=["POST"])
def api_save():
    try:
        data = request.json
        token = feishu.get_token()
        
        now = datetime.now()
        timestamp_ms = int(now.timestamp() * 1000)
        
        feishu.write_to_base(token, {
            "视频标题": data["title"],
            "BV号": data["bvid"],
            "字幕内容": data["subtitle"][:2000],
            "抓取时间": timestamp_ms,
            "创建时间": timestamp_ms,
            "作者": data.get("author", ""),
            "封面图": data.get("cover", ""),
            "简介": data.get("desc", ""),
            "minimax总结": data.get("summary", "")
        })
        return jsonify({"status": "ok", "message": "保存成功"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@subtitle_bp.route("/api/summarize", methods=["POST"])
def api_summarize():
    try:
        data = request.json
        subtitle = data.get("subtitle", "")
        prompt = data.get("prompt", "请总结这段字幕的核心观点")
        
        summary = minimax.summarize(subtitle, prompt)
        
        token = feishu.get_token()
        records = feishu.get_base_records(token, f'CurrentValue.[BV号] = "{data.get("bvid", "")}"')
        
        if records.get("data", {}).get("items"):
            record_id = records["data"]["items"][0]["record_id"]
            feishu.update_base_record(token, record_id, {"minimax总结": summary})
        
        return jsonify({"status": "ok", "summary": summary})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@subtitle_bp.route("/api/collect")
def api_collect():
    try:
        token = feishu.get_token()
        bvids = ["BV1DQ7k6JE4P", "BV1oDVv6wENJ"]
        
        for bvid in bvids:
            result, error = bilibili.get_subtitle(bvid)
            if not error and result:
                summary = minimax.summarize(result["subtitle"], "请总结这段字幕的核心观点，用简洁的中文回答，不超过100字")
                
                now = datetime.now()
                timestamp_ms = int(now.timestamp() * 1000)
                
                feishu.write_to_base(token, {
                    "视频标题": result["title"],
                    "BV号": bvid,
                    "字幕内容": result["subtitle"][:2000],
                    "抓取时间": timestamp_ms,
                    "创建时间": timestamp_ms,
                    "作者": result["author"],
                    "封面图": result["cover"],
                    "简介": result["desc"],
                    "minimax总结": summary
                })
                
                feishu.send_message(token, f"定时采集完成\n视频: {result['title']}\n作者: {result['author']}")
        
        return jsonify({"status": "ok", "message": f"采集完成，共{len(bvids)}个视频"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
