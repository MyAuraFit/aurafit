__all__ = ("CoinScreen",)

from os.path import join, dirname, basename
from kivy.lang import Builder
from features.basescreen import BaseScreen

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class CoinScreen(BaseScreen):
    pass
