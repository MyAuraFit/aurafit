__all__ = (
    "BaseSheet",
    "OtpSheet",
)

from pathlib import Path

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import mainthread
from kivy.clock import triggered
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.properties import (
    VariableListProperty,
    NumericProperty,
    StringProperty,
    BooleanProperty,
    ObjectProperty,
    ListProperty,
    DictProperty,
)
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.utils import platform

from components.behaviors import AdaptiveBehavior
from components.label import CustomLabel

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


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


class MoodOccasionSelectionSheet(BaseSheet):
    group = StringProperty()
    title = StringProperty()
    occasion = ListProperty(
        [
            "Birthday Party",
            "Date Night",
            "Wedding",
            "Night Out",
            "Casual Outing",
            "Work Meeting",
            "Office Day",
            "Interview",
            "Dinner",
            "Lunch",
            "Brunch",
            "Travel",
            "Airport Outfit",
            "Beach",
            "Pool Party",
            "Gym / Workout",
            "Sports Event",
            "Concert",
            "Festival",
            "Religious Service",
            "Traditional Event",
            "Graduation",
            "Photoshoot",
            "Shopping",
            "House Party",
            "Romantic Evening",
            "Stay Home / Lounge",
        ]
    )
    mood = DictProperty(
        {
            "Social / Party": [
                "confident",
                "bold",
                "playful",
                "flirty",
                "energetic",
                "expressive",
            ],
            "Romantic / Date": [
                "romantic",
                "seductive",
                "charming",
                "passionate",
                "intimate",
                "alluring",
                "soft",
                "sweet",
            ],
            "Professional / Work": [
                "business",
                "sharp",
                "powerful",
                "polished",
                "elegant",
                "dignified",
                "minimal",
                "authoritative",
            ],
            "Casual / Everyday": [
                "casual",
                "relaxed",
                "comfortable",
                "unstructured",
                "loose",
                "informal",
                "unconventional",
                "unstructured",
                "natural",
                "chill",
                "effortless",
            ],
            "Fashion / Trendy": [
                "edgy",
                "stylish",
                "modern",
                "experimental",
                "aesthetic",
            ],
        }
    )

    def on_open(self, *_):
        if self.group == "occasion":
            for occasion in self.occasion:
                btn = Factory.MoodOccasionButton(
                    text=occasion,
                    group=self.group,
                )
                btn.bind(active=self.on_occasion_active)
                self.ids.stack.add_widget(btn)
        else:
            for mood in self.mood:
                self.ids.stack.add_widget(
                    CustomLabel(
                        text=mood, bold=True, font_size="28sp", adaptive_height=True
                    )
                )
                for m in self.mood[mood]:
                    btn = Factory.MoodOccasionButton(
                        text=m,
                        group=self.group,
                    )
                    btn.bind(active=self.on_mood_active)
                    self.ids.stack.add_widget(btn)

    def on_occasion_active(self, instance, value):
        if value:
            self.screen.ids.occasion_text_input.text = instance.text
            self.dismiss()

    def on_mood_active(self, instance, value):
        if value:
            self.screen.ids.mood_text_input.text = instance.text
            self.dismiss()
