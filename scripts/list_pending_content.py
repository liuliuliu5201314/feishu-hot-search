import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.services.mrhlw_title_rewrite import MrhlwTitleRewriteService

items = MrhlwTitleRewriteService().list_pending_content(limit=100)["items"]
for i, item in enumerate(items, 1):
    print(f"{i}\t{item['record_id']}\t{item['rewrite_title']}")
