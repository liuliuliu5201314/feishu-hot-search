import threading
import time
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request

from ..config import Config
from ..services.mrhlw_sync import MrhlwSyncService

mrhlw_bp = Blueprint("mrhlw", __name__)
sync_service = MrhlwSyncService()

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
                sync_service.sync_once()
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


@mrhlw_bp.route("/api/mrhlw/articles")
def api_mrhlw_articles():
    try:
        date_text = request.args.get("date")
        target_date = None
        if date_text:
            target_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        result = sync_service.get_daily_overview(target_date)
        code = 200 if result.get("status") == "ok" else 400
        return jsonify(result), code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@mrhlw_bp.route("/api/mrhlw/sync", methods=["GET", "POST"])
def api_mrhlw_sync():
    try:
        date_text = request.args.get("date") or (request.json or {}).get("date")
        target_date = None
        if date_text:
            target_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        result = sync_service.sync_once(target_date)
        code = 200 if result.get("status") == "ok" else 400
        return jsonify(result), code
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500
