__all__ = ("HomeScreen",)

from os.path import join, dirname, basename
from kivy.lang import Builder

from components.behaviors import AdaptiveBehavior
from components.sheet import BaseSheet
from features.basescreen import BaseScreen

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class HomeScreen(BaseScreen):
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