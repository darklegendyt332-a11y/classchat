from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.list import (
    MDList,
    TwoLineAvatarIconListItem,
    IconLeftWidget
)

from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

import socketio
import datetime
import threading
import asyncio

from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaPlayer, MediaRecorder

# =========================
# SOCKET
# =========================
sio = socketio.Client()

Window.size = (360, 640)

MY_NUMBER = "9261413387"

users = [
    {"name": "Ali", "number": "8052055136", "msg": "Hello", "time": "10:22 PM"},
    {"name": "Ahmed", "number": "2222222222", "msg": "Kaha ho", "time": "9:10 PM"},
    {"name": "Aman", "number": "3333333333", "msg": "Online", "time": "Yesterday"}
]

pc = None


class Chat(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"

        self.current_user = ""
        self.current_number = ""

        try:
            sio.connect("https://classchat-fog5.onrender.com")
            sio.emit("join", {"number": MY_NUMBER})
            print("Connected ✔")
        except Exception as e:
            print("Socket Error:", e)

        self.screen = MDScreen()
        self.home()
        return self.screen

    # =========================
    # HOME
    # =========================
    def home(self):
        self.screen.clear_widgets()

        layout = MDBoxLayout(orientation="vertical")

        top = MDBoxLayout(adaptive_height=True, padding=15, spacing=10)
        title = MDLabel(text="Class Chat", font_style="H4")
        camera = MDFloatingActionButton(icon="camera")

        top.add_widget(title)
        top.add_widget(camera)
        layout.add_widget(top)

        scroll = ScrollView()
        chat_list = MDList()

        for user in users:
            item = TwoLineAvatarIconListItem(
                text=user["name"],
                secondary_text=user["msg"] + " ✓✓ " + user["time"]
            )
            item.number = user["number"]

            icon = IconLeftWidget(icon="account-circle")
            item.add_widget(icon)

            item.bind(on_press=self.open_chat)
            chat_list.add_widget(item)

        scroll.add_widget(chat_list)
        layout.add_widget(scroll)

        fab = MDFloatingActionButton(
            icon="message-plus",
            pos_hint={"center_x": 0.88, "center_y": 0.08}
        )

        self.screen.add_widget(layout)
        self.screen.add_widget(fab)

    # =========================
    # OPEN CHAT
    # =========================
    def open_chat(self, instance):

        self.current_user = instance.text
        self.current_number = instance.number

        self.screen.clear_widgets()

        layout = MDBoxLayout(orientation="vertical")

        top = MDBoxLayout(adaptive_height=True, padding=10, spacing=10)

        back = MDFloatingActionButton(icon="arrow-left")
        back.bind(on_press=self.back)

        title = MDLabel(
            text=self.current_user + " 🟢 Online",
            font_style="H6"
        )

        video = MDFloatingActionButton(icon="video")
        call = MDFloatingActionButton(icon="phone")

        call.bind(on_press=self.start_call)
        video.bind(on_press=self.start_video_call)

        top.add_widget(back)
        top.add_widget(title)
        top.add_widget(video)
        top.add_widget(call)

        layout.add_widget(top)

        self.chat_area = MDLabel(
            text="💬 Welcome To Class Chat\n\n",
            halign="left"
        )

        scroll = ScrollView()
        scroll.add_widget(self.chat_area)
        layout.add_widget(scroll)

        @sio.on("private_message")
        def private_message(data):
            self.chat_area.text += f"👤 {data['sender']}: {data['text']} ✓✓ {data['time']}\n\n"

        @sio.on("incoming_call")
        def incoming_call(data):
            self.chat_area.text += f"\n📞 Incoming call from {data['from']}\n"

        @sio.on("call_accepted")
        def call_accepted(data):
            self.chat_area.text += "\n📲 Call Accepted\n"

        bottom = MDBoxLayout(adaptive_height=True, spacing=5, padding=5)

        self.msg = MDTextField(hint_text="Message")

        send = MDFloatingActionButton(icon="send")
        send.bind(on_press=self.send_message)

        bottom.add_widget(self.msg)
        bottom.add_widget(send)

        layout.add_widget(bottom)

        self.screen.add_widget(layout)

    # =========================
    # CHAT SEND
    # =========================
    def send_message(self, obj):

        text = self.msg.text
        if text.strip() == "":
            return

        time = datetime.datetime.now().strftime("%I:%M %p")

        sio.emit("private_message", {
            "sender": MY_NUMBER,
            "receiver": self.current_number,
            "text": text,
            "time": time
        })

        self.chat_area.text += f"🧑 You: {text} ✓✓ {time}\n\n"
        self.msg.text = ""

    # =========================
    # 📞 CALL REQUEST
    # =========================
    def start_call(self, obj):

        sio.emit("call_request", {
            "from": MY_NUMBER,
            "to": self.current_number,
            "type": "audio"
        })

        threading.Thread(target=self.create_offer, daemon=True).start()

        self.chat_area.text += "\n📞 Starting voice call...\n"

    def start_video_call(self, obj):
        sio.emit("call_request", {
            "from": MY_NUMBER,
            "to": self.current_number,
            "type": "video"
        })

    # =========================
    # 🌐 WEBRTC OFFER (REAL CALL START)
    # =========================
    def create_offer(self):

        global pc
        pc = RTCPeerConnection()

        player = MediaPlayer(None)  # microphone

        if player and player.audio:
            pc.addTrack(player.audio)

        async def run():
            offer = await pc.createOffer()
            await pc.setLocalDescription(offer)

            sio.emit("offer", {
                "from": MY_NUMBER,
                "to": self.current_number,
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            })

        asyncio.run(run())

    # =========================
    # 📲 RECEIVE OFFER
    # =========================
    @sio.on("offer")
    def on_offer(data):

        async def handle():

            global pc
            pc = RTCPeerConnection()

            desc = RTCSessionDescription(
                sdp=data["sdp"],
                type=data["type"]
            )

            await pc.setRemoteDescription(desc)

            recorder = MediaRecorder("default")

            @pc.on("track")
            def on_track(track):
                recorder.addTrack(track)

            await recorder.start()

            answer = await pc.createAnswer()
            await pc.setLocalDescription(answer)

            sio.emit("answer", {
                "from": MY_NUMBER,
                "to": data["from"],
                "sdp": pc.localDescription.sdp,
                "type": pc.localDescription.type
            })

        asyncio.run(handle())

    # =========================
    # 📡 ANSWER RECEIVE
    # =========================
    @sio.on("answer")
    def on_answer(data):

        async def handle():
            global pc

            desc = RTCSessionDescription(
                sdp=data["sdp"],
                type=data["type"]
            )

            await pc.setRemoteDescription(desc)

        asyncio.run(handle())

    # =========================
    # BACK
    # =========================
    def back(self, obj):
        self.home()


Chat().run()
