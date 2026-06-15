const config = require('./config');

async function getToken() {
  const res = await fetch('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ app_id: config.FEISHU_APP_ID, app_secret: config.FEISHU_APP_SECRET })
  });
  const data = await res.json();
  return data.tenant_access_token;
}

async function sendMessage(token, content) {
  const res = await fetch('https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      receive_id: config.FEISHU_CHAT_ID,
      msg_type: 'text',
      content: JSON.stringify({ text: content })
    })
  });
  return res.json();
}

async function writeToBase(token, data) {
  const res = await fetch(`https://open.feishu.cn/open-apis/bitable/v1/apps/${config.BASE_TOKEN}/tables/${config.TABLE_ID}/records`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ fields: data })
  });
  return res.json();
}

module.exports = { getToken, sendMessage, writeToBase };
