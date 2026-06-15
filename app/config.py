import os

class Config:
    # 飞书配置
    FEISHU_APP_ID = os.environ.get("FEISHU_APP_ID", "cli_aa913ad0d7389cb6")
    FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "7JOAZJEanZMAweftGNorxc2QqhaahuBS")
    FEISHU_CHAT_ID = os.environ.get("FEISHU_CHAT_ID", "oc_e6c00175d7bf047de0f647d4c31db4f2")
    
    # 飞书多维表格配置
    BASE_TOKEN = os.environ.get("BASE_TOKEN", "O87ebAsOKaDlsQst6nccQp2InTd")
    TABLE_ID = os.environ.get("TABLE_ID", "tblsRVZOdBJQndkM")
    
    # MiniMax API配置
    MINIMAX_API_KEY = os.environ.get("MINIMAX_API_KEY", "sk-cp-HebzlLy0eNiPmfxSE2Rghfr_hop33KPdJrPEZlCPn4OCb83v_sSvk-D2_WLkHcVHNNlo04uGdPEXsCDtlWQQVE3J6hnskSLzIDETE7zIA4P9BxRR6vZ_qOM")
    
    # 代理配置
    PROXY = {
        "http": "socks5://User-001:User-001@115.190.242.8:1080",
        "https": "socks5://User-001:User-001@115.190.242.8:1080"
    }
    
    # 服务配置
    PORT = int(os.environ.get("PORT", 8080))
