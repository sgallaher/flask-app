import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, redirect, url_for, request
from flask_socketio import SocketIO, join_room, emit
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

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
    join_room(room)
    emit('message', {
        'msg': f"{data['username']} has joined the chat.",
        'username': 'System'
    }, room=room)

@socketio.on('message')
def handle_message(data):
    emit('message', {
        'msg': data['msg'],
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

if __name__ == '__main__':
    socketio.run(app, debug=True)
