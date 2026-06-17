from datetime import datetime
import re

from ..config import Config
from .bilibili import BilibiliService
from .feishu import FeishuService
from .minimax import MinimaxService
from .xinzhi import XinzhiService


def _property_value(properties, key):
    for item in properties or []:
        if item.get("key") != key:
            continue
        value = item.get("value")
        if isinstance(value, list):
            return value[0] if value else ""
        return value or ""
    return ""


def _property_list(properties, key):
    for item in properties or []:
        if item.get("key") != key:
            continue
        value = item.get("value")
        if isinstance(value, list):
            return value
        return [value] if value else []
    return []


class XinzhiSyncService:
    def __init__(self):
        self.xinzhi = XinzhiService()
        self.feishu = FeishuService()
        self.minimax = MinimaxService()
        self.bilibili = BilibiliService()

    def _classify_link(self, link):
        if not link:
            return None
        if "mp.weixin.qq.com" in link:
            return "wechat"
        if "bilibili.com" in link or "b23.tv" in link:
            return "bilibili"
        return None

    def _allowed_types(self):
        raw = Config.XINZHI_SYNC_TYPES
        return {item.strip() for item in raw.split(",") if item.strip()}

    def _parse_collect_time(self, value):
        if not value:
            return int(datetime.now().timestamp() * 1000)
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                return int(datetime.strptime(value[:19], fmt).timestamp() * 1000)
            except ValueError:
                continue
        return int(datetime.now().timestamp() * 1000)

    def _now_ms(self):
        return int(datetime.now().timestamp() * 1000)

    def _extract_cover_image(self, body, properties=None, bilibili_cover=""):
        if bilibili_cover:
            return bilibili_cover
        for key in ("cover", "coverUrl", "icon", "image", "thumb"):
            value = _property_value(properties or [], key)
            if value and str(value).startswith("http"):
                return str(value)
        text = body or ""
        match = re.search(r"!\[[^\]]*\]\((https?://[^\)]+)\)", text)
        if match:
            return match.group(1)
        match = re.search(
            r"(https?://[^\s\"']+\.(?:jpg|jpeg|png|gif|webp)(?:\?[^\s\"']*)?)",
            text,
            re.I,
        )
        if match:
            return match.group(1)
        return ""

    def _base_fields(self, collect_time, cover_url=""):
        fields = {
            "收藏时间": collect_time,
            "创建时间": self._now_ms(),
        }
        if cover_url:
            fields["封面图"] = cover_url
        return fields

    def _build_article_fields(self, content, source_type, link, extra=None):
        properties = content.get("properties", [])
        body = "\n".join(content.get("text") or [])
        authors = _property_list(properties, "authorList")
        collect_time = self._parse_collect_time(_property_value(properties, "collectTime"))
        summary = ""
        if body.strip():
            summary = self.minimax.summarize(
                body,
                "请用简洁中文总结这篇文章的核心观点，不超过150字",
            )

        fields = {
            "文章标题": content.get("title") or "暂无标题",
            "原文链接": link,
            "作者": ", ".join(authors),
            "正文内容": body[:8000],
            "来源类型": "公众号" if source_type == "wechat" else "哔哩哔哩",
            "新枝标签": ", ".join(content.get("tagList") or []),
            "minimax总结": summary,
        }
        fields.update(
            self._base_fields(
                collect_time,
                self._extract_cover_image(body, properties),
            )
        )
        if extra:
            fields.update(extra)
        return fields

    def _sync_bilibili_article(self, token, content, link):
        fetch_link = link.strip()
        if fetch_link and not fetch_link.startswith("http"):
            fetch_link = "https://" + fetch_link.lstrip("/")

        bvid = self.bilibili.extract_bvid(fetch_link)
        if not bvid:
            return None, f"无法从短链识别 BV 号: {link}", None

        result, error = self.bilibili.get_subtitle(bvid)
        if error:
            return None, error, None

        subtitle = result.get("subtitle", "")
        summary = ""
        if subtitle.strip():
            summary = self.minimax.summarize(
                subtitle,
                "请总结这段字幕的核心观点，用简洁的中文回答，不超过100字",
            )
        properties = content.get("properties", [])
        collect_time = self._parse_collect_time(_property_value(properties, "collectTime"))
        video_title = result.get("title") or content.get("title") or "暂无标题"
        desc = result.get("desc", "")

        fields = {
            "文章标题": video_title,
            "原文链接": link,
            "作者": result.get("author", ""),
            "正文内容": subtitle[:8000],
            "来源类型": "哔哩哔哩",
            "新枝标签": ", ".join(content.get("tagList") or []),
            "minimax总结": summary,
        }
        fields.update(
            self._base_fields(
                collect_time,
                self._extract_cover_image("", properties, result.get("封面图", "")),
            )
        )
        if desc:
            fields["正文内容"] = f"简介：{desc}\n\n{subtitle}"[:8000]

        feishu_result = self.feishu.write_article_to_base(token, fields)
        if feishu_result.get("code") not in (0, None) and "data" not in feishu_result:
            return None, str(feishu_result), None
        return feishu_result, None, video_title

    def _process_task(self, feishu_token, xinzhi_token, task_id):
        content = self.xinzhi.get_sync_content(task_id, xinzhi_token)
        if content is None:
            self.xinzhi.mark_sync_success(task_id, xinzhi_token)
            return {"task_id": task_id, "status": "skipped", "reason": "任务已同步过"}

        if content.get("superType") != "SUPER_LINK":
            self.xinzhi.mark_sync_success(task_id, xinzhi_token)
            return {"task_id": task_id, "status": "skipped", "reason": "非链接类内容"}

        link = _property_value(content.get("properties", []), "link")
        source_type = self._classify_link(link)
        if not source_type or source_type not in self._allowed_types():
            self.xinzhi.mark_sync_success(task_id, xinzhi_token)
            return {"task_id": task_id, "status": "skipped", "reason": "非目标来源"}

        if source_type == "bilibili":
            result, error, video_title = self._sync_bilibili_article(feishu_token, content, link)
            if error:
                self.xinzhi.mark_sync_failed(task_id, xinzhi_token, error)
                return {"task_id": task_id, "status": "failed", "error": error}
            display_title = video_title
        else:
            fields = self._build_article_fields(content, source_type, link)
            result = self.feishu.write_article_to_base(feishu_token, fields)
            if result.get("code") not in (0, None) and "data" not in result:
                error = str(result)
                self.xinzhi.mark_sync_failed(task_id, xinzhi_token, error)
                return {"task_id": task_id, "status": "failed", "error": error}
            display_title = content.get("title") or link

        self.xinzhi.mark_sync_success(task_id, xinzhi_token)
        self.feishu.send_message(
            feishu_token,
            f"新枝收藏已同步到飞书\n标题: {display_title}\n来源: {'公众号' if source_type == 'wechat' else '哔哩哔哩'}\n链接: {link}",
        )
        return {"task_id": task_id, "status": "ok", "title": display_title, "source": source_type}

    def sync_once(self):
        ready, auth = self.xinzhi.account_ready()
        if not ready:
            return {"status": "error", "message": "新枝账号未绑定或已失效，请先完成绑定"}

        xinzhi_token = auth["token"]
        feishu_token = self.feishu.get_token()
        processed = []
        has_more = True

        while has_more:
            tasks_response = self.xinzhi.get_sync_tasks(xinzhi_token)
            if not tasks_response.get("valid"):
                self.xinzhi.clear_auth()
                return {"status": "error", "message": "新枝账号已解绑，请重新绑定"}

            tasks = tasks_response.get("result") or []
            if not tasks:
                break

            for task in tasks:
                try:
                    processed.append(self._process_task(feishu_token, xinzhi_token, task["id"]))
                except Exception as exc:
                    try:
                        self.xinzhi.mark_sync_failed(task["id"], xinzhi_token, str(exc))
                    except Exception:
                        pass
                    processed.append({"task_id": task["id"], "status": "failed", "error": str(exc)})

            has_more = len(tasks) == tasks_response.get("limit", 0)

        ok_count = len([item for item in processed if item.get("status") == "ok"])
        return {
            "status": "ok",
            "message": f"同步完成，处理 {len(processed)} 条，成功 {ok_count} 条",
            "items": processed,
        }
