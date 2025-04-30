import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, emit
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
active_rooms = {}

@app.route('/')
def index():
    token = str(uuid.uuid4())
    return redirect(url_for('chat', token=token, role='host'))

@app.route('/chat/<token>')
def chat(token):
    role = request.args.get('role', 'guest')
    return render_template('chat.html', token=token, role=role)

@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    role = data.get('role')

    if room not in active_rooms:
        active_rooms[room] = {'host': None, 'guest': None}

    current = active_rooms[room]

    if role == 'host':
        if current['host'] is not None:
            emit('access_denied', {'reason': 'Host already exists'}, room=request.sid)
            return
        current['host'] = request.sid
    elif role == 'guest':
        if current['guest'] is not None:
            emit('access_denied', {'reason': 'Guest already exists'}, room=request.sid)
            return
        current['guest'] = request.sid
    else:
        emit('access_denied', {'reason': 'Invalid role'}, room=request.sid)
        return

    join_room(room)
    emit('message', {
        'msg': f"{username} has joined the chat.",
        'username': 'System'
    }, room=room)

@socketio.on('message')
def handle_message(data):
    msg = data['msg'].strip()
    if len(msg) == 0 or len(msg) > 255:
        return
    emit('message', {
        'msg': msg,
        'username': data['username']
    }, room=data['room'])

@socketio.on('typing')
def handle_typing(data):
    emit('typing', {
        'username': data['username']
    }, room=data['room'], include_self=False)

@socketio.on('end_chat')
def handle_end_chat(data):
    emit('chat_ended', {}, room=data['room'])

@socketio.on('disconnect')
def handle_disconnect():
    for room, users in list(active_rooms.items()):
        if users.get("host") == request.sid:
            users["host"] = None
        elif users.get("guest") == request.sid:
            users["guest"] = None
        if users["host"] is None and users["guest"] is None:
            del active_rooms[room]
            break

if __name__ == '__main__':
    socketio.run(app, debug=True)