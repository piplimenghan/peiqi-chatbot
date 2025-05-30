from flask import Flask, render_template, request, session
import requests

app = Flask(__name__)
app.secret_key = 'supersecret'

API_KEY = "sk-da124c10318142c88e682eceb2f58a70"
API_URL = "https://api.deepseek.com/v1/chat/completions"
SYSTEM_PROMPT = {"role": "system", "content": "你是一个友好、聪明的中文聊天助手。请简洁、自然地回复用户。"}

def get_reply_from_deepseek(messages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-chat",
        "messages": messages
    }
    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return f"请求失败：{response.status_code} - {response.text}"

@app.route("/", methods=["GET", "POST"])
def chat():
    if "history" not in session:
        session["history"] = [SYSTEM_PROMPT]

    reply = ""
    if request.method == "POST":
        user_input = request.form["user_input"]
        if user_input.lower() in ["退出", "清除记忆", "reset"]:
            session["history"] = [SYSTEM_PROMPT]
            reply = "记忆已清除，我们重新开始吧！"
        else:
            session["history"].append({"role": "user", "content": user_input})
            reply = get_reply_from_deepseek(session["history"])
            session["history"].append({"role": "assistant", "content": reply})

    chat_history = session.get("history", [SYSTEM_PROMPT])[1:]
    return render_template("chat.html", chat_history=chat_history, reply=reply)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

