const feishu = require('./feishu');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const data = req.body;
    const token = await feishu.getToken();
    
    const now = new Date();
    const timestamp = now.getTime();
    
    await feishu.writeToBase(token, {
      '视频标题': data.title,
      'BV号': data.bvid,
      '字幕内容': data.subtitle.substring(0, 2000),
      '抓取时间': timestamp,
      '创建时间': timestamp,
      '作者': data.author || '',
      '封面图': data.cover || '',
      '简介': data.desc || '',
      'minimax总结': data.summary || ''
    });
    
    return res.json({ status: 'ok', message: '保存成功' });
  } catch (e) {
    return res.status(500).json({ status: 'error', message: e.message });
  }
};
