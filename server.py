from flask import Flask
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)

socketio = SocketIO(
    app,
    cors_allowed_origins="*"
)

# =====================================
# USER JOIN
# =====================================

@socketio.on("join")
def join(data):

    number = data["number"]

    join_room(number)

    print(number, "joined")

# =====================================
# PRIVATE MESSAGE
# =====================================

@socketio.on("private_message")
def private_message(data):

    receiver = data["receiver"]

    emit(
        "private_message",
        data,
        room=receiver
    )

# =====================================
# RUN
# =====================================

socketio.run(
    app,
    host="0.0.0.0",
    port=5000
)
