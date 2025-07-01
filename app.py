from flask import Flask, send_from_directory
from flask_socketio import SocketIO, send
import os

app = Flask(__name__, static_folder='.', static_url_path='')
socketio = SocketIO(app, async_mode="eventlet")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('images', filename)

@socketio.on('message')
def handle_message(msg):
    send(msg, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    socketio.run(app, host='0.0.0.0', port=port)