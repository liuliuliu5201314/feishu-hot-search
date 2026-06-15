async function resolveShortUrl(url) {
  try {
    const res = await fetch(url, { redirect: 'follow' });
    return res.url;
  } catch {
    return url;
  }
}

function extractBvid(text) {
  const bvidMatch = text.match(/BV[a-zA-Z0-9]+/);
  if (bvidMatch) return bvidMatch[0];
  
  const urlMatch = text.match(/https?:\/\/[^\s]+/);
  if (urlMatch) {
    const url = urlMatch[0];
    if (url.includes('b23.tv') || url.includes('bilibili.com')) {
      // For short URLs, we need to follow redirects
      // This will be handled in the async function
      return { isShortUrl: true, url: url };
    }
  }
  return null;
}

async function getSubtitle(bvid) {
  const headers = { 'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com/' };
  
  try {
    const videoRes = await fetch(`https://api.bilibili.com/x/web-interface/view?bvid=${bvid}`, { headers });
    const videoData = await videoRes.json();
    
    if (videoData.code !== 0) {
      return { error: '视频不存在' };
    }
    
    const cid = videoData.data.cid;
    const aid = videoData.data.aid;
    const title = videoData.data.title;
    const author = videoData.data.owner.name;
    const cover = videoData.data.pic || '';
    const desc = videoData.data.desc || '';
    
    const dmRes = await fetch(`https://api.bilibili.com/x/v2/dm/view?aid=${aid}&type=1&oid=${cid}`, { headers });
    const dmData = await dmRes.json();
    
    const subtitles = dmData?.data?.subtitle?.subtitles || [];
    if (subtitles.length === 0) {
      return { title, author, subtitle: '该视频没有字幕', cover, desc, hasSubtitle: false };
    }
    
    let sub = subtitles[0];
    for (const s of subtitles) {
      if (s.lan === 'ai-zh') { sub = s; break; }
    }
    
    let subUrl = sub.subtitle_url;
    if (subUrl.startsWith('//')) subUrl = 'https:' + subUrl;
    if (subUrl.startsWith('http://')) subUrl = subUrl.replace('http://', 'https://');
    
    const contentRes = await fetch(subUrl);
    const contentData = await contentRes.json();
    const subtitleText = contentData.body.map(l => l.content).join('\n');
    
    return { title, author, subtitle: subtitleText, cover, desc, hasSubtitle: true };
  } catch (e) {
    return { error: e.message };
  }
}

module.exports = { extractBvid, getSubtitle, resolveShortUrl };
