__all__ = ("OutfitsScreen",)

from os.path import join, dirname, basename

from jnius import autoclass
from kivy.lang import Builder

from features.basescreen import BaseScreen
from sjfirebase.tools.mixin import FirestoreMixin, UserMixin

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class OutfitsScreen(BaseScreen, FirestoreMixin, UserMixin):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.ids.rv.effect_y.bind(overscroll=self.on_overscroll)
        self.get_outfits()

    def on_overscroll(self, _, value):
        if value > 0:
            self.get_outfits()

    def get_outfits(self):
        if self.ids.spinner.active:
            return
        self.ids.spinner.active = True
        Direction = autoclass("com.google.firebase.firestore.Query$Direction")
        self.get_pagination_of_documents(
            collection_path=f"users/{self.get_uid()}/outfit",
            limit=30,
            listener=self.update_rv,
            order_by=("created_at", Direction.DESCENDING),
        )

    def update_rv(self, success, data):
        self.ids.spinner.active = False
        if success:
            for d in data:
                self.ids.rv.data.append(
                    {
                        "loading_image": d["placeholder_image"],
                        "source": d["thumbnail"],
                        "on_release": lambda x=d: self.manager.switch_screen(
                            "view screen", screen_data=x
                        ),
                    }
                )
