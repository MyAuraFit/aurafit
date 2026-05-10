from kivy.app import App
from kivy.clock import Clock, triggered
from kivy.core.text import Label
from kivy.core.window import Window
from kivy.loader import Loader
from kivy.metrics import dp
from kivy.properties import (
    ObjectProperty,
    NumericProperty,
    StringProperty,
    BooleanProperty,
    ListProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import FadeTransition
from kivy.utils import platform

from components.bar import win_md_bnb
from components.behaviors import AdaptiveBehavior
from components.factory_register import register_factory
from components.progressindicator import CircularProgressIndicator
from components.sheet import BaseSheet
from features.screenmanager import AppScreenManager
from libs.ads import Ads
from libs.appcheck import initialize_appcheck
from libs.appupdate import AppUpdate

# from libs.billing import Billing
from sjfirebase.tools.mixin import UserMixin
from ui.theme import ThemeManager

Label.register(
    "Roboto",
    "assets/fonts/Cardo-Regular.ttf",
    "assets/fonts/Cardo-Italic.ttf",
    "assets/fonts/Cardo-Bold.ttf",
    # "assets/fonts/Cardo-BoldItalic.ttf",
)
Loader.error_image = "assets/images/transparent.png"
Loader.loading_image = "assets/images/transparent.png"
register_factory()

if platform == "android":
    from kvdroid.tools.display import (
        enable_edge_to_edge,
        set_on_apply_window_insets_listener,
        request_apply_insets,
    )
    from libs.tools import set_soft_input_adjust_nothing

    enable_edge_to_edge()


class MyAuraFitApp(App):
    theme_cls = ObjectProperty()
    dialog = ObjectProperty()
    use_kivy_settings = False
    kv_file = StringProperty("imports.kv")
    is_paused = BooleanProperty(False)
    statusbar_height = NumericProperty(0)
    navbar_height = NumericProperty(0)
    __database = None
    is_billing_ready = BooleanProperty(False)
    is_premium = BooleanProperty(False)
    premium_product_id = StringProperty()
    __billing_ready_listeners = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._listener = None
        self._dark_mode_listener = None
        self.sm = None
        if platform == "android":
            set_on_apply_window_insets_listener(self.on_apply_window_insets)
            request_apply_insets()
        initialize_appcheck()
        Ads.initialize()
        # Billing.initialize(self)
        self.theme_cls = ThemeManager()
        if platform == "android":
            from kvdroid.tools.darkmode import dark_mode
            from libs.jinterface.darkmode import DarkModeListener
            from kvdroid import activity

            self._dark_mode_listener = DarkModeListener(self.theme_cls.set_theme_style)
            activity.setDarkModeListener(self._dark_mode_listener)
            self.theme_cls.theme_style = "Dark" if dark_mode() else "Light"
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            change_statusbar_color(
                [0, 0, 0, 0],
                "black" if self.theme_cls.theme_style == "Light" else "white",
            )
            navbar_color(
                [0, 0, 0, 0],
                "black" if self.theme_cls.theme_style == "Light" else "white",
            )
            self.theme_cls.bind(
                theme_style=lambda _, value: (
                    change_statusbar_color(
                        [0, 0, 0, 0],
                        "black" if value == "Light" else "white",
                    ),
                    navbar_color(
                        [0, 0, 0, 0],
                        "black" if value == "Light" else "white",
                    ),
                )
            )

    def open_dialog(self):
        if not self.dialog:
            spinner = CircularProgressIndicator(
                line_width=dp(1.5), color=self.theme_cls.text_color_dark
            )
            self.dialog = ModalView(
                auto_dismiss=False,
                background="",
                background_color=[0] * 4,
                size_hint=(None, None),
                size=(dp(40), dp(40)),
                on_pre_open=lambda _: setattr(spinner, "active", True),
                on_dismiss=lambda _: setattr(spinner, "active", False),
            )
            self.dialog.add_widget(spinner)
        self.dialog.open()

    def dismiss_dialog(self):
        if not self.dialog:
            return
        self.dialog.dismiss()

    def on_apply_window_insets(self, insets):
        self.statusbar_height = insets.top
        self.navbar_height = insets.bottom
        if not self.root:
            return
        if self.sm.current not in ["splash screen", "subscription screen"]:
            self.root.padding = [0, self.statusbar_height, 0, self.navbar_height]

    # noinspection PyNoneFunctionAssignment
    def build(self):
        self.sm = AppScreenManager(
            transition=FadeTransition(
                clearcolor=(
                    [0, 0, 0, 0]
                    if self.theme_cls.theme_style == "Dark"
                    else [1, 1, 1, 0]
                ),
                duration=0.1,
            )
        )
        self.sm.bind(current=self.push_pop_win_md_bnb)
        box = BoxLayout()
        box.add_widget(self.sm)
        if platform == "android":
            self.sm.bind(
                current=lambda _, name: (
                    (
                        setattr(
                            box,
                            "padding",
                            [0, self.statusbar_height, 0, self.navbar_height],
                        )
                        if name not in ["splash screen", "subscription screen"]
                        else setattr(box, "padding", [0] * 4)
                    )
                )
            )
            if user := UserMixin().get_current_user():
                user.reload()
                self.sm.current = "home screen"
                return box
        self.sm.current = "splash screen"
        return box

    def on_start(self):
        win_md_bnb.create_bnb(
            tabs=[
                {
                    "icon": "wardrobe",
                    "icon_variant": "wardrobe-outline",
                    "text": "Wardrobe",
                    "name": "wardrobe screen",
                    "on_release": lambda _: setattr(
                        self.sm, "current", "wardrobe screen"
                    ),
                },
                {
                    "icon": "cards-club",
                    "icon_variant": "cards-club-outline",
                    "text": "Aurafit",
                    "name": "home screen",
                    "active": True,
                    "on_release": lambda _: setattr(self.sm, "current", "home screen"),
                },
                {
                    "icon": "tshirt-crew",
                    "icon_variant": "tshirt-crew-outline",
                    "text": "Outfits",
                    "name": "outfits screen",
                    "on_release": lambda _: setattr(
                        self.sm, "current", "outfits screen"
                    ),
                },
            ],
            use_text=True,
            shadow_color=self.theme_cls.shadow_color,
        )
        self.push_pop_win_md_bnb()
        self.dispatch("on_resume")

    def on_resume(self):
        if platform == "android":
            from kvdroid import activity

            set_soft_input_adjust_nothing()
            Window.update_viewport()
            Clock.schedule_once(lambda _: activity.setAppIsReady(True))
            AppUpdate.continue_update()

    def push_pop_win_md_bnb(self, *_):
        if not win_md_bnb.bar:
            return
        if self.sm.current in ["wardrobe screen", "home screen", "outfits screen"]:
            win_md_bnb.push()

            for child in win_md_bnb.bar.children:
                if self.sm.current == child.name and not child.active:
                    child.dispatch("on_release")
        else:
            win_md_bnb.pop()

    def pop_disconnect_sheet(
        self,
        text=None,
        icon=None,
        timeout=3,
        on_ref_press=lambda: None,
        on_dismiss=lambda: None,
    ):
        class DisconnectSheet(BaseSheet, AdaptiveBehavior):
            text = StringProperty()
            icon = StringProperty()

            __events__ = ("on_ref_press",)

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.modalview = type(
                    "DummyModalView",
                    (),
                    {
                        "open": lambda *_, **__: None,
                        "close": lambda *_, **__: None,
                        "dismiss": lambda *_, **__: None,
                    },
                )

            @triggered(timeout)
            def on_open(self, *args):
                self.dismiss()

            def on_ref_press(self):
                on_ref_press()

            def on_dismiss(self, *args):
                on_dismiss()

        sheet = DisconnectSheet(
            text=text or "You're currently offline. Check your internet data!",
            icon=icon or "wifi-off",
        )
        sheet.open()
        return sheet


if __name__ == "__main__":
    MyAuraFitApp().run()
