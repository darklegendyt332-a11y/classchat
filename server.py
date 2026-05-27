from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins="*")

# =========================
# USERS STORE
# =========================
users = {}

# =========================
# JOIN
# =========================
@socketio.on("join")
def join(data):
    number = data["number"]
    users[number] = request.sid
    join_room(number)
    print(number, "joined")

# =========================
# CHAT (UNCHANGED)
# =========================
@socketio.on("private_message")
def private_message(data):
    receiver = data["receiver"]
    emit("private_message", data, room=receiver)

# =========================
# 📞 CALL SYSTEM (NEW)
# =========================
@socketio.on("call_request")
def call_request(data):
    emit("incoming_call", data, room=data["to"])

@socketio.on("call_accept")
def call_accept(data):
    emit("call_accepted", data, room=data["to"])

# =========================
# 🌐 WEBRTC SIGNALING (NEW)
# =========================
@socketio.on("offer")
def offer(data):
    emit("offer", data, room=data["to"])

@socketio.on("answer")
def answer(data):
    emit("answer", data, room=data["to"])

@socketio.on("ice_candidate")
def ice_candidate(data):
    emit("ice_candidate", data, room=data["to"])

# =========================
# RUN
# =========================
socketio.run(app, host="0.0.0.0", port=5000)
