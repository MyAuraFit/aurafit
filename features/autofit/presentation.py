__all__ = ("AutofitScreen",)

from os.path import join, dirname, basename

from kivy.lang import Builder

from features.basescreen import BaseScreen, ScreenData

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class AutofitScreen(BaseScreen):
    def generate_my_aurafit(self):
        screen_data = ScreenData()
        screen_data.setdefault("type", "autofit")
        screen_data.setdefault("prompt", self.ids.text_input.text)
        self.manager.switch_screen("result screen", screen_data=screen_data)
        self.ids.text_input.text = ""
