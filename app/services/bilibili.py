import requests
import re


class BilibiliService:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.bilibili.com/"}
    
    def resolve_short_url(self, url):
        try:
            res = requests.head(url, allow_redirects=True, timeout=5)
            return res.url
        except:
            return url
    
    def extract_bvid(self, text):
        bvid_match = re.search(r"BV[a-zA-Z0-9]+", text)
        if bvid_match:
            return bvid_match.group()
        
        url_match = re.search(r"https?://[^\s]+", text)
        if url_match:
            url = url_match.group()
            if "b23.tv" in url or "bilibili.com" in url:
                full_url = self.resolve_short_url(url)
                bvid_match = re.search(r"BV[a-zA-Z0-9]+", full_url)
                if bvid_match:
                    return bvid_match.group()
        return None
    
    def get_subtitle(self, bvid):
        try:
            video_res = requests.get(f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}", headers=self.headers, timeout=10)
            video_data = video_res.json()
            
            if video_data["code"] != 0:
                return None, "视频不存在"
            
            cid = video_data["data"]["cid"]
            aid = video_data["data"]["aid"]
            title = video_data["data"]["title"]
            author = video_data["data"]["owner"]["name"]
            cover = video_data["data"].get("pic", "")
            desc = video_data["data"].get("desc", "")
            
            dm_res = requests.get(f"https://api.bilibili.com/x/v2/dm/view?aid={aid}&type=1&oid={cid}", headers=self.headers, timeout=10)
            dm_data = dm_res.json()
            
            subtitles = dm_data.get("data", {}).get("subtitle", {}).get("subtitles", [])
            if not subtitles:
                return {"title": title, "author": author, "subtitle": "该视频没有字幕", "封面图": cover, "desc": desc, "hasSubtitle": False}, None
            
            sub = subtitles[0]
            for s in subtitles:
                if s["lan"] == "ai-zh":
                    sub = s
                    break
            
            sub_url = sub["subtitle_url"]
            if sub_url.startswith("//"):
                sub_url = "https:" + sub_url
            if sub_url.startswith("http://"):
                sub_url = sub_url.replace("http://", "https://")
            
            content_res = requests.get(sub_url, timeout=10)
            content_data = content_res.json()
            subtitle_text = "\n".join([line["content"] for line in content_data["body"]])
            
            return {
                "title": title,
                "author": author,
                "subtitle": subtitle_text,
                "封面图": cover,
                "desc": desc,
                "hasSubtitle": True
            }, None
        except Exception as e:
            return None, str(e)
