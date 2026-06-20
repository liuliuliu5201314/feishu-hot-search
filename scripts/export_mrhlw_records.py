import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

import requests

from app.config import Config

tok = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": Config.FEISHU_APP_ID, "app_secret": Config.FEISHU_APP_SECRET},
).json()["tenant_access_token"]
headers = {"Authorization": f"Bearer {tok}"}
base, table = Config.MRHLW_BASE_TOKEN, Config.MRHLW_TABLE_ID

items = []
page_token = None
while True:
    params = {"page_size": 500}
    if page_token:
        params["page_token"] = page_token
    payload = requests.get(
        f"https://open.feishu.cn/open-apis/bitable/v1/apps/{base}/tables/{table}/records",
        headers=headers,
        params=params,
        timeout=20,
    ).json()
    for record in payload.get("data", {}).get("items", []):
        fields = record.get("fields", {})
        title = fields.get("文本") or ""
        if isinstance(title, list):
            title = "".join(title)
        if not str(title).strip():
            continue
        rewrite = fields.get("改写标题") or ""
        if isinstance(rewrite, list):
            rewrite = "".join(rewrite)
        content = fields.get("内容改编") or ""
        if isinstance(content, list):
            content = "".join(content)
        items.append(
            {
                "record_id": record["record_id"],
                "title": str(title),
                "rewrite_title": str(rewrite),
                "content": str(content),
                "categories": str(fields.get("分类") or ""),
                "author": str(fields.get("作者") or ""),
            }
        )
    if not payload.get("data", {}).get("has_more"):
        break
    page_token = payload.get("data", {}).get("page_token")

out = Path(__file__).resolve().parents[1] / "data" / "mrhlw_all_records.json"
out.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"exported {len(items)} records -> {out}")
