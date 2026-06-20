import json
from datetime import datetime, timedelta, timezone

import requests

from ..config import Config
from .feishu import FeishuService
from .mrhlw import CN_TZ, MrhlwService

REQUIRED_FIELDS = [
    ("封面图", 1),
    ("原文链接", 1),
    ("发布日期", 5),
    ("作者", 1),
    ("分类", 1),
    ("采集时间", 5),
    ("来源", 1),
    ("改写标题", 1),
    ("内容改编", 1),
    ("生成的封面图", 17),
]


class MrhlwSyncService:
    def __init__(self):
        self.mrhlw = MrhlwService()
        self.feishu = FeishuService()
        self.base_token = Config.MRHLW_BASE_TOKEN
        self.table_id = Config.MRHLW_TABLE_ID

    def _cover_for_storage(self, cover_url, base_url=""):
        return MrhlwService.build_cover_proxy_url(cover_url, base_url)

    def _normalize_item_covers(self, items, base_url=""):
        normalized = []
        for item in items:
            current = dict(item)
            cover = current.get("cover") or ""
            current["cover_raw"] = cover
            current["cover"] = self._cover_for_storage(cover, base_url)
            normalized.append(current)
        return normalized

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

    def _date_to_ms(self, value):
        if isinstance(value, datetime):
            dt = value
        else:
            dt = datetime(value.year, value.month, value.day, tzinfo=CN_TZ)
        return int(dt.timestamp() * 1000)

    def _now_ms(self):
        return int(datetime.now(CN_TZ).timestamp() * 1000)

    def ensure_table_fields(self, token):
        headers = self._auth_headers(token)
        response = requests.get(self._fields_url(), headers=headers, timeout=20)
        payload = response.json()
        if payload.get("code") != 0:
            return payload

        existing = {item.get("field_name") for item in payload.get("data", {}).get("items", [])}
        created = []
        for field_name, field_type in REQUIRED_FIELDS:
            if field_name in existing:
                continue
            body = {"field_name": field_name, "type": field_type}
            if field_type == 5:
                body["property"] = {"date_formatter": "yyyy/MM/dd"}
            result = requests.post(self._fields_url(), headers=headers, json=body, timeout=20)
            created.append({"field": field_name, "result": result.json()})
        return {"code": 0, "created": created}

    def _load_existing_links(self, token):
        headers = {"Authorization": f"Bearer {token}"}
        links = set()
        page_token = None
        while True:
            params = {"page_size": 500}
            if page_token:
                params["page_token"] = page_token
            response = requests.get(self._records_url(), headers=headers, params=params, timeout=20)
            payload = response.json()
            if payload.get("code") != 0:
                break
            for item in payload.get("data", {}).get("items", []):
                fields = item.get("fields", {})
                link = fields.get("原文链接") or fields.get("链接") or ""
                if isinstance(link, dict):
                    link = link.get("link") or link.get("text") or ""
                if link:
                    links.add(str(link).rstrip("/") + "/")
            if not payload.get("data", {}).get("has_more"):
                break
            page_token = payload.get("data", {}).get("page_token")
        return links

    def _write_record(self, token, fields):
        response = requests.post(
            self._records_url(),
            headers=self._auth_headers(token),
            json={"fields": fields},
            timeout=20,
        )
        return response.json()

    def _field_text(self, value):
        if isinstance(value, dict):
            return value.get("link") or value.get("text") or ""
        if isinstance(value, list):
            return ", ".join(str(item) for item in value if item)
        return str(value or "")

    def list_records_by_date(self, target_date=None):
        target_date = target_date or datetime.now(CN_TZ).date()
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败", "items": []}

        day_start = int(
            datetime(target_date.year, target_date.month, target_date.day, tzinfo=CN_TZ).timestamp()
            * 1000
        )
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        body = {
            "filter": {
                "conjunction": "and",
                "conditions": [
                    {
                        "field_name": "发布日期",
                        "operator": "is",
                        "value": ["ExactDate", str(day_start)],
                    }
                ],
            },
            "page_size": 500,
        }
        response = requests.post(
            f"{self._records_url()}/search",
            headers=headers,
            json=body,
            timeout=20,
        )
        payload = response.json()
        if payload.get("code") != 0:
            return {
                "status": "error",
                "message": payload.get("msg") or str(payload),
                "items": [],
            }

        items = []
        for record in payload.get("data", {}).get("items", []):
            fields = record.get("fields", {})
            publish_date = fields.get("发布日期")
            if isinstance(publish_date, (int, float)):
                publish_date = datetime.fromtimestamp(publish_date / 1000, CN_TZ).date().isoformat()
            items.append(
                {
                    "record_id": record.get("record_id"),
                    "title": self._field_text(fields.get("文本") or fields.get("文章标题")),
                    "cover": self._field_text(fields.get("封面图")),
                    "link": self._field_text(fields.get("原文链接")),
                    "author": self._field_text(fields.get("作者")),
                    "categories": self._field_text(fields.get("分类")),
                    "source": self._field_text(fields.get("来源")) or "每日黑料网",
                    "publish_date": publish_date or target_date.isoformat(),
                }
            )
        items.sort(key=lambda item: item.get("link", ""))
        return {
            "status": "ok",
            "date": target_date.isoformat(),
            "count": len(items),
            "items": items,
        }

    def get_daily_overview(self, target_date=None, base_url=""):
        target_date = target_date or datetime.now(CN_TZ).date()
        live_articles = self.mrhlw.fetch_today_articles(target_date)
        table_result = self.list_records_by_date(target_date)
        table_items = table_result.get("items", []) if table_result.get("status") == "ok" else []
        table_links = {item.get("link") for item in table_items if item.get("link")}

        live_items = []
        for article in live_articles:
            live_items.append(
                {
                    "title": article.get("title", ""),
                    "cover": article.get("cover", ""),
                    "link": article.get("link", ""),
                    "author": article.get("author", ""),
                    "categories": article.get("categories", ""),
                    "publish_date": target_date.isoformat(),
                    "synced": article.get("link") in table_links,
                }
            )

        return {
            "status": "ok",
            "date": target_date.isoformat(),
            "live_count": len(live_items),
            "table_count": len(table_items),
            "live_items": self._normalize_item_covers(live_items, base_url),
            "table_items": self._normalize_item_covers(table_items, base_url),
        }

    def _sync_date(self, target_date, token, existing_links, base_url=""):
        """同步指定日期文章，按链接去重；existing_links 会在成功插入后更新。"""
        articles = self.mrhlw.fetch_today_articles(target_date)
        inserted = []
        skipped = []
        inserted_items = []

        for article in articles:
            link = article["link"]
            if link in existing_links:
                skipped.append(link)
                continue

            fields = {
                "文本": article["title"],
                "封面图": self._cover_for_storage(article.get("cover") or "", base_url),
                "原文链接": link,
                "发布日期": self._date_to_ms(article["date"]),
                "作者": article.get("author") or "",
                "分类": article.get("categories") or "",
                "采集时间": self._now_ms(),
                "来源": "每日黑料网",
            }
            result = self._write_record(token, fields)
            if result.get("code") not in (0, None) and "data" not in result:
                return {
                    "status": "error",
                    "message": f"写入失败: {json.dumps(result, ensure_ascii=False)}",
                    "date": target_date.isoformat(),
                    "inserted": inserted,
                    "skipped": skipped,
                }
            inserted.append(article["title"])
            inserted_items.append(
                {
                    "title": article["title"],
                    "cover": self._cover_for_storage(article.get("cover") or "", base_url),
                    "link": link,
                    "author": article.get("author") or "",
                    "categories": article.get("categories") or "",
                }
            )
            existing_links.add(link)

        return {
            "status": "ok",
            "date": target_date.isoformat(),
            "inserted_count": len(inserted),
            "skipped_count": len(skipped),
            "inserted": inserted,
            "inserted_items": inserted_items,
            "skipped": skipped,
        }

    def sync_once(self, target_date=None, base_url="", fill_previous_day=True):
        token = self.feishu.get_token()
        if not token:
            return {"status": "error", "message": "获取飞书 token 失败"}

        ensure_result = self.ensure_table_fields(token)
        if ensure_result.get("code") not in (0, None):
            return {"status": "error", "message": f"初始化表格字段失败: {ensure_result}"}

        existing_links = self._load_existing_links(token)
        today = datetime.now(CN_TZ).date()
        explicit_date = target_date is not None

        if explicit_date:
            dates = [target_date]
        else:
            dates = []
            if fill_previous_day:
                dates.append(today - timedelta(days=1))
            dates.append(today)

        day_results = []
        total_inserted = 0
        total_skipped = 0
        all_inserted_titles = []

        for sync_date in dates:
            result = self._sync_date(sync_date, token, existing_links, base_url)
            if result.get("status") == "error":
                result["day_results"] = day_results
                return result
            day_results.append(result)
            total_inserted += result.get("inserted_count", 0)
            total_skipped += result.get("skipped_count", 0)
            all_inserted_titles.extend(result.get("inserted", []))

        if all_inserted_titles:
            summary = "\n".join(f"- {title}" for title in all_inserted_titles[:20])
            if len(all_inserted_titles) > 20:
                summary += f"\n... 另有 {len(all_inserted_titles) - 20} 篇"
            day_lines = []
            for item in day_results:
                label = item.get("date", "")
                day_lines.append(
                    f"{label}: 新增 {item.get('inserted_count', 0)}，跳过 {item.get('skipped_count', 0)}"
                )
            day_summary = "\n".join(day_lines)
            self.feishu.send_message(
                token,
                (
                    f"每日黑料网采集完成\n"
                    f"{day_summary}\n"
                    f"合计新增: {total_inserted} 篇，跳过: {total_skipped} 篇\n\n"
                    f"{summary}"
                ),
            )

        date_label = dates[-1].isoformat()
        return {
            "status": "ok",
            "message": f"同步完成，新增 {total_inserted} 篇，跳过 {total_skipped} 篇",
            "date": date_label,
            "dates": [d.isoformat() for d in dates],
            "inserted_count": total_inserted,
            "skipped_count": total_skipped,
            "inserted": all_inserted_titles,
            "day_results": day_results,
        }
