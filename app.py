import os
import re
import logging
from flask import Flask, send_from_directory, request, jsonify
from flask_socketio import SocketIO, send
import openai

def create_app():
    app = Flask(__name__, static_folder='.', static_url_path='')
    socketio = SocketIO(app, async_mode="eventlet", cors_allowed_origins="*")
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    app.logger = logging.getLogger("chatapp")

    # Rate limit state - very simple per-process (not per-user)
    from collections import deque
    import time
    recent_messages = deque(maxlen=5)  # store last 5 timestamps

    @app.route('/')
    def index():
        return send_from_directory('.', 'index.html')

    @app.route('/images/<path:filename>')
    def serve_image(filename):
        return send_from_directory('images', filename)

    @app.route('/health')
    def health():
        return jsonify({'status': 'ok'})

    def sanitize_message(msg):
        # Remove HTML tags for safety
        msg = re.sub(r'<[^>]*?>', '', msg)
        return msg.strip()

    @socketio.on('message')
    def handle_message(msg):
        clean_msg = sanitize_message(msg)
        if not clean_msg:
            return  # don't send empty messages

        send(clean_msg, broadcast=True)

        # Rate limiting: allow 1 msg per second (5 msgs in 5 secs)
        now = time.time()
        recent_messages.append(now)
        if len(recent_messages) == 5 and now - recent_messages[0] < 5:
            app.logger.warning("Rate limit hit. Too many messages.")
            send("بوت شهد وعدي: الرجاء الانتظار قليلاً قبل إرسال رسالة أخرى.", broadcast=True)
            return

        bot_reply = get_gpt_response(clean_msg, app)
        if bot_reply:
            send(f"بوت شهد وعدي: {bot_reply}", broadcast=True)

    def get_gpt_response(user_message, app):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "أنت بوت دردشة ذكي اسمه شهد وعدي. ساعد المستخدم في كل ما يحتاجه وكن ودوداً ومفيداً. يمكنك الإجابة عن أي سؤال في أي مجال."},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.85,
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            app.logger.error(f"OpenAI API error: {e}")
            return "عذراً، حدث خطأ في الاتصال بالذكاء الاصطناعي. حاول لاحقاً."
        except Exception as e:
            app.logger.error(f"Unknown error: {e}")
            return "عذراً، حدث خطأ تقني غير متوقع. حاول لاحقاً."

    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    port = int(os.environ.get("PORT", 8000))
    socketio.run(app, host='0.0.0.0', port=port)
