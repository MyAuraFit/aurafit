from importlib import import_module

from kivy.app import App
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.logger import Logger
from kivy.properties import DictProperty, ObjectProperty, ListProperty, StringProperty
from kivy.uix.screenmanager import ScreenManager
from kivy.utils import platform

from components.bar import win_md_bnb
from features.basescreen import ScreenData


class AppScreenManager(ScreenManager):
    """
    A custom ScreenManager that loads screens lazily.
    """

    screen_config = DictProperty(
        {
            "login screen": ("features.login", "LoginScreen"),
            "home screen": ("features.home", "HomeScreen"),
            "wardrobe screen": ("features.wardrobe", "WardrobeScreen"),
            "outfits screen": ("features.outfits", "OutfitsScreen"),
            "autofit screen": ("features.autofit", "AutofitScreen"),
            "instantfit screen": ("features.instantfit", "InstantfitScreen"),
            "result screen": ("features.result", "ResultScreen"),
            "coin screen": ("features.coin", "CoinScreen"),
            "account screen": ("features.account", "AccountScreen"),
            "view screen": ("features.view", "ViewScreen"),
            "upload screen": ("features.upload", "UploadScreen"),
        }
    )
    app = ObjectProperty()
    previous_screens = ListProperty()
    next_screen = StringProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self._go_back)

    def create_screen_from_name(self, name):
        if not self.has_screen(name):
            presentation_module_path, presentation_class_name = self.screen_config[name]
            presentation_module = import_module(
                presentation_module_path + ".presentation"
            )
            presentation_class = getattr(presentation_module, presentation_class_name)
            presentation = presentation_class(app=App.get_running_app())
            self.add_widget(presentation)

    @mainthread
    def switch_screen(self, name, *, screen_data: ScreenData = None):
        self.create_screen_from_name(name)
        target_screen = self.get_screen(name)
        if screen_data is not None:
            target_screen.set_screen_data(screen_data)
        self.current = name

    def on_current(self, instance, value):
        """
        Loads a screen dynamically if it hasn't been loaded yet.
        """

        self.create_screen_from_name(value)
        if self.next_screen:
            self.previous_screens.append(self.next_screen)
        self.next_screen = value
        supra = super().on_current(instance, value)
        return supra

    def go_back(self):
        self.next_screen = ""
        if not self.previous_screens:
            Logger.warning("ScreenManager: No previous screen to load")
            return
        self.current = self.previous_screens.pop()

    def _go_back(self, _window, key, *_args):
        if key in [1073742106, 27]:
            self.next_screen = ""
            if len(self.previous_screens) == 0 and platform == "android":
                self.app.pause()
            else:
                if self.previous_screens[-1] in [
                    "signup screen",
                    "login screen",
                ]:
                    self.app.pause()
                    return True
                self.current = self.previous_screens.pop()
                for child in win_md_bnb.bar.children:
                    if self.current == child.name:
                        child.dispatch("on_release")
            return True
        return False
