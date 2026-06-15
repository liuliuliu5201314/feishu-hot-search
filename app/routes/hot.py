from flask import Blueprint, jsonify, request
from ..services.bilibili_hot import BilibiliHotService
from ..services.weibo_hot import WeiboHotService
from ..services.zhihu_hot import ZhihuHotService

hot_bp = Blueprint("hot", __name__)
bilibili_hot = BilibiliHotService()
weibo_hot = WeiboHotService()
zhihu_hot = ZhihuHotService()


@hot_bp.route("/api/hot")
def api_hot():
    try:
        platform = request.args.get("platform", "bilibili")
        
        if platform == "weibo":
            items, error = weibo_hot.get_hot_list()
        elif platform == "zhihu":
            items, error = zhihu_hot.get_hot_list()
        else:
            items, error = bilibili_hot.get_hot_list()
        
        if error:
            return jsonify({"status": "error", "message": error})
        return jsonify({"status": "ok", "data": items})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
