__all__ = ("LoginScreen",)

from os.path import join, dirname, basename

from kivy.lang import Builder

from features.basescreen import BaseScreen
from libs.googleauth import GoogleAuthMixin

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class LoginScreen(GoogleAuthMixin, BaseScreen):
    pass
