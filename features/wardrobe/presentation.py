__all__ = ("WardrobeScreen",)

from os.path import join, dirname, basename

from jnius import autoclass
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.dropdown import DropDown

from components.button import CustomButton
from components.divider import Divider
from features.basescreen import BaseScreen
from sjfirebase.tools.mixin import FirestoreMixin, UserMixin

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class WardrobeScreen(BaseScreen, FirestoreMixin, UserMixin):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.ids.rv.effect_y.bind(overscroll=self.on_overscroll)
        self.get_clothes()

    def on_overscroll(self, _, value):
        if value > 0:
            self.get_clothes()

    def get_clothes(self):
        if self.ids.spinner.active:
            return
        self.ids.spinner.active = True
        Direction = autoclass("com.google.firebase.firestore.Query$Direction")
        self.get_pagination_of_documents(
            collection_path=f"users/{self.get_uid()}/clothes",
            limit=30,
            listener=self.update_rv,
            order_by=("created_at", Direction.DESCENDING),
        )

    def update_rv(self, success, data):
        self.ids.spinner.active = False
        if success:
            for d in data:
                if not (d.get("placeholder_image") and d.get("thumbnail_url")):
                    continue
                self.ids.rv.data.append(
                    {
                        "loading_image": d["placeholder_image"],
                        "source": d["thumbnail_url"],
                        "on_release": lambda x=d: self.manager.switch_screen(
                            "view screen", screen_data=x
                        ),
                    }
                )

    def show_dropdown(self, widget):
        dd = DropDown(auto_width=False, width=self.width / 1.8)
        dd.container.padding = ["10dp", "5dp"]
        dd.bind(
            on_select=lambda _, x: self.manager.switch_screen(
                "upload screen", screen_data={"folder": x}
            )
        )

        def force_set_item_bound_property(text, radius, folder):
            item = CustomButton(
                text=text,
                size_hint_y=None,
                height="45dp",
                italic=True,
                bold=True,
                spread_radius=[dp(-3), dp(-3)],
                shadow_color=self.app.theme_cls.shadow_color,
                radius=radius,
                on_release=lambda btn: dd.select(folder),
            )
            item.color = self.app.theme_cls.primary_color
            item.bg_color = self.app.theme_cls.bg_color
            return item

        dd.add_widget(
            force_set_item_bound_property(
                "Upload selfie", ["16dp", "16dp", 0, 0], "selfies"
            )
        )
        dd.add_widget(Divider(color=self.app.theme_cls.text_color))
        dd.add_widget(
            force_set_item_bound_property(
                "Upload clothes", [0, 0, "16dp", "16dp"], "clothes"
            )
        )
        dd.open(widget)
