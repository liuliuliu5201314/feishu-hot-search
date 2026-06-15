const feishu = require('./feishu');
const bilibili = require('./bilibili');

module.exports = async (req, res) => {
  const url = new URL(req.url);
  const bvid = url.searchParams.get('bvid');
  
  if (!bvid) {
    return res.status(400).json({ error: '请提供 bvid 参数' });
  }
  
  const result = await bilibili.getSubtitle(bvid);
  
  if (result.error) {
    return res.status(400).json({ error: result.error });
  }
  
  return res.json(result);
};
