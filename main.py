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
from kivy.metrics import dp

import datetime
import socketio

# =========================================
# SOCKET
# =========================================

sio = socketio.Client()

# =========================================
# WINDOW
# =========================================

Window.size = (360,640)

# =========================================
# USERS
# =========================================

users = [

    {
        "name":"Ali",
        "msg":"Hello Bhai",
        "time":"10:22 PM"
    },

    {
        "name":"Ahmed",
        "msg":"Kaha ho",
        "time":"9:10 PM"
    },

    {
        "name":"Farhan",
        "msg":"Class Chat",
        "time":"8:55 PM"
    },

    {
        "name":"Aman",
        "msg":"Online",
        "time":"Yesterday"
    }

]

# =========================================
# APP
# =========================================

class Chat(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"

        self.theme_cls.primary_palette = "Green"

        # =========================
        # SOCKET CONNECT
        # =========================

        try:

            sio.connect(
                "http://192.168.43.55:5000"
            )

            print("Socket Connected ✔")

        except Exception as e:

            print("Socket Error ❌", e)

        self.screen = MDScreen()

        self.home()

        return self.screen

    # =====================================
    # HOME SCREEN
    # =====================================

    def home(self):

        self.screen.clear_widgets()

        layout = MDBoxLayout(
            orientation='vertical'
        )

        # =================================
        # TOP BAR
        # =================================

        top = MDBoxLayout(

            adaptive_height=True,

            padding=dp(15),

            spacing=10

        )

        title = MDLabel(

            text="Class Chat",

            font_style="H4",

            theme_text_color="Primary"

        )

        camera = MDFloatingActionButton(
            icon="camera"
        )

        top.add_widget(title)

        top.add_widget(camera)

        layout.add_widget(top)

        # =================================
        # SEARCH
        # =================================

        search = MDTextField(

            hint_text="Search",

            size_hint_x=0.95,

            pos_hint={"center_x":0.5}

        )

        layout.add_widget(search)

        # =================================
        # CHAT LIST
        # =================================

        scroll = ScrollView()

        chat_list = MDList()

        for user in users:

            item = TwoLineAvatarIconListItem(

                text=
                user["name"],

                secondary_text=
                user["msg"] +
                "   ✓✓   " +
                user["time"]

            )

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

        # =================================
        # FLOAT BUTTON
        # =================================

        fab = MDFloatingActionButton(

            icon="message-plus",

            pos_hint={
                "center_x":0.88,
                "center_y":0.08
            }

        )

        self.screen.add_widget(layout)

        self.screen.add_widget(fab)

    # =====================================
    # OPEN CHAT SCREEN
    # =====================================

    def open_chat(self, instance):

        self.screen.clear_widgets()

        layout = MDBoxLayout(
            orientation='vertical'
        )

        # =================================
        # TOP BAR
        # =================================

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
            instance.text +
            " 🟢 Online",

            font_style="H6"

        )

        video = MDFloatingActionButton(
            icon="video"
        )

        call = MDFloatingActionButton(
            icon="phone"
        )

        top.add_widget(back)

        top.add_widget(title)

        top.add_widget(video)

        top.add_widget(call)

        layout.add_widget(top)

        # =================================
        # CHAT AREA
        # =================================

        self.chat_area = MDLabel(

            text=
            "💬 Welcome To Class Chat\n\n",

            halign="left"

        )

        scroll = ScrollView()

        scroll.add_widget(self.chat_area)

        layout.add_widget(scroll)

        # =================================
        # RECEIVE MESSAGE
        # =================================

        @sio.on("message")
        def on_message(data):

            try:

                self.chat_area.text += (

                    "👤 " +

                    data["sender"] +

                    ": " +

                    data["text"] +

                    "   ✓✓   " +

                    data["time"] +

                    "\n\n"

                )

            except:

                print(data)

        # =================================
        # BOTTOM BAR
        # =================================

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

        mic = MDFloatingActionButton(
            icon="microphone"
        )

        send.bind(
            on_press=self.send_message
        )

        mic.bind(
            on_press=self.voice_note
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
    # SEND MESSAGE
    # =====================================

    def send_message(self, obj):

        text = self.msg.text

        if text.strip() == "":
            return

        time = datetime.datetime.now().strftime("%I:%M %p")

        data = {

            "sender":"You",

            "text":text,

            "time":time

        }

        # =========================
        # SEND TO SERVER
        # =========================

        try:

            sio.emit(
                "message",
                data
            )

        except Exception as e:

            print("Send Error:", e)

        # =========================
        # SHOW OWN MESSAGE
        # =========================

        self.chat_area.text += (

            "🧑 You: " +

            text +

            "   ✓✓   " +

            time +

            "\n\n"

        )

        self.msg.text = ""

    # =====================================
    # VOICE NOTE
    # =====================================

    def voice_note(self, obj):

        self.chat_area.text += (
            "🎤 Voice Note Sent ✓✓\n\n"
        )

    # =====================================
    # BACK
    # =====================================

    def back(self, obj):

        self.home()

# =========================================
# RUN
# =========================================

Chat().run()
