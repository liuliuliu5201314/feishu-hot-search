const feishu = require('./feishu');

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  try {
    const data = req.body;
    const token = await feishu.getToken();
    await feishu.sendMessage(token, `字幕提取完成\n视频: ${data.title}\n作者: ${data.author}\n\n字幕内容:\n${data.subtitle.substring(0, 1000)}`);
    return res.json({ status: 'ok', message: '推送成功' });
  } catch (e) {
    return res.status(500).json({ status: 'error', message: e.message });
  }
};
