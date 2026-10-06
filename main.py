from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ListProperty
from kivy.uix.screenmanager import Screen
import socket, threading, ipaddress

KV = r"""
#:import dp kivy.metrics.dp

<MainScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: dp(14)
        spacing: dp(10)
        canvas.before:
            Color:
                rgba: .055, .075, .11, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Label:
            text: "NetGuard"
            font_size: "26sp"
            bold: True
            color: .2, .75, 1, 1
            size_hint_y: None
            height: dp(45)

        Label:
            text: root.status
            color: .75, .8, .86, 1
            size_hint_y: None
            height: dp(30)

        GridLayout:
            cols: 2
            spacing: dp(10)
            size_hint_y: None
            height: dp(145)

            Button:
                text: "📶\\nالشبكة"
                font_size: "18sp"
                on_release: root.scan_network()
            Button:
                text: "📹\\nالكاميرات"
                font_size: "18sp"
                on_release: root.show_cameras()
            Button:
                text: "🛡️\\nالأمان"
                font_size: "18sp"
                on_release: root.security_check()
            Button:
                text: "⚙️\\nالإعدادات"
                font_size: "18sp"
                on_release: root.settings()

        Label:
            text: "الأجهزة المكتشفة"
            font_size: "19sp"
            bold: True
            size_hint_y: None
            height: dp(35)
            halign: "right"

        ScrollView:
            GridLayout:
                id: devices
                cols: 1
                spacing: dp(7)
                size_hint_y: None
                height: self.minimum_height

        Button:
            text: "فحص الشبكة"
            size_hint_y: None
            height: dp(52)
            on_release: root.scan_network()
"""

class MainScreen(Screen):
    status = StringProperty("جاهز — اضغط «فحص الشبكة» للبدء")

    def _local_network(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("192.0.2.1", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "192.168.1.1"
        finally:
            s.close()
        parts = ip.split(".")
        return ipaddress.ip_network(".".join(parts[:3]) + ".0/24", strict=False)

    def scan_network(self):
        self.status = "جاري فحص شبكتك المحلية..."
        self.ids.devices.clear_widgets()
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        net = self._local_network()
        found = []
        # فحص اتصال TCP محدود على منافذ شائعة، وليس اختراقًا أو تجاوزًا للحماية.
        ports = (80, 443, 554, 8080)
        for host in net.hosts():
            for port in ports:
                try:
                    with socket.create_connection((str(host), port), timeout=.12):
                        found.append(f"{host}  •  منفذ {port} مفتوح")
                        break
                except OSError:
                    pass
        Clock.schedule_once(lambda dt: self._show(found), 0)

    def _show(self, found):
        from kivy.uix.label import Label
        self.status = f"اكتمل الفحص — تم العثور على {len(found)} جهاز/خدمة"
        if not found:
            found = ["لم يتم العثور على خدمة شائعة مفتوحة."]
        for item in found:
            self.ids.devices.add_widget(
                Label(text=item, size_hint_y=None, height=40,
                      color=(.9,.93,.96,1), halign="right")
            )

    def show_cameras(self):
        self.status = "الكاميرات: سيتم اكتشاف ONVIF/NVR وربط RTSP في المرحلة التالية."

    def security_check(self):
        self.status = "فحص الأمان الأساسي جاهز — سنضيف تقرير المخاطر والتنبيهات."

    def settings(self):
        self.status = "الإعدادات: الشبكة، الكاميرات، VPN، والإشعارات."

class NetGuardApp(App):
    def build(self):
        Builder.load_string(KV)
        return MainScreen()

if __name__ == "__main__":
    NetGuardApp().run()
