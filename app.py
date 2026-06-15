
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
