"""将本地封面图上传到飞书「生成的封面图」列。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from app.services.mrhlw_cover import MrhlwCoverService


def main():
    parser = argparse.ArgumentParser(description="上传封面到飞书多维表格")
    parser.add_argument("--record-id", required=True)
    parser.add_argument("--image", required=True, help="本地图片路径，如 配图/cover.png")
    args = parser.parse_args()

    image_path = Path(args.image)
    if not image_path.is_absolute():
        image_path = Path(__file__).resolve().parents[1] / image_path

    result = MrhlwCoverService().attach_cover(args.record_id, image_path)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
