from flask import Blueprint, jsonify
from ..services.bilibili_hot import BilibiliHotService

hot_bp = Blueprint("hot", __name__)
bilibili_hot = BilibiliHotService()


@hot_bp.route("/api/hot")
def api_hot():
    try:
        items, error = bilibili_hot.get_hot_list()
        if error:
            return jsonify({"status": "error", "message": error})
        return jsonify({"status": "ok", "data": items})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
