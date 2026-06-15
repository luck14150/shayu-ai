from flask import Flask, request, jsonify
import json, os, socket

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    import urllib.request, ssl

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>shayu-ai</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:8px}.c{max-width:500px;margin:0 auto;background:white;border-radius:20px;overflow:hidden}.h{background:linear-gradient(135deg,#667eea,#764ba2);padding:20px;text-align:center;color:white}.config{padding:15px 20px;background:#f8f9ff}.config label{display:block;margin:8px 0 5px;font-size:12px;color:#666}.config input{width:100%;padding:10px 12px;border:1.5px solid #e8eaf6;border-radius:8px;font-size:13px}.chat{height:400px;overflow-y:auto;padding:20px;background:#fafbff}.msg{margin-bottom:12px;display:flex}.msg.u{justify-content:flex-end}.b{max-width:85%;padding:10px 14px;border-radius:14px;font-size:14px;line-height:1.5;word-wrap:break-word;white-space:pre-wrap}.msg.u .b{background:linear-gradient(135deg,#667eea,#764ba2);color:white}.msg.a .b{background:#f0f4ff;color:#333}.msg.s .b{background:#fff8e1;color:#666;font-size:12px;font-style:italic}.in{padding:15px;background:white;border-top:1px solid #e8eaf6;display:flex;gap:8px}.in input{flex:1;padding:12px 16px;border:2px solid #e8eaf6;border-radius:25px;font-size:14px}.in button{padding:12px 20px;border:none;border-radius:25px;background:linear-gradient(135deg,#667eea,#764ba2);color:white;font-size:14px;font-weight:600;cursor:pointer}.in button:disabled{opacity:.5}.ftr{text-align:center;padding:12px;font-size:11px;color:#888;background:#f8f9ff}</style>
</head><body><div class="c"><div class="h"><h1>shayu-ai</h1></div>
<div class="config"><label>API地址</label><input type="text" id="ab" value="https://api.deepseek.com"><label>API Key</label><input type="password" id="ak" placeholder="输入API Key"><label>模型</label><input type="text" id="md" value="deepseek-chat"></div>
<div class="chat" id="ca"><div class="msg a"><div class="b">Hi! I am shayu-ai. Please configure your API Key and start chatting!</div></div></div>
<div class="in"><input type="text" id="ui" placeholder="Type message and press enter..." autocomplete="off"><button onclick="send()" id="sb">Send</button></div>
<div class="ftr">shayu-ai v2.0</div></div>
<script>let msgs=[];const ca=document.getElementById("ca");const ui=document.getElementById("ui");const sb=document.getElementById("sb");ui.addEventListener("keypress",function(e){if(e.key==="Enter")send()});function am(t,r){const m=document.createElement("div");m.className="msg "+r;const b=document.createElement("div");b.className="b";b.textContent=t;m.appendChild(b);ca.appendChild(m);ca.scrollTop=ca.scrollHeight}function send(){const t=ui.value.trim();if(!t)return;am(t,"u");msgs.push({role:"user",content:t});ui.value="";sb.disabled=true;const body={messages:msgs,api_base:document.getElementById("ab").value,api_key:document.getElementById("ak").value,model:document.getElementById("md").value};fetch("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}).then(function(r){return r.json()}).then(function(d){am(d.reply||"Sorry, I am tired now.","a");msgs.push({role:"assistant",content:d.reply||""});sb.disabled=false}).catch(function(e){am("Error:"+e.message,"s");sb.disabled=false})}</script></body></html>"""

@app.route("/")
def index():
    return HTML

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json or {}
    messages = data.get("messages", [])
    api_base = data.get("api_base") or "https://api.deepseek.com"
    api_key = data.get("api_key", "")
    model = data.get("model") or "deepseek-chat"
    if not api_key:
        return jsonify({"error": "missing api key", "reply": "Please configure your API Key first."}), 200
    sys_msg = {"role": "system", "content": "You are shayu-ai, a warm and smart AI assistant. Answer concisely and friendly."}
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {"model": model, "messages": [sys_msg] + messages, "temperature": 0.7}
    headers = {"Content-Type": "application/json", "Authorization": "Bearer " + api_key}
    try:
        if HAS_REQUESTS:
            resp = requests.post(url, json=payload, headers=headers, timeout=120, verify=True)
            result = resp.json()
        else:
            body_bytes = json.dumps(payload).encode("utf-8")
            ctx = ssl.create_default_context()
            req = urllib.request.Request(url, data=body_bytes, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=120, context=ctx) as response:
                result = json.loads(response.read().decode("utf-8"))
        if "choices" in result and len(result["choices"]) > 0:
            return jsonify({"reply": result["choices"][0]["message"]["content"]})
        if "error" in result:
            return jsonify({"error": result["error"], "reply": "API error: " + str(result["error"])})
        return jsonify({"error": "unexpected response", "reply": "Unexpected API response format."})
    except socket.timeout:
        return jsonify({"error": "timeout", "reply": "Request timeout. Please try again."}), 200
    except Exception as e:
        return jsonify({"error": str(e), "reply": "Error: " + str(e)}), 200

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "shayu-ai"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
