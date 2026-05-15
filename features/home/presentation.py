__all__ = ("HomeScreen",)

from pathlib import Path

from kivy.lang import Builder

from components.behaviors import AdaptiveBehavior
from components.sheet import BaseSheet
from features.basescreen import BaseScreen
from libs.review import check_for_review
from sjfirebase.tools.mixin import UserMixin, FirestoreMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class HomeScreen(BaseScreen, UserMixin, FirestoreMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        check_for_review()
        self.add_document_snapshot_listener(
            f"users/{self.get_uid()}",
            lambda data, _: setattr(self.app, "coins", data["coins"]),
        )

    def pop_create_selection_sheet(self):
        sheet = CreateSelectionSheet(screen=self)
        sheet.open()


class CreateSelectionSheet(BaseSheet, AdaptiveBehavior):
    def go_to_autofit(self):
        self.dismiss()
        self.screen.manager.current = "autofit screen"

    def go_to_instantfit(self):
        self.dismiss()
        self.screen.manager.current = "instantfit screen"
