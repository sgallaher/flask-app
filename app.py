from flask import Flask, render_template, redirect, url_for, request
import uuid
from flask_socketio import SocketIO, join_room, emit

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

# Dictionary to keep track of rooms and whether the session is active
active_sessions = {}

@app.route('/')
def index():
    # Generate a unique token
    token = str(uuid.uuid4())
    # The host is the first one to join
    return redirect(url_for('chat', token=token, role="host"))

@app.route('/chat/<token>')
def chat(token):
    role = request.args.get('role', 'guest')  # Default to 'guest'
    return render_template('chat.html', token=token, role=role)

# Handle user joining a room (either host or guest)
@socketio.on('join')
def handle_join(data):
    room = data['room']
    username = data['username']
    role = data['role']
    
    # Mark session as active when the host joins
    if role == 'host' and room not in active_sessions:
        active_sessions[room] = {'host': username, 'client': None, 'active': True}
    
    join_room(room)
    
    if role == 'host':
        emit('message', {'msg': f"{username} (Host) has joined the chat."}, room=room)
        emit('waiting', {'msg': 'Waiting for the client to join...'}, room=room)
    else:
        # Update active_sessions with the guest's information
        active_sessions[room]['client'] = username
        emit('message', {'msg': f"{username} (Guest) has joined the chat."}, room=room)
        emit('waiting', {'msg': f"{username} has joined the chat!"}, room=room)

# Handle real-time message sending
@socketio.on('message')
def handle_message(data):
    room = data['room']
    emit('message', {'msg': data['msg'], 'username': data['username']}, room=room)

# Handle typing indication
@socketio.on('user_typing')
def handle_typing(data):
    room = data['room']
    emit('user_typing', {'username': data['username']}, room=room)

# Handle session closure
@socketio.on('close_session')
def handle_close_session(data):
    room = data['room']
    emit('message', {'msg': 'The host has closed the session. You will be disconnected.'}, room=room)
    active_sessions[room]['active'] = False  # Mark the session as inactive
    socketio.disconnect()

# Handle user disconnecting
@socketio.on('disconnect')
def handle_disconnect():
    for room, session in active_sessions.items():
        if session['host'] == request.sid or session['client'] == request.sid:
            session['active'] = False
            break

if __name__ == '__main__':
    socketio.run(app, debug=True)
