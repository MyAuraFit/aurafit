from kivy import platform
from kivy.app import App
from kivy.clock import mainthread
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

from components.bar import win_md_bnb
from components.behaviors import AdaptiveBehavior
from components.button import IconButton
from components.factory_register import register_factory
from components.progressindicator import CircularProgressIndicator
from components.sheet import BaseSheet
from features.screenmanager import AppScreenManager
from sjfirebase.tools.mixin import UserMixin

# from libs.ads import Ads
# from libs.appcheck import initialize_appcheck
# from libs.appupdate import AppUpdate
# from libs.billing import Billing
# from sjfirebase.jclass.firebaseremoteconfig import FirebaseRemoteConfig
# from sjfirebase.jclass.firebaseremoteconfigsettings import FirebaseRemoteConfigSettings
# from sjfirebase.tools.mixin import UserMixin
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
    is_offline = BooleanProperty(True)
    is_billing_ready = BooleanProperty(False)
    is_premium = BooleanProperty(False)
    premium_product_id = StringProperty()
    __billing_ready_listeners = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._listener = None
        self._ad_load_listener = None
        self.sm = None
        if platform == "android":
            set_on_apply_window_insets_listener(self.on_apply_window_insets)
            request_apply_insets()
        # initialize_appcheck()
        # Ads.initialize(self)
        # Billing.initialize(self)
        # remote_config: FirebaseRemoteConfig = FirebaseRemoteConfig.getInstance()
        # config_settings = (
        #     FirebaseRemoteConfigSettings.Builder()
        #     .setMinimumFetchIntervalInSeconds(3600)
        #     .build()
        # )
        # remote_config.setConfigSettingsAsync(config_settings)
        # remote_config.setDefaultsAsync(get_resource("xml").remote_config_defaults)
        # remote_config.fetchAndActivate()
        self.theme_cls = ThemeManager()
        # self.theme_cls.theme_style = "Dark"
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
                bg_color=lambda _, value: (
                    change_statusbar_color(
                        [0, 0, 0, 0],
                        "black" if self.theme_cls.theme_style == "Light" else "white",
                    ),
                    navbar_color(
                        [0, 0, 0, 0],
                        "black" if self.theme_cls.theme_style == "Light" else "white",
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
        if self.sm.current not in ["splash screen", "result screen"]:
            self.root.padding = [0, self.statusbar_height, 0, self.navbar_height]

    def build(self):
        self.icon_button = IconButton(
            icon="home",
            bg_color=self.theme_cls.primary_color,
            y="100dp",
            shadow_color=self.theme_cls.shadow_color,
            x=Window.width - dp(45) - dp(20),
            spread_radius=[dp(-2), dp(-2)],
            on_release=lambda _: setattr(self.sm, "current", "home screen"),
        )
        self.icon_button.color = self.theme_cls.text_color_dark
        self.icon_button.size = ["45dp", "45dp"]
        self.icon_button.radius = "16dp"

        self.sm = AppScreenManager(
            transition=FadeTransition(
                clearcolor=(
                    [0, 0, 0, 0]
                    if self.theme_cls.theme_style == "Dark"
                    else [1, 1, 1, 0]
                ),
                duration=0.2,
            )
        )
        self.sm.bind(current=self.push_pop_win_md_bnb)
        box = BoxLayout()
        box.add_widget(self.sm)
        if platform == "android":
            self.sm.bind(
                current=lambda _, name: (
                    setattr(
                        box,
                        "padding",
                        [0, self.statusbar_height, 0, self.navbar_height],
                    )
                    if name not in ["splash screen", "result screen"]
                    else setattr(box, "padding", [0] * 4)
                )
            )
            if user := UserMixin().get_current_user():
                user.reload()
                self.sm.current = "home screen"
                return box
        self.sm.current = "login screen"
        return box

    def register_billing_ready_listener(self, listener):
        self.__billing_ready_listeners.append(listener)

    def unregister_billing_ready_listener(self, listener):
        self.__billing_ready_listeners.remove(listener)

    def on_is_billing_ready(self, *_):
        if self.is_premium:
            self.__billing_ready_listeners.clear()
            return
        for instance in self.__billing_ready_listeners:
            instance.dispatch("on_billing_ready")

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
        # if platform == "android":
        #     from sjfirebase.tools.mixin import DatabaseMixin
        #     self.__database = DatabaseMixin()
        #     self.__database.add_value_event_listener(
        #         ".info/connected",
        #         on_data_changed=self.check_firebase_disconnected,
        #     )

    def on_resume(self):
        if platform == "android":
            set_soft_input_adjust_nothing()
            Window.update_viewport()
            # AppUpdate.continue_update()

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

    @mainthread
    def check_firebase_disconnected(self, connected):
        if not connected and not self.is_offline:

            class DisconnectSheet(BaseSheet, AdaptiveBehavior):
                app_sheet = None

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

            sheet = DisconnectSheet()
            sheet.open()
            self.is_offline = True
        else:
            for child in Window.children:
                if hasattr(child, "app_sheet"):
                    child.dismiss()
            self.is_offline = False


if __name__ == "__main__":
    MyAuraFitApp().run()
