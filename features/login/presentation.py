__all__ = ("LoginScreen",)

from pathlib import Path

from kivy.lang import Builder

from features.basescreen import BaseScreen
from libs.googleauth import GoogleAuthMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class LoginScreen(GoogleAuthMixin, BaseScreen):
    pass
