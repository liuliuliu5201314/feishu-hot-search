from flask import Blueprint, jsonify, request
from ..services.bilibili_hot import BilibiliHotService
from ..services.weibo_hot import WeiboHotService
from ..services.zhihu_hot import ZhihuHotService
from ..services.zhihu_search_hot import ZhihuSearchHotService
from ..services.douyin_hot import DouyinHotService

hot_bp = Blueprint("hot", __name__)
bilibili_hot = BilibiliHotService()
weibo_hot = WeiboHotService()
zhihu_hot = ZhihuHotService()
zhihu_search_hot = ZhihuSearchHotService()
douyin_hot = DouyinHotService()


@hot_bp.route("/api/hot")
def api_hot():
    try:
        platform = request.args.get("platform", "bilibili")
        
        if platform == "weibo":
            items, error = weibo_hot.get_hot_list()
        elif platform == "zhihu":
            items, error = zhihu_hot.get_hot_list()
        elif platform == "zhihu_search":
            items, error = zhihu_search_hot.get_hot_list()
        elif platform == "douyin":
            items, error = douyin_hot.get_hot_list()
        else:
            items, error = bilibili_hot.get_hot_list()
        
        if error:
            return jsonify({"status": "error", "message": error})
        return jsonify({"status": "ok", "data": items})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
