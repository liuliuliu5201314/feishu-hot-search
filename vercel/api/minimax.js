const config = require('./config');

async function summarize(text, prompt = '请总结这段内容的核心观点') {
  const res = await fetch('https://api.minimax.chat/v1/text/chatcompletion_v2', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${config.MINIMAX_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      model: 'MiniMax-Text-01',
      messages: [
        { role: 'system', content: '你是一个专业的文本总结助手。' },
        { role: 'user', content: `${prompt}\n\n${text.substring(0, 3000)}` }
      ],
      temperature: 0.7,
      max_tokens: 500
    })
  });
  
  const result = await res.json();
  if (result.choices) {
    return result.choices[0].message.content;
  }
  return '总结失败';
}

module.exports = { summarize };
