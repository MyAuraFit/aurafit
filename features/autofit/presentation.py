__all__ = ("AutofitScreen",)

from pathlib import Path

from kivy.clock import mainthread
from kivy.lang import Builder

from components.sheet import MoodOccasionSelectionSheet
from features.basescreen import BaseScreen, ScreenData
from sjfirebase.tools.mixin import FirestoreMixin, UserMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class AutofitScreen(BaseScreen, FirestoreMixin, UserMixin):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.at_least_one_active_sheet = False

    def on_enter(self):
        self.get_pagination_of_documents(
            f"users/{self.get_uid()}/selfies",
            limit=1,
            listener=lambda *args: self.pop_warning_sheet(*args, folder="selfies"),
        )
        self.get_pagination_of_documents(
            f"users/{self.get_uid()}/clothes",
            limit=1,
            listener=lambda *args: self.pop_warning_sheet(*args, folder="clothes"),
        )

    def generate_my_aurafit(self):
        screen_data = ScreenData()
        screen_data.setdefault("type", "autofit")
        screen_data.setdefault("mood", self.ids.mood_text_input.text)
        screen_data.setdefault("occasion", self.ids.occasion_text_input.text)
        screen_data.setdefault("time_of_day", self.ids.time_sv_box.text)
        self.manager.switch_screen("result screen", screen_data=screen_data)

    def pop_mood_occasion_selection_sheet(self, group, title):
        sheet = MoodOccasionSelectionSheet(screen=self, group=group, title=title)
        sheet.open()

    @mainthread
    def pop_warning_sheet(self, success, data, folder):
        if self.at_least_one_active_sheet:
            return
        if not success:
            return
        if success and data:
            return
        sheet = self.app.pop_disconnect_sheet(
            text=f"Seems like you haven't uploaded any {folder} yet. "
            "You can do so by uploading them in the [b][u][ref=wardrobe]wardrobe section[/ref][u][/b].",
            icon="alert",
            timeout=20,
            on_ref_press=lambda: {
                self.manager.switch_screen("wardrobe screen"),
                sheet.dismiss(),
            },
            on_dismiss=lambda: setattr(self, "at_least_one_active_sheet", False),
        )
        self.at_least_one_active_sheet = True
