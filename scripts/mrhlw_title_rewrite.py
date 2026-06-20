"""黑料采集标题改写：读写飞书表。改写由 Cursor AI 按 app/prompts/mrhlw_zhihu_title.txt 完成，本脚本不调用 MiniMax。"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from app.services.mrhlw_title_rewrite import MrhlwTitleRewriteService


def cmd_pending(args):
    service = MrhlwTitleRewriteService()
    result = service.list_pending(limit=args.limit, only_empty=not args.all)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_apply(args):
    if args.file:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    else:
        payload = json.loads(args.json or "[]")
    if isinstance(payload, dict):
        items = payload.get("items", payload)
    else:
        items = payload
    service = MrhlwTitleRewriteService()
    result = service.apply_rewrites(items)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_content_prompt(args):
    service = MrhlwTitleRewriteService()
    print(
        service.format_content_prompt(
            args.title,
            args.rewrite_title,
            args.categories,
        )
    )


def cmd_pending_content(args):
    service = MrhlwTitleRewriteService()
    result = service.list_pending_content(limit=args.limit, only_empty=not args.all)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_apply_content(args):
    if args.file:
        payload = json.loads(Path(args.file).read_text(encoding="utf-8"))
    else:
        payload = json.loads(args.json or "[]")
    if isinstance(payload, dict):
        items = payload.get("items", payload)
    else:
        items = payload
    service = MrhlwTitleRewriteService()
    result = service.apply_content(items)
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_prompt(args):
    service = MrhlwTitleRewriteService()
    if args.title:
        print(service.format_prompt(args.title))
    else:
        print(service.get_prompt_template())


def main():
    parser = argparse.ArgumentParser(description="黑料采集：知乎风格标题改写（飞书读写）")
    sub = parser.add_subparsers(dest="command", required=True)

    pending = sub.add_parser("pending", help="列出待改写记录（含 prompt）")
    pending.add_argument("--limit", type=int, default=10)
    pending.add_argument("--all", action="store_true", help="包含已有改写标题的记录")

    apply = sub.add_parser("apply", help="写入改写标题到飞书表")
    apply.add_argument("--file", help="JSON 文件，如 [{record_id, rewrite_title}, ...]")
    apply.add_argument("--json", help="JSON 字符串")

    prompt = sub.add_parser("prompt", help="打印提示词模板")
    prompt.add_argument("--title", help="填入原标题后打印完整 prompt")

    pending_content = sub.add_parser("pending-content", help="列出待写内容改编的记录")
    pending_content.add_argument("--limit", type=int, default=10)
    pending_content.add_argument("--all", action="store_true")

    apply_content = sub.add_parser("apply-content", help="写入内容改编到飞书表")
    apply_content.add_argument("--file", help="JSON 文件")
    apply_content.add_argument("--json", help="JSON 字符串")

    content_prompt = sub.add_parser("content-prompt", help="打印内容改编提示词")
    content_prompt.add_argument("--title", required=True)
    content_prompt.add_argument("--rewrite-title", default="")
    content_prompt.add_argument("--categories", default="")

    args = parser.parse_args()
    if args.command == "pending":
        cmd_pending(args)
    elif args.command == "apply":
        cmd_apply(args)
    elif args.command == "prompt":
        cmd_prompt(args)
    elif args.command == "pending-content":
        cmd_pending_content(args)
    elif args.command == "apply-content":
        cmd_apply_content(args)
    elif args.command == "content-prompt":
        cmd_content_prompt(args)


if __name__ == "__main__":
    main()
