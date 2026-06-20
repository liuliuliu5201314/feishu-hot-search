import json
from pathlib import Path

import requests

from ..config import Config
from .feishu import FeishuService

COVER_FIELD = "生成的封面图"


class MrhlwCoverService:
    def __init__(self):
        self.feishu = FeishuService()
        self.base_token = Config.MRHLW_BASE_TOKEN
        self.table_id = Config.MRHLW_TABLE_ID

    def _fields_url(self):
        return (
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.base_token}/tables/{self.table_id}/fields"
        )

    def _records_url(self):
        return (
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.base_token}/tables/{self.table_id}/records"
        )

    def _auth_headers(self, token):
        return {"Authorization": f"Bearer {token}"}

    def ensure_cover_field(self, token):
        headers = self._auth_headers(token)
        payload = requests.get(self._fields_url(), headers=headers, timeout=20).json()
        if payload.get("code") != 0:
            return payload

        existing = {item.get("field_name") for item in payload.get("data", {}).get("items", [])}
        if COVER_FIELD in existing:
            return {"code": 0, "created": False}

        result = requests.post(
            self._fields_url(),
            headers={**headers, "Content-Type": "application/json"},
            json={"field_name": COVER_FIELD, "type": 17},
            timeout=20,
        ).json()
        if result.get("code") != 0:
            return result
        return {"code": 0, "created": True, "result": result}

    def upload_image(self, token, image_path):
        path = Path(image_path)
        if not path.exists():
            return {"code": -1, "msg": f"文件不存在: {path}"}

        size = path.stat().st_size
        upload_url = "https://open.feishu.cn/open-apis/drive/v1/medias/upload_all"
        headers = self._auth_headers(token)
        with path.open("rb") as handle:
            response = requests.post(
                upload_url,
                headers=headers,
                data={
                    "file_name": path.name,
                    "parent_type": "bitable_image",
                    "parent_node": self.base_token,
                    "size": str(size),
                },
                files={"file": (path.name, handle, "image/png")},
                timeout=60,
            )
        payload = response.json()
        if payload.get("code") != 0:
            return payload
        return {"code": 0, "file_token": payload.get("data", {}).get("file_token")}

    def attach_cover(self, record_id, image_path):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败"}

        ensure = self.ensure_cover_field(token)
        if ensure.get("code") != 0:
            return {"status": "error", "message": f"初始化字段失败: {ensure}"}

        upload = self.upload_image(token, image_path)
        if upload.get("code") != 0:
            return {"status": "error", "message": f"上传图片失败: {upload}"}

        file_token = upload.get("file_token")
        url = f"{self._records_url()}/{record_id}"
        result = requests.put(
            url,
            headers={**self._auth_headers(token), "Content-Type": "application/json"},
            json={"fields": {COVER_FIELD: [{"file_token": file_token}]}},
            timeout=20,
        ).json()
        if result.get("code") != 0:
            return {"status": "error", "message": result.get("msg") or json.dumps(result, ensure_ascii=False)}

        return {
            "status": "ok",
            "record_id": record_id,
            "field": COVER_FIELD,
            "file_token": file_token,
            "local_path": str(image_path),
        }
