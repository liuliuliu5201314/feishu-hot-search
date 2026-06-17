import threading
import time

from flask import Blueprint, jsonify, request

from ..config import Config
from ..services.xinzhi import XinzhiService
from ..services.xinzhi_sync import XinzhiSyncService

xinzhi_bp = Blueprint("xinzhi", __name__)
xinzhi_service = XinzhiService()
sync_service = XinzhiSyncService()

_poller_started = False
_poller_lock = threading.Lock()


def _poll_loop():
    while True:
        try:
            ready, _ = xinzhi_service.account_ready()
            if ready:
                sync_service.sync_once()
        except Exception:
            pass
        time.sleep(Config.XINZHI_SYNC_INTERVAL)


def start_xinzhi_poller(app):
    global _poller_started
    if not Config.XINZHI_POLL_ENABLED:
        return

    with _poller_lock:
        if _poller_started:
            return
        _poller_started = True

    def run():
        with app.app_context():
            _poll_loop()

    thread = threading.Thread(target=run, name="xinzhi-poller", daemon=True)
    thread.start()


@xinzhi_bp.route("/api/xinzhi/bind", methods=["POST"])
def api_xinzhi_bind():
    try:
        session_id = xinzhi_service.get_session_id()
        return jsonify({"status": "ok", "sessionId": session_id})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@xinzhi_bp.route("/api/xinzhi/bind/status")
def api_xinzhi_bind_status():
    session_id = request.args.get("sessionId", "")
    if not session_id:
        return jsonify({"status": "error", "message": "缺少 sessionId"}), 400

    try:
        login_status = xinzhi_service.get_login_status(session_id)
        if login_status.get("invalidSessionId"):
            return jsonify({"status": "ok", "bound": False, "expired": True})

        if login_status.get("status") and login_status.get("token"):
            xinzhi_service.save_auth(
                {
                    "token": login_status["token"],
                    "sessionId": session_id,
                    "user": {
                        "id": login_status.get("id"),
                        "name": login_status.get("name") or "新枝用户",
                    },
                }
            )
            return jsonify(
                {
                    "status": "ok",
                    "bound": True,
                    "user": login_status.get("name") or "新枝用户",
                }
            )

        return jsonify({"status": "ok", "bound": False, "expired": False})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@xinzhi_bp.route("/api/xinzhi/account")
def api_xinzhi_account():
    ready, auth = xinzhi_service.account_ready()
    if not ready:
        return jsonify({"status": "ok", "bound": False})
    return jsonify(
        {
            "status": "ok",
            "bound": True,
            "user": (auth.get("user") or {}).get("name", "新枝用户"),
        }
    )


@xinzhi_bp.route("/api/xinzhi/unbind", methods=["POST"])
def api_xinzhi_unbind():
    auth = xinzhi_service.load_auth() or {}
    token = auth.get("token")
    if token:
        try:
            xinzhi_service.unbind(token)
        except Exception:
            pass
    xinzhi_service.clear_auth()
    return jsonify({"status": "ok", "message": "已解绑新枝账号"})


@xinzhi_bp.route("/api/xinzhi/sync", methods=["GET", "POST"])
def api_xinzhi_sync():
    try:
        result = sync_service.sync_once()
        code = 200 if result.get("status") == "ok" else 400
        return jsonify(result), code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500
