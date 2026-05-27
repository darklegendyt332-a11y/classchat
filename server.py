from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room
import json
import os

# =========================================
# APP
# =========================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "classchat"

socketio = SocketIO(

    app,

    cors_allowed_origins="*"

)

# =========================================
# USERS
# =========================================

online_users = {}

# =========================================
# CREATE MESSAGE FILE
# =========================================

if not os.path.exists("messages.json"):

    with open("messages.json", "w") as f:

        json.dump([], f)

# =========================================
# SAVE MESSAGE
# =========================================

def save_message(data):

    with open("messages.json", "r") as f:

        messages = json.load(f)

    messages.append(data)

    with open("messages.json", "w") as f:

        json.dump(messages, f)

# =========================================
# HOME
# =========================================

@app.route("/")
def home():

    return "Class Chat Server Running ✔"

# =========================================
# USER JOIN
# =========================================

@socketio.on("join")
def join(data):

    try:

        number = data["number"]

        online_users[number] = request.sid

        join_room(number)

        print(f"{number} joined ✔")

        emit(

            "user_online",

            {
                "number": number
            },

            broadcast=True

        )

    except Exception as e:

        print("Join Error:", e)

# =========================================
# PRIVATE MESSAGE
# =========================================

@socketio.on("private_message")
def private_message(data):

    try:

        receiver = data["receiver"]

        # SAVE MESSAGE
        save_message(data)

        # SEND REALTIME
        emit(

            "private_message",

            data,

            room=receiver

        )

        print(

            f"MSG {data['sender']} -> {receiver}"

        )

    except Exception as e:

        print("Message Error:", e)

# =========================================
# GET OLD MESSAGES
# =========================================

@socketio.on("get_messages")
def get_messages(data):

    try:

        user1 = data["user1"]

        user2 = data["user2"]

        with open("messages.json", "r") as f:

            messages = json.load(f)

        chat = []

        for msg in messages:

            if (

                (
                    msg["sender"] == user1
                    and
                    msg["receiver"] == user2
                )

                or

                (
                    msg["sender"] == user2
                    and
                    msg["receiver"] == user1
                )

            ):

                chat.append(msg)

        emit(

            "old_messages",

            chat

        )

    except Exception as e:

        print("Get Messages Error:", e)

# =========================================
# CALL REQUEST
# =========================================

@socketio.on("call_request")
def call_request(data):

    try:

        emit(

            "incoming_call",

            data,

            room=data["to"]

        )

        print(

            f"CALL {data['from']} -> {data['to']}"

        )

    except Exception as e:

        print("Call Request Error:", e)

# =========================================
# CALL ACCEPT
# =========================================

@socketio.on("call_accept")
def call_accept(data):

    try:

        emit(

            "call_accepted",

            data,

            room=data["to"]

        )

        print(

            f"CALL ACCEPTED {data['from']}"

        )

    except Exception as e:

        print("Call Accept Error:", e)

# =========================================
# CALL REJECT
# =========================================

@socketio.on("call_reject")
def call_reject(data):

    try:

        emit(

            "call_rejected",

            data,

            room=data["to"]

        )

        print(

            f"CALL REJECTED {data['from']}"

        )

    except Exception as e:

        print("Call Reject Error:", e)

# =========================================
# END CALL
# =========================================

@socketio.on("end_call")
def end_call(data):

    try:

        emit(

            "call_ended",

            data,

            room=data["to"]

        )

        print(

            f"CALL ENDED {data['from']}"

        )

    except Exception as e:

        print("End Call Error:", e)

# =========================================
# TYPING
# =========================================

@socketio.on("typing")
def typing(data):

    try:

        emit(

            "typing",

            data,

            room=data["to"]

        )

    except Exception as e:

        print("Typing Error:", e)

# =========================================
# STOP TYPING
# =========================================

@socketio.on("stop_typing")
def stop_typing(data):

    try:

        emit(

            "stop_typing",

            data,

            room=data["to"]

        )

    except Exception as e:

        print("Stop Typing Error:", e)

# =========================================
# DISCONNECT
# =========================================

@socketio.on("disconnect")
def disconnect():

    try:

        disconnected_user = None

        for number, sid in online_users.items():

            if sid == request.sid:

                disconnected_user = number

                break

        if disconnected_user:

            del online_users[disconnected_user]

            print(f"{disconnected_user} disconnected ❌")

            emit(

                "user_offline",

                {
                    "number": disconnected_user
                },

                broadcast=True

            )

    except Exception as e:

        print("Disconnect Error:", e)

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    socketio.run(

        app,

        host="0.0.0.0",

        port=5000,

        debug=True

    )
