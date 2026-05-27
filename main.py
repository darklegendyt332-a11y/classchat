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

# =========================================
# SOCKET
# =========================================

sio = socketio.Client()

Window.size = (360, 640)

# =========================================
# YOUR NUMBER
# =========================================

MY_NUMBER = "8052055136"

# =========================================
# CONTACTS
# =========================================

users = [

    {
        "name": "Farhan",
        "number": "9261413387",
        "msg": "Hello",
        "time": "10:22 PM"
    },

    {
        "name": "Ahmed",
        "number": "2222222222",
        "msg": "Kaha ho",
        "time": "9:10 PM"
    }

]

# =========================================
# APP
# =========================================

class Chat(MDApp):

    def build(self):

        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Green"

        self.current_user = ""
        self.current_number = ""

        # =================================
        # SOCKET CONNECT
        # =================================

        try:

            sio.connect(
                "https://classchat-fog5.onrender.com"
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
    # SOCKET EVENTS
    # =====================================

    def setup_socket_events(self):

        @sio.on("private_message")
        def private_message(data):

            try:

                sender = data["sender"]

                text = data["text"]

                time = data["time"]

                if hasattr(self, "chat_area"):

                    self.chat_area.text += (

                        "👤 " +

                        sender +

                        ": " +

                        text +

                        "   ✓✓   " +

                        time +

                        "\n\n"

                    )

            except Exception as e:

                print(e)

        # =================================
        # INCOMING CALL
        # =================================

        @sio.on("incoming_call")
        def incoming_call(data):

            caller = data["from"]

            self.incoming_call_screen(caller)

        # =================================
        # CALL ACCEPTED
        # =================================

        @sio.on("call_accepted")
        def call_accepted(data):

            self.open_call_ui()

    # =====================================
    # HOME
    # =====================================

    def home(self):

        self.screen.clear_widgets()

        layout = MDBoxLayout(
            orientation="vertical"
        )

        # =================================
        # TOP BAR
        # =================================

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

        # =================================
        # CHAT LIST
        # =================================

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

        self.screen.add_widget(layout)

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
            self.current_user +
            " 🟢 Online",

            font_style="H6"

        )

        # =================================
        # CALL BUTTON
        # =================================

        call = MDFloatingActionButton(
            icon="phone"
        )

        call.bind(
            on_press=self.start_call
        )

        top.add_widget(back)

        top.add_widget(title)

        top.add_widget(call)

        layout.add_widget(top)

        # =================================
        # CHAT AREA
        # =================================

        self.chat_area = MDLabel(

            text="💬 Welcome To Class Chat\n\n",

            halign="left"

        )

        scroll = ScrollView()

        scroll.add_widget(self.chat_area)

        layout.add_widget(scroll)

        # =================================
        # BOTTOM
        # =================================

        bottom = MDBoxLayout(

            adaptive_height=True,

            spacing=5,

            padding=5

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

        bottom.add_widget(self.msg)

        bottom.add_widget(send)

        layout.add_widget(bottom)

        self.screen.add_widget(layout)

    # =====================================
    # SEND MESSAGE
    # =====================================

    def send_message(self, obj):

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

        self.chat_area.text += (

            "🧑 You: " +

            text +

            "   ✓✓   " +

            time +

            "\n\n"

        )

        self.msg.text = ""

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
            "\n📞 Calling...\n\n"
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

        buttons = MDBoxLayout(

            adaptive_height=True,

            spacing=50,

            pos_hint={"center_x": 0.5}

        )

        # RED BUTTON

        reject = MDFloatingActionButton(

            icon="phone-hangup",

            md_bg_color=(1, 0, 0, 1)


        )

        # GREEN BUTTON

        accept = MDFloatingActionButton(

            icon="phone",

            md_bg_color=(0, 1, 0, 1)

        )

        reject.bind(
            on_press=self.reject_call
        )

        accept.bind(
            on_press=lambda x:
            self.accept_call(caller)
        )

        buttons.add_widget(reject)

        buttons.add_widget(accept)

        layout.add_widget(title)

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

    def reject_call(self, obj):

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

        end_call = MDFloatingActionButton(

            icon="phone-hangup",

            md_bg_color=(1, 0, 0, 1),

            pos_hint={"center_x": 0.5}

        )

        end_call.bind(
            on_press=self.end_call
        )

        layout.add_widget(title)

        layout.add_widget(end_call)

        self.screen.add_widget(layout)

    # =====================================
    # END CALL
    # =====================================

    def end_call(self, obj):

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
