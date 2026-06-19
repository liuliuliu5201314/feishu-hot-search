import threading
import time
from datetime import datetime, timedelta, timezone

from flask import Blueprint, Response, jsonify, request

from ..config import Config
from ..services.mrhlw import MrhlwService
from ..services.mrhlw_sync import MrhlwSyncService

mrhlw_bp = Blueprint("mrhlw", __name__)
sync_service = MrhlwSyncService()
mrhlw_service = MrhlwService()

_scheduler_started = False
_scheduler_lock = threading.Lock()
_last_run_date = None

CN_TZ = timezone(timedelta(hours=8))


def _should_run_now(now=None):
    now = now or datetime.now(CN_TZ)
    return now.hour == Config.MRHLW_SYNC_HOUR and now.minute < Config.MRHLW_SYNC_WINDOW_MINUTES


def _scheduler_loop():
    global _last_run_date
    while True:
        try:
            now = datetime.now(CN_TZ)
            today = now.date()
            if _should_run_now(now) and _last_run_date != today:
                sync_service.sync_once(
                    base_url=Config.PUBLIC_BASE_URL.rstrip("/") if Config.PUBLIC_BASE_URL else ""
                )
                _last_run_date = today
        except Exception:
            pass
        time.sleep(60)


def start_mrhlw_scheduler(app):
    global _scheduler_started
    if not Config.MRHLW_SCHEDULER_ENABLED:
        return

    with _scheduler_lock:
        if _scheduler_started:
            return
        _scheduler_started = True

    def run():
        with app.app_context():
            _scheduler_loop()

    thread = threading.Thread(target=run, name="mrhlw-scheduler", daemon=True)
    thread.start()


def _request_base_url():
    if Config.PUBLIC_BASE_URL:
        return Config.PUBLIC_BASE_URL.rstrip("/")
    return request.host_url.rstrip("/")


@mrhlw_bp.route("/api/mrhlw/cover")
def api_mrhlw_cover():
    cover_url = request.args.get("url", "").strip()
    if not cover_url:
        return jsonify({"status": "error", "message": "缺少 url 参数"}), 400
    try:
        data, mime = mrhlw_service.fetch_decrypted_image(cover_url)
        return Response(
            data,
            mimetype=mime,
            headers={"Cache-Control": "public, max-age=86400"},
        )
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 502


@mrhlw_bp.route("/api/mrhlw/articles")
def api_mrhlw_articles():
    try:
        date_text = request.args.get("date")
        target_date = None
        if date_text:
            target_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        result = sync_service.get_daily_overview(target_date, base_url=_request_base_url())
        code = 200 if result.get("status") == "ok" else 400
        return jsonify(result), code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@mrhlw_bp.route("/api/mrhlw/sync", methods=["GET", "POST"])
def api_mrhlw_sync():
    try:
        payload = request.get_json(silent=True) or {}
        date_text = request.args.get("date") or payload.get("date")
        target_date = None
        if date_text:
            target_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        result = sync_service.sync_once(
            target_date,
            base_url=Config.PUBLIC_BASE_URL.rstrip("/") if Config.PUBLIC_BASE_URL else "",
        )
        code = 200 if result.get("status") == "ok" else 400
        return jsonify(result), code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500
