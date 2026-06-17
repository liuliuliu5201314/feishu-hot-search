import json
import os
import time

import jwt
import requests

from ..config import Config

API_BASE = "https://api.xinzhi.zone/api/integration/obsidian"
SUCCESS_CODE = 1001


class XinzhiService:
    def __init__(self):
        self.auth_file = Config.XINZHI_AUTH_FILE
        self._ensure_auth_dir()

    def _ensure_auth_dir(self):
        auth_dir = os.path.dirname(self.auth_file)
        if auth_dir:
            os.makedirs(auth_dir, exist_ok=True)

    def _headers(self, token=None):
        headers = {"Content-Type": "application/json", "X-Client": "Obsidian"}
        if token:
            headers["X-Obsidian-Token"] = token
        return headers

    def _request(self, method, path, token=None, body=None):
        res = requests.request(
            method,
            f"{API_BASE}{path}",
            headers=self._headers(token),
            json=body,
            timeout=30,
        )
        res.raise_for_status()
        payload = res.json()
        if payload.get("code") != SUCCESS_CODE:
            raise RuntimeError(f"新枝 API 错误: {payload}")
        return payload.get("data")

    def load_auth(self):
        if Config.XINZHI_TOKEN and Config.XINZHI_SESSION_ID:
            return {
                "token": Config.XINZHI_TOKEN,
                "sessionId": Config.XINZHI_SESSION_ID,
                "user": {"name": Config.XINZHI_USER},
            }
        if not os.path.exists(self.auth_file):
            return None
        with open(self.auth_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_auth(self, data):
        self._ensure_auth_dir()
        with open(self.auth_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def clear_auth(self):
        if os.path.exists(self.auth_file):
            os.remove(self.auth_file)

    def token_valid(self, token):
        if not token:
            return False
        try:
            decoded = jwt.decode(token, options={"verify_signature": False})
            return time.time() < decoded.get("exp", 0)
        except Exception:
            return False

    def get_session_id(self):
        data = self._request("GET", "/session-id")
        return data.get("sessionId")

    def get_login_status(self, session_id):
        return self._request("GET", f"/login-status?sessionId={session_id}")

    def get_integration(self, session_id, token):
        return self._request("GET", f"/integration?sessionId={session_id}", token=token)

    def get_sync_tasks(self, token):
        return self._request("GET", "/sync-task", token=token)

    def get_sync_content(self, task_id, token):
        res = requests.request(
            "GET",
            f"{API_BASE}/sync-content?id={task_id}",
            headers=self._headers(token),
            timeout=30,
        )
        res.raise_for_status()
        payload = res.json()
        if payload.get("code") == 5000:
            return None
        if payload.get("code") != SUCCESS_CODE:
            raise RuntimeError(f"新枝 API 错误: {payload}")
        return payload.get("data")

    def mark_sync_success(self, task_id, token):
        self._request("PUT", "/sync-success", token=token, body={"id": task_id})

    def mark_sync_failed(self, task_id, token, error):
        self._request("PUT", "/sync-failed", token=token, body={"id": task_id, "error": error})

    def unbind(self, token):
        self._request("DELETE", "/unbind", token=token)

    def retry_failed(self, token):
        self._request("PUT", "/retry", token=token)

    def account_ready(self):
        auth = self.load_auth() or {}
        token = auth.get("token")
        session_id = auth.get("sessionId")
        if not self.token_valid(token) or not session_id:
            return False, auth
        try:
            integration = self.get_integration(session_id, token)
            return bool(integration.get("valid")), auth
        except Exception:
            return False, auth
