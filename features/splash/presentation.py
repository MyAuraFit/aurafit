__all__ = ("SplashScreen",)

from pathlib import Path

from kivy.clock import triggered
from kivy.lang import Builder
from kivy.utils import platform

from features.basescreen import BaseScreen
from libs.googleauth import GoogleAuthMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class SplashScreen(BaseScreen, GoogleAuthMixin):
    @triggered(3, True)
    def animate_button(self):
        self.ids.btn.grow()

    def on_enter(self):
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            change_statusbar_color(
                [0, 0, 0, 0],
                "white",
            )
            navbar_color(
                [0, 0, 0, 0],
                "white",
            )
        self.animate_button()

    def on_leave(self):
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color
            from kvdroid.tools.darkmode import dark_mode

            change_statusbar_color(
                [0, 0, 0, 0],
                "white" if dark_mode() else "black",
            )
            navbar_color(
                [0, 0, 0, 0],
                "white" if dark_mode() else "black",
            )
        self.animate_button.cancel()
