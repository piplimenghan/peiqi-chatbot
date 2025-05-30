from flask import Flask, render_template, request, session
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecret'

API_KEY = os.environ.get("KEY", "sk-da124c10318142c88e682eceb2f58a70")
API_URL = "https://api.deepseek.com/v1/chat/completions"
SYSTEM_PROMPT = {"role": "system", "content": "你是一个由中国矿业大学（北京）李孟翰开发的 PeiQi AI 助手。请简洁、自然地回复用户。"}

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
        user_input = request.form["user_input"].strip()

        if user_input.lower() in ["退出", "清除记忆", "reset"]:
            session["history"] = [SYSTEM_PROMPT]
            reply = "记忆已清除，我们重新开始吧！"
        else:
            # ✅ 添加用户输入到历史
            session["history"].append({"role": "user", "content": user_input})

            # 主人/开发者识别逻辑
            owner_phrases = ["你主人是谁", "谁开发了你", "你是谁做的", "你主人的名字", "你是谁的机器人", "你是谁开发的"]
            dev_phrases = ["李孟翰是谁", "谁是李孟翰", "你认识李孟翰吗", "你知道李孟翰吗"]

            if any(phrase in user_input for phrase in owner_phrases):
                reply = "李孟翰是我的主人。"
            elif "李孟翰" in user_input and len(user_input) < 7:
                reply = "李孟翰是我的开发者，他基于 DeepSeek 模型开发了我——PeiQi AI 助手。"
            elif any(phrase in user_input for phrase in dev_phrases):
                reply = "李孟翰是我的开发者，他基于 DeepSeek 模型开发了我——PeiQi AI 助手。"
            else:
                reply = get_reply_from_deepseek(session["history"])

            # ✅ 添加 AI 回复到历史
            session["history"].append({"role": "assistant", "content": reply})

    chat_history = session.get("history", [SYSTEM_PROMPT])[1:]
    return render_template("chat.html", chat_history=chat_history, reply=reply)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
