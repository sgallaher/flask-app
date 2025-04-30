from flask import Flask, render_template, redirect, url_for
import uuid
from flask_socketio import SocketIO, join_room, emit

app=Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    token = str(uuid.uuid4())
    return redirect(url_for('chat', token=token))

@app.route('/chat/<token>')
def chat(token):
    return render_template('chat.html', token=token)

@socketio.on('join')
def handle_join(data):
    room=data['room']
    join_room(room)
    emit('message', {'msg': f"{data['username']} has joined the chat."}, room=room)


@socketio.on('message')
def handle_message(data):
    emit('message', data, room=data['room'])

if __name__ == '__main__':
    socketio.run(app, debug=True)