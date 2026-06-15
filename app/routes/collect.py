from flask import Blueprint, jsonify
from ..services.bilibili_hot import BilibiliHotService
from ..services.weibo_hot import WeiboHotService
from ..services.zhihu_hot import ZhihuHotService
from ..services.hot_search import HotSearchService

collect_bp = Blueprint("collect", __name__)
bilibili_hot = BilibiliHotService()
weibo_hot = WeiboHotService()
zhihu_hot = ZhihuHotService()
hot_search = HotSearchService()


@collect_bp.route("/api/collect-hot")
def api_collect_hot():
    try:
        bilibili_items, _ = bilibili_hot.get_hot_list()
        weibo_items, _ = weibo_hot.get_hot_list()
        zhihu_items, _ = zhihu_hot.get_hot_list()
        
        result = hot_search.write_hot_data(bilibili_items, weibo_items, zhihu_items)
        
        if result.get("code") == 0:
            return jsonify({"status": "ok", "message": "热搜数据采集完成"})
        else:
            return jsonify({"status": "error", "message": str(result)})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
