const feishu = require('./feishu');
const bilibili = require('./bilibili');
const minimax = require('./minimax');

const processedEvents = new Set();

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  const data = req.body;
  
  if (data.challenge) {
    return res.json({ challenge: data.challenge });
  }
  
  if (data.header && data.header.event_type === 'im.message.receive_v1') {
    const eventId = data.header.event_id;
    
    if (processedEvents.has(eventId)) {
      return res.json({ code: 0 });
    }
    processedEvents.add(eventId);
    
    if (processedEvents.size > 1000) {
      processedEvents.clear();
    }
    
    const event = data.event;
    const message = event.message || {};
    const chatId = message.chat_id || '';
    const content = JSON.parse(message.content || '{}');
    const text = content.text || '';
    
    const bvidResult = bilibili.extractBvid(text);
    let bvid = null;
    
    if (bvidResult && bvidResult.isShortUrl) {
      const fullUrl = await bilibili.resolveShortUrl(bvidResult.url);
      const match = fullUrl.match(/BV[a-zA-Z0-9]+/);
      if (match) bvid = match[0];
    } else if (bvidResult) {
      bvid = bvidResult;
    }
    
    if (bvid) {
      const token = await feishu.getToken();
      const result = await bilibili.getSubtitle(bvid);
      
      if (result.error) {
        await feishu.sendMessage(token, chatId, `提取失败: ${result.error}`);
      } else {
        const summary = await minimax.summarize(result.subtitle, '请总结这段字幕的核心观点，用简洁的中文回答，不超过100字');
        
        const now = new Date();
        const timestamp = now.getTime();
        
        await feishu.writeToBase(token, {
          '视频标题': result.title,
          'BV号': bvid,
          '字幕内容': result.subtitle.substring(0, 2000),
          '抓取时间': timestamp,
          '创建时间': timestamp,
          '作者': result.author,
          '封面图': result.cover,
          '简介': result.desc,
          'minimax总结': summary
        });
        
        await feishu.sendMessage(token, chatId, `字幕提取完成\n视频: ${result.title}\n作者: ${result.author}\n\nAI总结:\n${summary}`);
      }
    }
  }
  
  res.json({ code: 0 });
};
