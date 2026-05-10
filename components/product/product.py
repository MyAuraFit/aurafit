__all__ = ("ProductWidget",)

from pathlib import Path

from kivy.lang import Builder
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.behaviors import ToggleButtonBehavior

from components.layout import CustomBoxLayout

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class ProductWidget(ToggleButtonBehavior, CustomBoxLayout):
    currency = StringProperty()
    amount = NumericProperty()
    product_id = StringProperty()
    base_plan_id = StringProperty()
    period = StringProperty()
    title = StringProperty()
    name = StringProperty()
    slash = StringProperty("/")

    __events__ = ("on_product_selected",)

    def on_product_selected(self):
        pass

    def on_active(self, instance, value):
        if value:
            self.dispatch("on_product_selected")
