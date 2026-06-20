import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

from ..config import Config
from .feishu import FeishuService

CN_TZ = timezone(timedelta(hours=8))
SOURCE_FIELD = "文本"
REWRITE_FIELD = "改写标题"
CONTENT_FIELD = "内容改编"
TITLE_PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "mrhlw_zhihu_title.txt"
CONTENT_PROMPT_FILE = Path(__file__).resolve().parents[1] / "prompts" / "mrhlw_zhihu_content.txt"
PROMPT_FILE = TITLE_PROMPT_FILE


class MrhlwTitleRewriteService:
    def __init__(self):
        self.feishu = FeishuService()
        self.base_token = Config.MRHLW_BASE_TOKEN
        self.table_id = Config.MRHLW_TABLE_ID

    def _records_url(self):
        return (
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.base_token}/tables/{self.table_id}/records"
        )

    def _fields_url(self):
        return (
            f"https://open.feishu.cn/open-apis/bitable/v1/apps/"
            f"{self.base_token}/tables/{self.table_id}/fields"
        )

    def _auth_headers(self, token):
        return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    def _field_text(self, value):
        if isinstance(value, dict):
            return value.get("link") or value.get("text") or ""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item)
        return str(value or "").strip()

    def get_prompt_template(self):
        return PROMPT_FILE.read_text(encoding="utf-8")

    def format_prompt(self, title):
        return self.get_prompt_template().format(title=title.strip())

    def get_content_prompt_template(self):
        return CONTENT_PROMPT_FILE.read_text(encoding="utf-8")

    def format_content_prompt(self, title, rewrite_title="", categories=""):
        return self.get_content_prompt_template().format(
            title=title.strip(),
            rewrite_title=(rewrite_title or title).strip(),
            categories=(categories or "未分类").strip(),
        )

    def _ensure_field(self, token, field_name):
        headers = self._auth_headers(token)
        response = requests.get(self._fields_url(), headers=headers, timeout=20)
        payload = response.json()
        if payload.get("code") != 0:
            return payload

        existing = {item.get("field_name") for item in payload.get("data", {}).get("items", [])}
        if field_name in existing:
            return {"code": 0, "created": False}

        result = requests.post(
            self._fields_url(),
            headers=headers,
            json={"field_name": field_name, "type": 1},
            timeout=20,
        ).json()
        if result.get("code") != 0:
            return result
        return {"code": 0, "created": True, "result": result}

    def ensure_rewrite_field(self, token):
        return self._ensure_field(token, REWRITE_FIELD)

    def ensure_content_field(self, token):
        return self._ensure_field(token, CONTENT_FIELD)

    def _iter_records(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        page_token = None
        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
            response = requests.get(self._records_url(), headers=headers, params=params, timeout=20)
            payload = response.json()
            if payload.get("code") != 0:
                return payload
            for item in payload.get("data", {}).get("items", []):
                yield item
            if not payload.get("data", {}).get("has_more"):
                break
            page_token = payload.get("data", {}).get("page_token")

    def list_pending(self, limit=50, only_empty=True):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败", "items": []}

        ensure = self.ensure_rewrite_field(token)
        if ensure.get("code") != 0:
            return {"status": "error", "message": f"初始化字段失败: {ensure}", "items": []}

        pending = []
        for record in self._iter_records(token):
            fields = record.get("fields", {})
            title = self._field_text(fields.get(SOURCE_FIELD))
            if not title:
                continue
            rewrite = self._field_text(fields.get(REWRITE_FIELD))
            if only_empty and rewrite:
                continue
            pending.append(
                {
                    "record_id": record.get("record_id"),
                    "title": title,
                    "rewrite_title": rewrite,
                    "link": self._field_text(fields.get("原文链接")),
                    "author": self._field_text(fields.get("作者")),
                    "categories": self._field_text(fields.get("分类")),
                    "prompt": self.format_prompt(title),
                }
            )
            if limit and len(pending) >= limit:
                break

        return {
            "status": "ok",
            "count": len(pending),
            "rewrite_field": REWRITE_FIELD,
            "source_field": SOURCE_FIELD,
            "prompt_file": "app/prompts/mrhlw_zhihu_title.txt",
            "items": pending,
        }

    def apply_rewrites(self, items):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败"}

        ensure = self.ensure_rewrite_field(token)
        if ensure.get("code") != 0:
            return {"status": "error", "message": f"初始化字段失败: {ensure}"}

        updated = []
        failed = []
        headers = self._auth_headers(token)
        for item in items:
            record_id = (item.get("record_id") or "").strip()
            rewrite_title = (item.get("rewrite_title") or item.get(REWRITE_FIELD) or "").strip()
            if not record_id or not rewrite_title:
                failed.append({"item": item, "error": "缺少 record_id 或 rewrite_title"})
                continue
            url = f"{self._records_url()}/{record_id}"
            result = requests.put(
                url,
                headers=headers,
                json={"fields": {REWRITE_FIELD: rewrite_title}},
                timeout=20,
            ).json()
            if result.get("code") == 0:
                updated.append(
                    {
                        "record_id": record_id,
                        "rewrite_title": rewrite_title,
                    }
                )
            else:
                failed.append(
                    {
                        "record_id": record_id,
                        "rewrite_title": rewrite_title,
                        "error": result.get("msg") or json.dumps(result, ensure_ascii=False),
                    }
                )

        return {
            "status": "ok" if not failed else "partial",
            "message": f"成功 {len(updated)} 条，失败 {len(failed)} 条",
            "updated_count": len(updated),
            "failed_count": len(failed),
            "updated": updated,
            "failed": failed,
        }

    def list_pending_content(self, limit=50, only_empty=True):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败", "items": []}

        ensure = self.ensure_content_field(token)
        if ensure.get("code") != 0:
            return {"status": "error", "message": f"初始化字段失败: {ensure}", "items": []}

        pending = []
        for record in self._iter_records(token):
            fields = record.get("fields", {})
            title = self._field_text(fields.get(SOURCE_FIELD))
            if not title:
                continue
            content = self._field_text(fields.get(CONTENT_FIELD))
            if only_empty and content:
                continue
            rewrite_title = self._field_text(fields.get(REWRITE_FIELD))
            categories = self._field_text(fields.get("分类"))
            pending.append(
                {
                    "record_id": record.get("record_id"),
                    "title": title,
                    "rewrite_title": rewrite_title,
                    "link": self._field_text(fields.get("原文链接")),
                    "author": self._field_text(fields.get("作者")),
                    "categories": categories,
                    "prompt": self.format_content_prompt(title, rewrite_title, categories),
                }
            )
            if limit and len(pending) >= limit:
                break

        return {
            "status": "ok",
            "count": len(pending),
            "content_field": CONTENT_FIELD,
            "prompt_file": "app/prompts/mrhlw_zhihu_content.txt",
            "items": pending,
        }

    def apply_content(self, items):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败"}

        ensure = self.ensure_content_field(token)
        if ensure.get("code") != 0:
            return {"status": "error", "message": f"初始化字段失败: {ensure}"}

        updated = []
        failed = []
        headers = self._auth_headers(token)
        for item in items:
            record_id = (item.get("record_id") or "").strip()
            content = (
                item.get("content")
                or item.get("rewrite_content")
                or item.get(CONTENT_FIELD)
                or ""
            ).strip()
            if not record_id or not content:
                failed.append({"item": item, "error": "缺少 record_id 或 content"})
                continue
            url = f"{self._records_url()}/{record_id}"
            result = requests.put(
                url,
                headers=headers,
                json={"fields": {CONTENT_FIELD: content}},
                timeout=20,
            ).json()
            if result.get("code") == 0:
                updated.append({"record_id": record_id, "content_length": len(content)})
            else:
                failed.append(
                    {
                        "record_id": record_id,
                        "error": result.get("msg") or json.dumps(result, ensure_ascii=False),
                    }
                )

        return {
            "status": "ok" if not failed else "partial",
            "message": f"成功 {len(updated)} 条，失败 {len(failed)} 条",
            "updated_count": len(updated),
            "failed_count": len(failed),
            "updated": updated,
            "failed": failed,
        }
