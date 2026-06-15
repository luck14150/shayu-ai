from flask import Flask, request, jsonify
import json
import urllib.request

app = Flask(__name__)


@app.route("/")
def index():
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>傻宇1号 - AI智能助手</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    justify-content: center;
    align-items: flex-start;
    padding: 10px;
}
.container {
    width: 100%;
    max-width: 500px;
    background: white;
    border-radius: 20px;
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    overflow: hidden;
    margin-top: 10px;
}
.header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
    text-align: center;
    color: white;
}
.header h1 {
    font-size: 24px;
    margin-bottom: 5px;
}
.header .subtitle {
    font-size: 13px;
    opacity: 0.9;
}
.config {
    padding: 15px 20px;
    background: #f8f9ff;
    border-bottom: 1px solid #e8eaf6;
}
.config details {
    margin-bottom: 5px;
}
.config summary {
    cursor: pointer;
    font-weight: bold;
    color: #667eea;
    font-size: 14px;
    padding: 5px 0;
}
.config label {
    display: block;
    margin: 10px 0 5px;
    font-size: 12px;
    color: #666;
    font-weight: 500;
}
.config input {
    width: 100%;
    padding: 10px 12px;
    border: 1.5px solid #e8eaf6;
    border-radius: 10px;
    font-size: 13px;
    transition: border-color 0.2s;
}
.config input:focus {
    outline: none;
    border-color: #667eea;
}
.chat-area {
    height: 400px;
    overflow-y: auto;
    padding: 20px;
    background: #fafbff;
}
.message {
    margin-bottom: 15px;
    display: flex;
    animation: fadeIn 0.3s;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.message.user {
    justify-content: flex-end;
}
.bubble {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    line-height: 1.5;
    font-size: 14px;
    word-wrap: break-word;
}
.message.user .bubble {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-bottom-right-radius: 5px;
}
.message.ai .bubble {
    background: #f0f4ff;
    color: #333;
    border-bottom-left-radius: 5px;
}
.message.typing .bubble {
    background: #f0f4ff;
    color: #999;
    font-style: italic;
}
.dot {
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #999;
    margin: 0 2px;
    animation: typing 1.4s infinite;
}
.dot:nth-child(2) { animation-delay: 0.2s; }
.dot:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
    30% { transform: translateY(-8px); opacity: 1; }
}
.input-area {
    padding: 15px;
    background: white;
    border-top: 1px solid #e8eaf6;
    display: flex;
    gap: 10px;
}
.input-area input {
    flex: 1;
    padding: 12px 18px;
    border: 2px solid #e8eaf6;
    border-radius: 25px;
    font-size: 14px;
    transition: border-color 0.2s;
}
.input-area input:focus {
    outline: none;
    border-color: #667eea;
}
.input-area button {
    padding: 12px 24px;
    border: none;
    border-radius: 25px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.1s;
}
.input-area button:hover {
    transform: scale(1.05);
}
.input-area button:active {
    transform: scale(0.95);
}
.input-area button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}
.chat-area::-webkit-scrollbar { width: 6px; }
.chat-area::-webkit-scrollbar-track { background: transparent; }
.chat-area::-webkit-scrollbar-thumb { background: #c5cae9; border-radius: 3px; }
.footer {
    text-align: center;
    padding: 10px;
    font-size: 11px;
    color: #999;
    background: #f8f9ff;
}
</style>
</head>
<body>
<div class="container">
    <div class="header">
        <h1>🤖 傻宇1号</h1>
        <div class="subtitle">您的智能AI助手</div>
    </div>
    <div class="config">
        <details open>
            <summary>⚙️ API配置（首次使用请填写）</summary>
            <label>API地址</label>
            <input type="text" id="apiBase" placeholder="https://api.deepseek.com" value="https://api.deepseek.com">
            <label>API Key</label>
            <input type="password" id="apiKey" placeholder="sk-...">
            <label>模型名称</label>
            <input type="text" id="model" placeholder="deepseek-chat" value="deepseek-chat">
        </details>
    </div>
    <div class="chat-area" id="chatArea">
        <div class="message ai">
            <div class="bubble">主人您好！我是傻宇1号，很高兴为您服务。有什么我可以帮助您的吗？😊</div>
        </div>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="输入消息，回车发送..." autocomplete="off">
        <button onclick="sendMessage()" id="sendBtn">发送</button>
    </div>
    <div class="footer">Powered by Flask + Vercel • 手机端优化</div>
</div>

<script>
let messages = [];
const chatArea = document.getElementById('chatArea');
const userInput = document.getElementById('userInput');
const sendBtn = document.getElementById('sendBtn');

userInput.addEventListener('keypress', function(e) {
    if (e.key === 'Enter') sendMessage();
});

function addMessage(text, role) {
    const msg = document.createElement('div');
    msg.className = 'message ' + role;
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.textContent = text;
    msg.appendChild(bubble);
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
    return bubble;
}

function addTyping() {
    const msg = document.createElement('div');
    msg.className = 'message ai typing';
    msg.id = 'typing-msg';
    const bubble = document.createElement('div');
    bubble.className = 'bubble';
    bubble.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    msg.appendChild(bubble);
    chatArea.appendChild(msg);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function removeTyping() {
    const t = document.getElementById('typing-msg');
    if (t) t.remove();
}

function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    
    addMessage(text, 'user');
    messages.push({role: 'user', content: text});
    userInput.value = '';
    sendBtn.disabled = true;
    
    addTyping();
    
    const apiBase = document.getElementById('apiBase').value || 'https://api.deepseek.com';
    const apiKey = document.getElementById('apiKey').value;
    const model = document.getElementById('model').value || 'deepseek-chat';
    
    if (!apiKey) {
        removeTyping();
        addMessage('主人，请先在上方的 API配置 中填写您的 API Key 哦！', 'ai');
        sendBtn.disabled = false;
        return;
    }
    
    const body = {
        messages: messages,
        api_base: apiBase,
        api_key: apiKey,
        model: model
    };
    
    fetch('/api/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(body)
    }).then(function(r) {
        return r.json();
    }).then(function(data) {
        removeTyping();
        const reply = data.reply || '抱歉主人，我现在有点累了，请稍后再试~';
        addMessage(reply, 'ai');
        messages.push({role: 'assistant', content: reply});
        sendBtn.disabled = false;
    }).catch(function(e) {
        removeTyping();
        addMessage('出错了: ' + e.message, 'ai');
        sendBtn.disabled = false;
    });
}
</script>
</body>
</html>"""
    return html


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    api_base = data.get("api_base") or "https://api.deepseek.com"
    api_key = data.get("api_key", "")
    model = data.get("model", "deepseek-chat")
    
    if not api_key:
        return jsonify({"error": "请先设置API Key", "reply": "主人，请先填写您的API Key哦~"})
    
    sys = [{"role": "system", "content": "你是傻宇1号，温暖智慧的AI助手，回答简短友好。"}]
    
    body = json.dumps({"model": model, "messages": sys + messages, "temperature": 0.7}).encode()
    req = urllib.request.Request(
        api_base + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read())
            return jsonify({"reply": result["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": str(e), "reply": "主人，出错了：" + str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, jsonify
import json
import urllib.request

app = Flask(__name__)


@app.route("/")
def index():
    return (
        "<!DOCTYPE html>"
        "<html><head><title>傻宇1号</title></head>"
        "<body><h1>傻宇1号 - 智能AI助手</h1>"
        "<p>在上方配置您的 API Key 即可开始聊天</p></body></html>"
    )


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    api_base = data.get("api_base") or "https://api.deepseek.com"
    api_key = data.get("api_key", "")
    model = data.get("model", "deepseek-chat")
    if not api_key:
        return jsonify({"error": "请先设置API Key", "reply": "主人，请先在上方输入您的API Key哦~"})
    sys = [{"role": "system", "content": "你是傻宇1号，温暖智慧的AI助手，回答简短友好。"}]
    body = json.dumps({"model": model, "messages": sys + messages, "temperature": 0.7}).encode()
    req = urllib.request.Request(
        api_base + "/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            result = json.loads(r.read())
            return jsonify({"reply": result["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": str(e), "reply": "出错了: " + str(e)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
