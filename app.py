from flask import Flask, send_from_directory
from flask_socketio import SocketIO, send
import os
import openai  # pip install openai

app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app, async_mode="eventlet")

# Set your OpenAI API key as an environment variable (OPENAI_API_KEY)
openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@socketio.on('message')
def handle_message(msg):
    # Send user message to all
    send(msg, broadcast=True)
    # Get a helpful reply from GPT
    bot_reply = get_gpt_response(msg)
    # Send the bot's reply as a new chat message
    if bot_reply:
        send(f"بوت شهد وعدي: {bot_reply}", broadcast=True)

def get_gpt_response(user_message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "أنت بوت دردشة ذكي اسمه شهد وعدي. ساعد المستخدم في كل ما يحتاجه وكن ودوداً ومفيداً. يمكنك الإجابة عن أي سؤال في أي مجال."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=150,
            temperature=0.85,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI error: {e}")
        return "عذراً، حدث خطأ تقني. حاول مرة أخرى."

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    socketio.run(app, host='0.0.0.0', port=port)
