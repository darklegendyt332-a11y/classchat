from flask import Flask, request
from flask_socketio import SocketIO, emit

# =========================================
# FLASK
# =========================================

app = Flask(__name__)

app.config["SECRET_KEY"] = "classchat"

socketio = SocketIO(

    app,

    cors_allowed_origins="*",

    async_mode="threading"

)

# =========================================
# USERS
# =========================================

connected_users = {}

# =========================================
# CONNECT
# =========================================

@socketio.on("connect")
def connect():

    print("User Connected ✔")

# =========================================
# DISCONNECT
# =========================================

@socketio.on("disconnect")
def disconnect():

    remove = None

    for number, sid in connected_users.items():

        if sid == request.sid:

            remove = number

            break

    if remove:

        del connected_users[remove]

        print(remove, "Disconnected ❌")

# =========================================
# JOIN
# =========================================

@socketio.on("join")
def join(data):

    number = data.get("number")

    connected_users[number] = request.sid

    print(number, "Joined ✔")

# =========================================
# PRIVATE MESSAGE
# =========================================

@socketio.on("private_message")
def private_message(data):

    try:

        receiver = data.get("receiver")

        sender = data.get("sender")

        text = data.get("text")

        time = data.get("time")

        print(f"{sender} -> {receiver}: {text}")

        # ================================
        # SEND TO RECEIVER
        # ================================

        if receiver in connected_users:

            emit(

                "private_message",

                {
                    "sender": sender,
                    "text": text,
                    "time": time
                },

                to=connected_users[receiver]

            )

        # ================================
        # DELIVERY STATUS
        # ================================

        emit(

            "message_sent",

            {
                "status": "success"
            },

            to=request.sid

        )

    except Exception as e:

        print("Message Error:", e)

# =========================================
# CALL REQUEST
# =========================================

@socketio.on("call_request")
def call_request(data):

    try:

        caller = data.get("from")

        receiver = data.get("to")

        print(f"Call Request {caller} -> {receiver}")

        if receiver in connected_users:

            emit(

                "incoming_call",

                {
                    "from": caller
                },

                to=connected_users[receiver]

            )

    except Exception as e:

        print("Call Request Error:", e)

# =========================================
# CALL ACCEPT
# =========================================

@socketio.on("call_accept")
def call_accept(data):

    try:

        caller = data.get("to")

        accepter = data.get("from")

        print(f"Call Accepted {accepter}")

        if caller in connected_users:

            emit(

                "call_accepted",

                {
                    "from": accepter
                },

                to=connected_users[caller]

            )

    except Exception as e:

        print("Call Accept Error:", e)

# =========================================
# CALL REJECT
# =========================================

@socketio.on("call_reject")
def call_reject(data):

    try:

        caller = data.get("to")

        rejecter = data.get("from")

        print(f"Call Rejected {rejecter}")

        if caller in connected_users:

            emit(

                "call_rejected",

                {
                    "from": rejecter
                },

                to=connected_users[caller]

            )

    except Exception as e:

        print("Call Reject Error:", e)

# =========================================
# END CALL
# =========================================

@socketio.on("end_call")
def end_call(data):

    try:

        receiver = data.get("to")

        sender = data.get("from")

        print(f"Call Ended {sender}")

        if receiver in connected_users:

            emit(

                "call_ended",

                {
                    "from": sender
                },

                to=connected_users[receiver]

            )

    except Exception as e:

        print("End Call Error:", e)

# =========================================
# HOME ROUTE
# =========================================

@app.route("/")
def home():

    return "Class Chat Server Running ✔"

# =========================================
# RUN SERVER
# =========================================

if __name__ == "__main__":

    print("=================================")
    print(" Class Chat Server Started ✔ ")
    print("=================================")

    socketio.run(

        app,

        host="0.0.0.0",

        port=5000,

        debug=True

    )
