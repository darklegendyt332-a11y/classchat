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
from kivy.clock import Clock

import socketio
import datetime
import json
import os

# =========================================
# SOCKET
# =========================================

sio = socketio.Client()

Window.size = (360, 640)

# =========================================
# YOUR NUMBER
# =========================================

MY_NUMBER = "9261413387"

# =========================================
# CONTACTS
# =========================================

users = [

    {
        "name": "Farhan",
        "number": "8052055136",
        "msg": "Online",
        "time": "Now"
    },

    {
        "name": "Ahmed",
        "number": "2222222222",
        "msg": "Hello",
        "time": "9:10 PM"
    }

]

# =========================================
# SAVE FILE
# =========================================

CHAT_FILE = "messages.json"

# =========================================
# APP
# =========================================

class Chat(MDApp):

    # =====================================
    # BUILD
    # =====================================

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"

        self.current_user = ""
        self.current_number = ""

        self.messages = self.load_messages()

        # =================================
        # SOCKET CONNECT
        # =================================

        try:

            sio.connect(
                "http://192.168.43.55:5000"
            )

            sio.emit(
                "join",
                {
                    "number": MY_NUMBER
                }
            )

            print("Connected ✔")

        except Exception as e:

            print("Socket Error:", e)

        self.screen = MDScreen()

        self.setup_socket_events()

        self.home()

        return self.screen

    # =====================================
    # LOAD MESSAGES
    # =====================================

    def load_messages(self):

        if os.path.exists(CHAT_FILE):

            try:

                with open(CHAT_FILE, "r") as file:

                    return json.load(file)

            except:

                return {}

        return {}

    # =====================================
    # SAVE MESSAGES
    # =====================================

    def save_messages(self):

        with open(CHAT_FILE, "w") as file:

            json.dump(self.messages, file)

    # =====================================
    # STORE MESSAGE
    # =====================================

    def store_message(self, user, msg):

        if user not in self.messages:

            self.messages[user] = []

        self.messages[user].append(msg)

        self.save_messages()

    # =====================================
    # SOCKET EVENTS
    # =====================================

    def setup_socket_events(self):

        # =================================
        # RECEIVE MESSAGE
        # =================================

        @sio.on("private_message")
        def private_message(data):

            try:

                sender = data["sender"]

                text = data["text"]

                time = data["time"]

                message = (

                    "👤 " +
                    sender +
                    ": " +
                    text +
                    "   ✓✓   " +
                    time

                )

                self.store_message(sender, message)

                Clock.schedule_once(
                    lambda dt: self.safe_add_message(message)
                )

            except Exception as e:

                print("Receive Error:", e)

        # =================================
        # INCOMING CALL
        # =================================

        @sio.on("incoming_call")
        def incoming_call(data):

            caller = data["from"]

            Clock.schedule_once(

                lambda dt:

                self.incoming_call_screen(caller)

            )

        # =================================
        # CALL ACCEPTED
        # =================================

        @sio.on("call_accepted")
        def call_accepted(data):

            Clock.schedule_once(

                lambda dt:

                self.open_call_ui()

            )

        # =================================
        # CALL REJECTED
        # =================================

        @sio.on("call_rejected")
        def call_rejected(data):

            Clock.schedule_once(

                lambda dt:

                self.call_rejected_ui()

            )

        # =================================
        # CALL ENDED
        # =================================

        @sio.on("call_ended")
        def call_ended(data):

            Clock.schedule_once(

                lambda dt:

                self.home()

            )

    # =====================================
    # HOME
    # =====================================

    def home(self):

        self.screen.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical"
        )

        top = MDBoxLayout(

            adaptive_height=True,

            padding=15,

            spacing=10

        )

        title = MDLabel(

            text="Class Chat",

            font_style="H4"

        )

        camera = MDFloatingActionButton(
            icon="camera"
        )

        top.add_widget(title)

        top.add_widget(camera)

        layout.add_widget(top)

        search = MDTextField(

            hint_text="Search",

            size_hint_x=0.95,

            pos_hint={"center_x": 0.5}

        )

        layout.add_widget(search)

        scroll = ScrollView()

        chat_list = MDList()

        for user in users:

            item = TwoLineAvatarIconListItem(

                text=user["name"],

                secondary_text=
                user["msg"] +
                "   ✓✓   " +
                user["time"]

            )

            item.number = user["number"]

            icon = IconLeftWidget(
                icon="account-circle"
            )

            item.add_widget(icon)

            item.bind(
                on_press=self.open_chat
            )

            chat_list.add_widget(item)

        scroll.add_widget(chat_list)

        layout.add_widget(scroll)

        fab = MDFloatingActionButton(

            icon="message-plus",

            pos_hint={
                "center_x": 0.88,
                "center_y": 0.08
            }

        )

        self.screen.add_widget(layout)

        self.screen.add_widget(fab)

    # =====================================
    # OPEN CHAT
    # =====================================

    def open_chat(self, instance):

        self.current_user = instance.text

        self.current_number = instance.number

        self.screen.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical"
        )

        top = MDBoxLayout(

            adaptive_height=True,

            padding=10,

            spacing=10

        )

        back = MDFloatingActionButton(
            icon="arrow-left"
        )

        back.bind(
            on_press=self.back
        )

        title = MDLabel(

            text=
            self.current_user +
            " 🟢 Online",

            font_style="H6"

        )

        video = MDFloatingActionButton(
            icon="video"
        )

        call = MDFloatingActionButton(
            icon="phone"
        )

        call.bind(
            on_press=self.start_call
        )

        top.add_widget(back)

        top.add_widget(title)

        top.add_widget(video)

        top.add_widget(call)

        layout.add_widget(top)

        self.chat_area = MDLabel(

            text="",

            halign="left"

        )

        # LOAD OLD CHAT

        if self.current_number in self.messages:

            for msg in self.messages[self.current_number]:

                self.chat_area.text += msg + "\n\n"

        scroll = ScrollView()

        scroll.add_widget(self.chat_area)

        layout.add_widget(scroll)

        bottom = MDBoxLayout(

            adaptive_height=True,

            spacing=5,

            padding=5

        )

        emoji = MDFloatingActionButton(
            icon="emoticon"
        )

        attach = MDFloatingActionButton(
            icon="paperclip"
        )

        camera = MDFloatingActionButton(
            icon="camera"
        )

        self.msg = MDTextField(
            hint_text="Message"
        )

        send = MDFloatingActionButton(
            icon="send"
        )

        send.bind(
            on_press=self.send_message
        )

        mic = MDFloatingActionButton(
            icon="microphone"
        )

        bottom.add_widget(emoji)

        bottom.add_widget(attach)

        bottom.add_widget(camera)

        bottom.add_widget(self.msg)

        bottom.add_widget(send)

        bottom.add_widget(mic)

        layout.add_widget(bottom)

        self.screen.add_widget(layout)

    # =====================================
    # SAFE MESSAGE UI
    # =====================================

    def safe_add_message(self, message):

        try:

            if hasattr(self, "chat_area"):

                self.chat_area.text += (
                    message + "\n\n"
                )

        except Exception as e:

            print("UI Error:", e)

    # =====================================
    # SEND MESSAGE
    # =====================================

    def send_message(self, obj):

        try:

            text = self.msg.text

            if text.strip() == "":
                return

            time = datetime.datetime.now().strftime(
                "%I:%M %p"
            )

            data = {

                "sender": MY_NUMBER,

                "receiver": self.current_number,

                "text": text,

                "time": time

            }

            sio.emit(
                "private_message",
                data
            )

            message = (

                "🧑 You: " +

                text +

                "   ✓✓   " +

                time

            )

            self.store_message(
                self.current_number,
                message
            )

            if hasattr(self, "chat_area"):

                self.chat_area.text += (
                    message + "\n\n"
                )

            self.msg.text = ""

            print("Message Sent ✔")

        except Exception as e:

            print("Send Error:", e)

    # =====================================
    # START CALL
    # =====================================

    def start_call(self, obj):

        sio.emit(

            "call_request",

            {

                "from": MY_NUMBER,

                "to": self.current_number

            }

        )

        self.chat_area.text += (

            "\n📞 Calling " +

            self.current_user +

            "...\n\n"

        )

    # =====================================
    # INCOMING CALL SCREEN
    # =====================================

    def incoming_call_screen(self, caller):

        self.screen.clear_widgets()

        layout = MDBoxLayout(

            orientation="vertical",

            spacing=40,

            padding=40

        )

        title = MDLabel(

            text=f"📞 {caller} Calling...",

            halign="center",

            font_style="H4"

        )

        subtitle = MDLabel(

            text="Incoming Voice Call",

            halign="center"

        )

        buttons = MDBoxLayout(

            adaptive_height=True,

            spacing=60,

            pos_hint={"center_x": 0.5}

        )

        reject = MDFloatingActionButton(

            icon="phone-hangup",

            md_bg_color=(1, 0, 0, 1)

        )

        accept = MDFloatingActionButton(

            icon="phone",

            md_bg_color=(0, 1, 0, 1)

        )

        reject.bind(
            on_press=lambda x:
            self.reject_call(caller)
        )

        accept.bind(
            on_press=lambda x:
            self.accept_call(caller)
        )

        buttons.add_widget(reject)

        buttons.add_widget(accept)

        layout.add_widget(title)

        layout.add_widget(subtitle)

        layout.add_widget(buttons)

        self.screen.add_widget(layout)

    # =====================================
    # ACCEPT CALL
    # =====================================

    def accept_call(self, caller):

        sio.emit(

            "call_accept",

            {

                "from": MY_NUMBER,

                "to": caller

            }

        )

        self.open_call_ui()

    # =====================================
    # REJECT CALL
    # =====================================

    def reject_call(self, caller):

        sio.emit(

            "call_reject",

            {

                "from": MY_NUMBER,

                "to": caller

            }

        )

        self.home()

    # =====================================
    # CALL UI
    # =====================================

    def open_call_ui(self):

        self.screen.clear_widgets()

        layout = MDBoxLayout(

            orientation="vertical",

            spacing=40,

            padding=40

        )

        title = MDLabel(

            text="📞 Call Connected",

            halign="center",

            font_style="H4"

        )

        subtitle = MDLabel(

            text="Voice Call Running...",

            halign="center"

        )

        end_call = MDFloatingActionButton(

            icon="phone-hangup",

            md_bg_color=(1, 0, 0, 1),

            pos_hint={"center_x": 0.5}

        )

        end_call.bind(
            on_press=self.end_call
        )

        layout.add_widget(title)

        layout.add_widget(subtitle)

        layout.add_widget(end_call)

        self.screen.add_widget(layout)

    # =====================================
    # CALL REJECTED UI
    # =====================================

    def call_rejected_ui(self):

        try:

            if hasattr(self, "chat_area"):

                self.chat_area.text += "\n❌ Call Rejected\n\n"

        except Exception as e:

            print(e)

    # =====================================
    # END CALL
    # =====================================

    def end_call(self, obj):

        sio.emit(

            "end_call",

            {

                "from": MY_NUMBER,

                "to": self.current_number

            }

        )

        self.home()

    # =====================================
    # BACK
    # =====================================

    def back(self, obj):

        self.home()

# =========================================
# RUN
# =========================================

Chat().run()
