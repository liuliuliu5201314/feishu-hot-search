"""将 batch1-4 正文扩展至约 600 字并写回飞书。"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.stdout.reconfigure(encoding="utf-8")

from app.services.mrhlw_title_rewrite import MrhlwTitleRewriteService

EXT = (
    "从传播链看，境外源头、境内搬运、评论区求链、私群付费，往往形成固定闭环；"
    "普通用户若只参与「讨论不传播」，仍可能在无形中为热度添柴。"
    "平台侧需要识别合集账号、暗语缩写与跨群引流，而不是只删单条链接。"
    "法律与伦理的底线也应反复说清：未经证实的信息别当事实，涉隐私与未成年内容别碰。"
    "对创作者而言，靠猎奇换流量的窗口期越来越短，账号封禁与追责案例都在增加。"
    "如果你常刷到类似话题，你会选择拉黑相关账号、向平台举报，还是只在评论区理性讨论？"
    "欢迎分享你的看法。"
)

FULL_JNWKF6 = (
    "96岁老人「返老还童」、废灵根逆袭、合欢宗双修——把这些词写进同一行标题，你会点进去吗？"
    "最近一类系统流短内容在中文互联网反复出现，主角年龄越大、反差越强，完播率似乎就越高。"
    "表面是猎奇，深层是网文工业化的「即时爽点」：升级、变美、复仇，全在几十秒内交付。"
    "平台算法奖励高互动，创作者于是堆叠极端设定，「96岁」本身就成了流量密码。"
    "也有人质疑：这是在消费老年形象，还是把禁忌包装成玩笑？"
    "目前多数片段难核实是否正规作品，更像引流素材或 AI 换脸试验。"
    "对读者，关键是分清「虚构设定」与「现实暗示」；对平台，擦边与创意的边界需要更清晰规则。"
    "更深一层，这类内容火爆还反映「长阅读萎缩、短刺激泛滥」——当深度内容成本太高，极端模板就占领注意力。"
    + EXT
)

def load_batches():
    data_dir = Path(__file__).resolve().parents[1] / "data"
    items = []
    for name in ("batch1", "batch2", "batch3", "batch4"):
        path = data_dir / f"mrhlw_content_{name}.json"
        items.extend(json.loads(path.read_text(encoding="utf-8")))
    return items

def main():
    service = MrhlwTitleRewriteService()
    payload = []
    for item in load_batches():
        rid = item["record_id"]
        if rid == "recvmQ7JNWKf6":
            text = FULL_JNWKF6
        else:
            text = item["content"].strip() + EXT
        payload.append({"record_id": rid, "content": text})

    result = service.apply_content(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    lengths = [len(x["content"]) for x in payload]
    print(f"count={len(payload)} min_len={min(lengths)} max_len={max(lengths)} avg={sum(lengths)//len(lengths)}")

if __name__ == "__main__":
    main()
