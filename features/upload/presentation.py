__all__ = ("UploadScreen",)

import secrets
import time
from os.path import join, dirname, basename, exists
from pathlib import Path, PurePath

from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.utils import platform

from components.behaviors import AdaptiveBehavior
from components.sheet import BaseSheet
from features.basescreen import BaseScreen
from libs.tools import compress_image, create_scaled_bitmap
from plyer import camera
from sjfirebase.tools.mixin import StorageMixin, UserMixin

Builder.load_file(join(dirname(__file__), basename(__file__).split(".")[0] + ".kv"))


class UploadScreen(BaseScreen, StorageMixin, UserMixin):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.storage_path = None
        self.to_be_deleted = []
        self.upload_tasks = []

    def on_enter(self, *args):
        data = self.get_screen_data()
        self.ids.title.folder = data.folder
        self.storage_path = PurePath(f"users/{self.get_uid()}/{data.folder}")

    def pop_create_selection_sheet(self):
        sheet = UploadSelectionSheet(screen=self)
        sheet.open()

    def upload_images(self):
        if not self.ids.grid.children:
            return
        self.ids.upload_btn.disabled = True
        from kvdroid.jclass.java import File
        from kvdroid.jclass.android import Uri

        for widget, path in zip(self.ids.grid.children, self.to_be_deleted):
            widget.status = "uploading"
            file = Uri().fromFile(File(f"{path}"))
            task = self.put_file(f"{self.storage_path}/{path.name}", file)
            self.add_progress_listener(
                task,
                self.progress_update,
            )
            self.upload_tasks.append(task)

    @mainthread
    def progress_update(self, snapshot):
        if self.ids.progress_bar.value == len(self.ids.grid.children):
            return
        progress = snapshot.getBytesTransferred() / snapshot.getTotalByteCount()
        self.ids.progress_bar.value += progress
        if self.ids.progress_bar.value == len(self.ids.grid.children):
            self.ids.upload_btn.disabled = False
            self.toast(":) Images uploaded successfully")
            for widget in self.ids.grid.children:
                widget.status = "uploaded"
            self.manager.go_back()

    def cancel_upload(self):
        for widget, task in zip(self.ids.grid.children, self.upload_tasks):
            task.cancel()
            widget.status = "cancelled"
        self.upload_tasks = []
        self.ids.upload_btn.disabled = False
        self.ids.progress_bar.value = 0

    def remove_image(self, widget):
        self.ids.grid.remove_widget(widget)
        path = Path(widget.source)
        path.unlink()
        self.to_be_deleted.remove(path)

    def on_leave(self, *args):
        for path in self.to_be_deleted:
            path.unlink()
        self.to_be_deleted.clear()
        self.ids.grid.clear_widgets()
        self.ids.progress_bar.value = 0


class UploadSelectionSheet(BaseSheet, AdaptiveBehavior):
    def get_filename(self):
        from kvdroid import activity

        cache_path = activity.getExternalCacheDir().getAbsolutePath()
        t = time.gmtime()
        timestamp = time.strftime("%b-%d-%Y_%H:%M:%S", t)
        return join(cache_path, f"aurafit-{secrets.token_urlsafe(4)}-{timestamp}.png")

    def open_photo_picker(self):
        if platform == "android":
            from androidstorage4kivy.chooser import Chooser

            Chooser(self.process_selected_image).choose_content(
                "image/*", multiple=True
            )

    def take_photo(self):
        if platform == "android":
            image_path = self.get_filename()
            self.screen.to_be_deleted.append(Path(image_path))
            camera.take_picture(filename=image_path, on_complete=self.add_image)
        self.dismiss()

    def process_selected_image(self, uris):
        from kvdroid.tools.uri import resolve_uri

        for uri in uris:
            filename = resolve_uri(uri)
            self.add_image(filename)
        self.dismiss()

    def add_image(self, filename):
        if not exists(filename):
            return False
        bitmap = create_scaled_bitmap(filename, 1280)
        data = compress_image(bitmap)
        image_path = self.get_filename()
        with open(image_path, "wb") as f:
            f.write(data[0].tostring())
        self._add_image(image_path)
        self.screen.to_be_deleted.append(Path(image_path))
        return False

    @mainthread
    def _add_image(self, filename):
        image = Factory.WardrobeImage()
        image.ids.delete_btn.bind(on_release=lambda _: self.screen.remove_image(image))
        image.source = filename
        self.screen.ids.grid.add_widget(image)
