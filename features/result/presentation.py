__all__ = ("ResultScreen",)

import shutil
import time
from os import mkdir
from os.path import join, exists
from pathlib import Path

from kivy.animation import Animation
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.lang import Builder

from features.basescreen import BaseScreen
from libs.throttle import CallLimiter
from sjfirebase.tools.mixin import FunctionMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class ResultScreen(BaseScreen, FunctionMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.image_paths = []
        self.cancel = False

    def on_pre_enter(self, *args):
        shimmer_box = Factory.ShimmerWidget()
        self.add_widget(shimmer_box)
        self.update_outfit_label_progress(shimmer_box)
        self.generate_outfit()

    @CallLimiter(max_calls=4)
    def generate_outfit(self):
        outfit_data = self.get_screen_data()
        self.get_https_callable_call(
            "generate_image",
            data=outfit_data,
            timeout=600,
            listener=self.on_outfit_generated,
            enforce_app_check=False,
        )

    @mainthread
    def update_outfit_label_progress(self, shimmer_box):
        lbl = shimmer_box.ids.lbl
        messages = [
            "Creating the outfit...",
            "Almost there...",
            "Adding the final touches...",
        ]
        index = 0
        lbl.text = messages[index]

        anim = Animation(shimmer_x=lbl.width * 1.2, duration=5, step=1 / 20)

        def change_text(_, widget):
            if not shimmer_box.parent:
                return
            nonlocal index, anim
            print("still running")
            index = (index + 1) % len(messages)
            widget.text = messages[index]
            lbl.shimmer_x = -lbl.width
            anim = Animation(shimmer_x=lbl.width * 1.2, duration=5, step=1 / 30)
            anim.bind(on_complete=change_text)
            anim.start(lbl)

        anim.bind(on_complete=change_text)
        anim.start(lbl)

    @mainthread
    def on_outfit_generated(self, success, data):
        if self.cancel:
            self.cancel = False
            if self.manager.current == self.name:
                self.generate_outfit()
            return
        if not success:
            print(data)
            self.generate_outfit.decrement()
            self.generate_outfit()
            return
        if self.generate_outfit.calls_made() > 4:
            return
        self.ids[f"style_{self.generate_outfit.calls_made()}"].loading_image = data[
            "thumbnail"
        ]
        self.ids[f"style_{self.generate_outfit.calls_made()}"].source = data["image"]
        if self.generate_outfit.calls_made() == 1:
            self.ids.image.loading_image = data["thumbnail"]
            self.ids.image.source = data["image"]

            if hasattr(self.children[0], "is_removable"):
                self.remove_widget(self.children[0])
        if self.generate_outfit.calls_made() == 4:
            self.generate_outfit.reset()
            return
        self.generate_outfit()

    def save_outfit(self, texture):
        from kvdroid import activity

        t = time.gmtime()
        timestamp = time.strftime("%b-%d-%Y_%H:%M:%S", t)
        cache_dir = join(activity.getCacheDir().getAbsolutePath(), "texture-cache")
        if not exists(cache_dir):
            mkdir(cache_dir)
        image_path = join(cache_dir, f"my-aurafit-{timestamp}.png")
        self.image_paths.append(image_path)
        texture.save(image_path, flipped=False)

    def download_images(self):
        from androidstorage4kivy.sharedstorage import SharedStorage

        to_be_deleted = []
        ss = SharedStorage()
        for image_path in self.image_paths:
            ss.copy_to_shared(image_path)
        self.toast("Images downloaded")

    def share_images(self):
        from androidstorage4kivy.sharesheet import ShareSheet
        from kvdroid import activity
        from kvdroid.jclass.java import File
        from kvdroid.jclass.androidx import FileProvider

        ShareSheet().share_file_list(
            [
                FileProvider().getUriForFile(
                    activity,
                    f"{activity.getPackageName()}.fileprovider",
                    File(image_file),
                )
                for image_file in self.image_paths
            ]
        )
        print("Sharing")

    def on_leave(self, *args):
        for i in range(1, 5):
            self.ids[f"style_{i}"].source = ""
            self.ids[f"style_{i}"].loading_image = ""
        self.ids.image.loading_image = ""
        self.ids.image.source = ""
        if self.in_progress:
            self.cancel = True
            print("Cancelling")
        self.generate_outfit.reset()
        self.cleanup()

    @staticmethod
    def cleanup():
        from kvdroid import activity

        cache_dir = join(activity.getCacheDir().getAbsolutePath(), "texture-cache")
        if exists(cache_dir):
            shutil.rmtree(cache_dir)

    @property
    def in_progress(self):
        if self.generate_outfit.in_progress():
            return True
        elif self.generate_outfit.calls_made() == 4 and self.ids.style_4.source == "":
            return True
        else:
            return False
