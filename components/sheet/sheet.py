__all__ = (
    "BaseSheet",
    "OtpSheet",
)

from os.path import join, dirname, basename

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import mainthread
from kivy.clock import triggered
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    VariableListProperty,
    NumericProperty,
    StringProperty,
    BooleanProperty,
    ObjectProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.utils import platform

from components.behaviors import AdaptiveBehavior

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


def _handle_keyboard(self, _window, key, *_args):
    if key in [1073742106, 27] and self.auto_dismiss:
        self.dismiss()
        return True
    return False


ModalView._handle_keyboard = _handle_keyboard


class BaseSheet(ButtonBehavior, BoxLayout):
    __events__ = ("on_open", "on_dismiss")
    is_open = BooleanProperty(False)
    screen = ObjectProperty()
    radius = VariableListProperty(["30dp", "30dp", 0, 0])
    bottom_padding = NumericProperty("20dp")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.y = self._y
        self.modalview = ModalView(
            background_color=(0, 0, 0, 0),
            background="",
            overlay_color=(0, 0, 0, 0.4),
            on_dismiss=lambda _: self.dismiss(),
        )
        if platform == "android":
            from kvdroid.tools.display import get_navbar_height

            self.bottom_padding = self.bottom_padding + get_navbar_height()

    @mainthread
    def open(self, statusbar_color="black", navbar_color="white"):
        if self.is_open:
            return
        for child in Window.children:
            if child.__class__ == self.__class__:
                del self
                return
        self.modalview.open(animate=True)
        Window.add_widget(self)
        self._open(statusbar_color, navbar_color)

    def _open(self, sc, nc):
        anim = Animation(y=0, duration=0.2)
        anim.bind(on_complete=lambda *_: self.dispatch("on_open"))
        anim.start(self)
        self.is_open = True
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            change_statusbar_color([0, 0, 0, 0], sc)
            navbar_color([0, 0, 0, 0], nc)  #

    @mainthread
    def dismiss(self):
        if not self.is_open:
            return
        anim = Animation(y=-self.height - dp(50), duration=0.2)
        anim.bind(on_complete=self._dismiss)
        anim.start(self)
        self.is_open = False
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            app = App.get_running_app()
            change_statusbar_color(
                [0, 0, 0, 0],
                "black" if app.theme_cls.theme_style == "Light" else "white",
            )
            navbar_color(
                [0, 0, 0, 0],
                "black" if app.theme_cls.theme_style == "Light" else "white",
            )

    def _dismiss(self, *_):
        Window.remove_widget(self)
        self.modalview.dismiss()
        self.dispatch("on_dismiss")

    def on_open(self, *args):
        pass

    def on_dismiss(self, *args):
        pass


class OtpSheet(BaseSheet, AdaptiveBehavior):
    __events__ = ("on_submit_otp", "on_resend_otp")
    timeout = NumericProperty(60)
    phone_number = StringProperty()

    @triggered(1, True)
    def _countdown_callback(self):
        self.timeout -= 1
        if self.timeout == 0:
            self._countdown_callback.cancel()

    def on_open(self, *_):
        self._countdown_callback()

    def _dismiss(self, *_):
        super()._dismiss(*_)
        self._countdown_callback.cancel()

    def submit_otp(self):
        if self.ids.spinner.active:
            return
        self.ids.spinner.active = True
        otp = self.ids.otp.text
        self.dispatch("on_submit_otp", otp)

    def resend_otp(self):
        self.dispatch("on_resend_otp")
        self.timeout = self.property("timeout").defaultvalue
        self._countdown_callback()

    def stop_spinner(self):
        self.ids.spinner.active = False

    def on_submit_otp(self, otp):
        pass

    def on_resend_otp(self):
        pass
