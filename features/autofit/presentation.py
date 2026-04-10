__all__ = ("AutofitScreen",)

from pathlib import Path

from kivy.lang import Builder

from components.sheet.sheet import MoodOccasionSelectionSheet
from features.basescreen import BaseScreen, ScreenData

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class AutofitScreen(BaseScreen):
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
