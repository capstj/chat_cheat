from flask import Flask, render_template, request  # Import 'request' here
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('joinRoom')
def handle_join_room(data):
    username = data['username']
    room = data['room']
    join_room(room)
    emit('userJoined', username, room=room)

    emit('message', {
        'type': 'system',
        'content': f'{username} has joined the room.',
        'sender': 'System'
    }, room=room)

    if room in chat_history:
        for message in chat_history[room]:
            emit('message', message, room=request.sid)

@socketio.on('chatMessage')
def handle_message(data):
    room = data['room']
    if room not in chat_history:
        chat_history[room] = []

    chat_history[room].append(data)

    emit('message', data, room=room)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=3001)
