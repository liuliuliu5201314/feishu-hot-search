import os

class Config:
    # 飞书配置
    FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_aa913ad0d7389cb6")
    FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "7JOAZJEanZMAweftGNorxc2QqhaahuBS")
    FEISHU_CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "oc_e6c00175d7bf047de0f647d4c31db4f2")
    
    # 飞书多维表格配置 - 字幕数据
    BASE_TOKEN = os.environ.get("BASE_TOKEN", "O87ebAsOKaDlsQst6nccQp2InTd")
    TABLE_ID = os.environ.get("TABLE_ID", "tblsRVZOdBJQndkM")
    
    # 飞书多维表格配置 - 热搜数据
    HOT_BASE_TOKEN = os.environ.get("HOT_BASE_TOKEN", "YoZQbG6KpakTEjsJa01c4xOZnMe")
    HOT_TABLE_ID = os.environ.get("HOT_TABLE_ID", "tblLv11iIPrg93ls")
    
    # MiniMax API配置
    MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-HebzlLy0eNiPmfxSE2Rghfr_hop33KPdJrPEZlCPn4OCb83v_sSvk-D2_WLkHcVHNNlo04uGdPEXsCDtlWQQVE3J6hnskSLzIDETE7zIA4P9BxRR6vZ_qOM")
    
    # 代理配置
    PROXY = {
        "http": "socks5://User-001:User-001@115.190.242.8:1080",
        "https": "socks5://User-001:User-001@115.190.242.8:1080"
    }
    
    # 新枝同步配置
    XINZHI_AUTH_FILE = os.environ.get("XINZHI_AUTH_FILE", "data/xinzhi_auth.json")
    XINZHI_TOKEN = os.environ.get("XINZHI_TOKEN", "")
    XINZHI_SESSION_ID = os.environ.get("XINZHI_SESSION_ID", "")
    XINZHI_USER = os.environ.get("XINZHI_USER", "新枝用户")
    XINZHI_SYNC_INTERVAL = int(os.environ.get("XINZHI_SYNC_INTERVAL", "120"))
    XINZHI_POLL_ENABLED = os.environ.get("XINZHI_POLL_ENABLED", "true").lower() == "true"
    XINZHI_SYNC_TYPES = os.environ.get("XINZHI_SYNC_TYPES", "wechat,bilibili")

    # 飞书多维表格配置 - 新枝文章（公众号等）
    # Wiki: https://jxxi08phou.feishu.cn/wiki/JZmswE7u2iTWGGkKjXScNRrNnKh?table=tblF2tvY8pSEjDjF
    ARTICLE_WIKI_TOKEN = os.environ.get("ARTICLE_WIKI_TOKEN", "JZmswE7u2iTWGGkKjXScNRrNnKh")
    ARTICLE_BASE_TOKEN = os.environ.get("ARTICLE_BASE_TOKEN", "PQBMbIK8saM22qsPNbTcsAIjnKg")
    ARTICLE_TABLE_ID = os.environ.get("ARTICLE_TABLE_ID", "tblF2tvY8pSEjDjF")

    # 飞书多维表格配置 - 每日黑料网
    MRHLW_BASE_TOKEN = os.environ.get("MRHLW_BASE_TOKEN", "I3X8bToaFaTx1LswJH9c2QFHnpd")
    MRHLW_TABLE_ID = os.environ.get("MRHLW_TABLE_ID", "tblUuP2ecpsgMsBg")
    MRHLW_SCHEDULER_ENABLED = os.environ.get("MRHLW_SCHEDULER_ENABLED", "true").lower() == "true"
    MRHLW_SYNC_HOUR = int(os.environ.get("MRHLW_SYNC_HOUR", "15"))
    MRHLW_SYNC_WINDOW_MINUTES = int(os.environ.get("MRHLW_SYNC_WINDOW_MINUTES", "5"))

    PUBLIC_BASE_URL = os.environ.get("PUBLIC_BASE_URL", "https://feishu-hot-search.onrender.com")

    # 服务配置
    PORT = int(os.environ.get("PORT", 8080))
