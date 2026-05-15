__all__ = ("WardrobeScreen",)

from pathlib import Path

from jnius import autoclass
from kivy.clock import mainthread, Clock
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.dropdown import DropDown

from components.button import CustomButton
from components.divider import Divider
from features.basescreen import BaseScreen
from sjfirebase.tools.mixin import FirestoreMixin, UserMixin, StorageMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class WardrobeScreen(BaseScreen, FirestoreMixin, UserMixin, StorageMixin):

    def __init__(self, **kw):
        super().__init__(**kw)
        self.ids.clothes_rv.effect_y.bind(
            overscroll=lambda *args: self.on_overscroll(
                *args, item_collection="clothes", rv_id="clothes_rv"
            )
        )
        self.ids.selfies_rv.effect_y.bind(
            overscroll=lambda *args: self.on_overscroll(
                *args, item_collection="selfies", rv_id="selfies_rv"
            )
        )
        self.get_wardrobe_items(item_collection="clothes", rv_id="clothes_rv")

    def on_overscroll(self, _, value, item_collection, rv_id):
        if value > 0:
            self.get_wardrobe_items(item_collection=item_collection, rv_id=rv_id)

    def get_wardrobe_items(self, item_collection, rv_id):
        if self.ids.spinner.active:
            return
        self.ids.spinner.active = True
        self.ids.spinner.opacity = 1
        Direction = autoclass("com.google.firebase.firestore.Query$Direction")
        self.get_pagination_of_documents(
            collection_path=f"users/{self.get_uid()}/{item_collection}",
            limit=30,
            listener=lambda *args: self.update_rv(
                *args, item_collection=item_collection, rv_id=rv_id
            ),
            order_by=("created_at", Direction.DESCENDING),
        )

    @mainthread
    def update_rv(self, success, data, item_collection, rv_id):
        self.ids.spinner.active = False
        self.ids.spinner.opacity = 0
        if success:
            for d in data:
                if not (d.get("placeholder_image") and d.get("thumbnail_url")):
                    continue

                self.ids[rv_id].data.append(
                    self.extract_data(rv_id, d, item_collection)
                )

    def extract_data(self, rv_id, d, item_collection):
        item = {
            "image.loading_image": d["placeholder_image"],
            "image.source": d["thumbnail_url"],
            "image_url": d["image_url"],
            "item_id": d["document_id"],
            "on_release": lambda: self.manager.switch_screen(
                "view screen", screen_data=d
            ),
            "delete_btn.on_release": lambda: self.delete_wardrobe_item(
                item, rv_id, item_collection
            ),
        }
        return item

    def delete_wardrobe_item(self, item, rv_id, item_collection):
        print(item)
        gs_image_file = item["image_url"].split("/my-aurafit.firebasestorage.app")[1]
        gs_thumbnail_file = item["image.source"].split(
            "/my-aurafit.firebasestorage.app"
        )[1]
        self.delete_file(gs_image_file)
        self.delete_file(gs_thumbnail_file)
        self.delete_document(
            f"users/{self.get_uid()}/{item_collection}/{item['item_id']}"
        )
        self.ids[rv_id].data.remove(item)
        self.ids[rv_id].data = self.ids[rv_id].data.copy()
        Clock.schedule_once(lambda _: self.ids[rv_id].refresh_from_data())

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
