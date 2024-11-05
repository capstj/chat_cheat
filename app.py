import socket
from flask import Flask, render_template, request
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

chat_history = {}
active_rooms = {}

port = 5000
@app.route('/')
def index():
    ip_address = get_local_ip()
    # Pass IP and port to the HTML template
    return render_template('index.html', server_ip=ip_address, server_port=port)


@socketio.on('connect')
def handle_connect():
    emit('activeRooms', list(active_rooms.keys()))


@socketio.on('joinRoom')
def handle_join_room(data):
    username = data['username']
    room = data['room']

    join_room(room)

    if room in active_rooms:
        active_rooms[room] += 1
    else:
        active_rooms[room] = 1

    emit('userJoined', username, room=room)

    emit('message', {
        'type': 'system',
        'content': f'{username} has joined the room.',
        'sender': 'System'
    }, room=room)

    if room in chat_history:
        for message in chat_history[room]:
            emit('message', message, room=request.sid)

    emit('activeRooms', list(active_rooms.keys()), broadcast=True)


@socketio.on('leaveRoom')
def handle_leave_room(data):
    username = data['username']
    room = data['room']

    leave_room(room)
    if room in active_rooms:
        active_rooms[room] -= 1
        if active_rooms[room] == 0:
            del active_rooms[room]

    emit('message', {
        'type': 'system',
        'content': f'{username} has left the room.',
        'sender': 'System'
    }, room=room)

    emit('activeRooms', list(active_rooms.keys()), broadcast=True)


@socketio.on('chatMessage')
def handle_message(data):
    room = data['room']
    if room not in chat_history:
        chat_history[room] = []

    chat_history[room].append(data)
    emit('message', data, room=room)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't have to be reachable
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


if __name__ == '__main__':
    ip_address = get_local_ip()
    print(f"Starting server on http://{ip_address}:{port}")
    socketio.run(app, host='0.0.0.0', port=port)
