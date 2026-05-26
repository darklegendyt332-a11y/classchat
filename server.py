from flask import Flask
from flask_socketio import SocketIO, send

app = Flask(__name__)

socketio = SocketIO(app)

@socketio.on("message")
def handle(msg):

    print(msg)

    send(msg, broadcast=True)

socketio.run(app, host="0.0.0.0", port=5000)
