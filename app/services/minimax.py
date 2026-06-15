import requests
from ..config import Config


class MinimaxService:
    def __init__(self):
        self.api_key = Config.MINIMAX_API_KEY
        self.url = "https://api.minimax.chat/v1/text/chatcompletion_v2"
    
    def summarize(self, text, prompt="请总结这段内容的核心观点"):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "MiniMax-Text-01",
            "messages": [
                {"role": "system", "content": "你是一个专业的文本总结助手。"},
                {"role": "user", "content": f"{prompt}\n\n{text[:3000]}"}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }
        res = requests.post(self.url, headers=headers, json=data, timeout=30)
        result = res.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"]
        return "总结失败"
