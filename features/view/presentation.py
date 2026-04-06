__all__ = ("ViewScreen",)

import shutil
import time
from os import mkdir
from os.path import join, dirname, basename, exists

from kivy.lang import Builder
from kivy.utils import platform

from features.basescreen import BaseScreen

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class ViewScreen(BaseScreen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.image_path = None

    def on_pre_enter(self, *args):
        self.app.theme_cls.theme_style = "Dark"
        self.ids.btn_box.disabled = True
        self.ids.spinner.active = True
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            change_statusbar_color(
                [0, 0, 0, 0],
                "white",
            )
            navbar_color(
                [0, 0, 0, 0],
                "white",
            )
        data = self.get_screen_data()
        self.ids.image.loading_image = data.placeholder_image
        self.ids.image.source = data.image_url
        if self.ids.image.is_loaded:
            self.save_outfit(self.ids.image.texture)

    def on_leave(self, *args):
        self.app.theme_cls.theme_style = "Light"
        if platform == "android":
            from kvdroid.tools import change_statusbar_color, navbar_color

            change_statusbar_color(
                [0, 0, 0, 0],
                "black",
            )
            navbar_color(
                [0, 0, 0, 0],
                "black",
            )
        self.ids.image.loading_image = ""
        self.ids.image.source = ""
        self.ids.spinner.active = False
        self.cleanup()

    @staticmethod
    def cleanup():
        from kvdroid import activity

        cache_dir = join(activity.getCacheDir().getAbsolutePath(), "texture-cache")
        if exists(cache_dir):
            shutil.rmtree(cache_dir)

    def save_outfit(self, texture):
        from kvdroid import activity

        t = time.gmtime()
        timestamp = time.strftime("%b-%d-%Y_%H:%M:%S", t)
        cache_dir = join(activity.getCacheDir().getAbsolutePath(), "texture-cache")
        if not exists(cache_dir):
            mkdir(cache_dir)
        self.image_path = join(cache_dir, f"my-aurafit-{timestamp}.png")
        texture.save(self.image_path, flipped=False)
        self.ids.btn_box.disabled = False
        self.ids.spinner.active = False

    def download_image(self):
        from androidstorage4kivy.sharedstorage import SharedStorage

        ss = SharedStorage()
        if self.image_path:
            ss.copy_to_shared(self.image_path)
        self.toast("Images downloaded")

    def share_image(self):
        from kvdroid import activity
        from androidstorage4kivy.sharesheet import ShareSheet
        from kvdroid.jclass.java import File
        from kvdroid.jclass.androidx import FileProvider

        uri = FileProvider().getUriForFile(
            activity, f"{activity.getPackageName()}.fileprovider", File(self.image_path)
        )

        ShareSheet().share_file(uri)
        print("Sharing")
