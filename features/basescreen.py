from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.utils import QueryDict


class ScreenData(QueryDict):
    pass


class BaseScreen(Screen):
    app = ObjectProperty(None)
    watched_ads = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._screen_data = ScreenData()

    def get_screen_data(self):
        return self._screen_data

    def set_screen_data(self, screen_data: ScreenData):
        self._screen_data = ScreenData(screen_data)

    @staticmethod
    def toast(text, length_long=True):
        from kvdroid.tools import toast

        toast(text, length_long)
