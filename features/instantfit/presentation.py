__all__ = ("InstantfitScreen",)

import time
from os.path import join, basename, exists
from pathlib import Path

from jnius import cast
from kivy.clock import mainthread
from kivy.lang import Builder
from kivy.properties import OptionProperty
from kivy.utils import platform

from components.sheet.sheet import MoodOccasionSelectionSheet
from features.basescreen import BaseScreen, ScreenData
from libs.tools import create_scaled_bitmap, compress_image, get_filename
from plyer import camera
from sjfirebase.tools.mixin import StorageMixin, FirestoreMixin, UserMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class InstantfitScreen(BaseScreen, StorageMixin, FirestoreMixin, UserMixin):
    image_type = OptionProperty("none", options=["none", "cloth", "selfie"])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.to_be_deleted = []

    def open_photo_picker(self, image_type):
        self.image_type = image_type
        if platform == "android":
            from androidstorage4kivy.chooser import Chooser

            Chooser(self.process_selected_image).choose_content("image/*")

    def take_picture(self, image_type):
        self.image_type = image_type
        if platform == "android":
            from kvdroid import activity

            cache_path = activity.getExternalCacheDir().getAbsolutePath()
            t = time.gmtime()
            timestamp = time.strftime("%b-%d-%Y_%H:%M:%S", t)
            image_path = join(cache_path, f"img_{timestamp}.png")
            self.to_be_deleted.append(image_path)
            camera.take_picture(filename=image_path, on_complete=self.add_image)

    def process_selected_image(self, uris):
        from kvdroid.tools.uri import resolve_uri

        for uri in uris:
            filename = resolve_uri(uri)
            self.add_image(filename)

    def add_image(self, filename):
        if not exists(filename):
            return False
        bitmap = create_scaled_bitmap(filename, 1280)
        data = compress_image(bitmap)
        image_path = get_filename(filename)
        with open(image_path, "wb") as f:
            f.write(data[0].tostring())
        self._add_image(image_path)
        self.to_be_deleted.append(image_path)
        return False

    @mainthread
    def _add_image(self, filename):
        if self.image_type == "selfie":
            self.ids.selfie_cover_image.source = filename
        else:
            self.ids.cloth_cover_image.source = filename

    def generate_my_aurafit(self):
        self.ids.content.disabled = True
        self.ids.btn.disabled = True
        self.upload_images(
            self.ids.cloth_cover_image.source, self.ids.selfie_cover_image.source
        )

    def upload_images(self, cloth_image_filename, selfie_image_filename):
        from kvdroid.jclass.java import File
        from kvdroid.jclass.android import Uri

        cloth_file = Uri().fromFile(File(cloth_image_filename))
        selfie_file = Uri().fromFile(File(selfie_image_filename))

        cloth_cloud_storage_path = (
            f"users/{self.get_uid()}/clothes/{basename(cloth_image_filename)}"
        )
        selfie_cloud_storage_path = (
            f"users/{self.get_uid()}/selfies/{basename(selfie_image_filename)}"
        )

        upload_gs_count = 0

        result_screen_data = ScreenData()
        result_screen_data.setdefault("type", "instantfit")
        result_screen_data.setdefault("mood", self.ids.mood_text_input.text)
        result_screen_data.setdefault("occasion", self.ids.occasion_text_input.text)
        result_screen_data.setdefault("time_of_day", self.ids.time_sv_box.text)

        cloth_gs_data = {}
        selfie_gs_data = {}

        def get_gs_url(task):
            nonlocal upload_gs_count
            if not task.isSuccessful():
                self.get_gemini_error(None)
                print(
                    f"Failed to upload image to Google Storage: {task.getErrorMessage()}"
                )
                return
            mimetype = task.getResult().getMetadata().getContentType()
            bucket = task.getResult().getMetadata().getBucket()
            path = task.getResult().getMetadata().getPath()
            if "cloth" in path:
                cloth_gs_data["gs_url"] = f"gs://{bucket}/{path}"
                cloth_gs_data["mimetype"] = mimetype
                result_screen_data.setdefault("cloth", cloth_gs_data)
            else:
                selfie_gs_data["gs_url"] = f"gs://{bucket}/{path}"
                selfie_gs_data["mimetype"] = mimetype
                result_screen_data.setdefault("selfie", selfie_gs_data)
            upload_gs_count += 1
            if upload_gs_count == 2:
                self.manager.switch_screen(
                    "result screen", screen_data=result_screen_data
                )

        cloth_upload_task = self.put_file(
            cloth_cloud_storage_path, cloth_file, get_gs_url
        )

        selfie_upload_task = self.put_file(
            selfie_cloud_storage_path, selfie_file, get_gs_url
        )

        self.add_progress_listener(
            cloth_upload_task,
            lambda snapshot: self.progress_update(
                snapshot,
                cast(
                    "com.google.firebase.storage.UploadTask$TaskSnapshot",
                    selfie_upload_task.getSnapshot(),
                ),
            ),
        )

        self.add_progress_listener(
            selfie_upload_task,
            lambda snapshot: self.progress_update(
                snapshot,
                cast(
                    "com.google.firebase.storage.UploadTask$TaskSnapshot",
                    cloth_upload_task.getSnapshot(),
                ),
            ),
        )

    @mainthread
    def progress_update(self, snapshot1, snapshot2):
        total_bytes_transferred = (
            snapshot1.getBytesTransferred() + snapshot2.getBytesTransferred()
        )
        total_bytes_count = (
            snapshot1.getTotalByteCount() + snapshot2.getTotalByteCount()
        )
        if total_bytes_count > 0:
            progress = (100 * total_bytes_transferred) / total_bytes_count
            self.ids.btn.text = f"Uploading {progress:.1f}%"

    def cleanup(self):
        self.ids.content.disabled = False
        self.ids.btn.disabled = False
        self.ids.btn.text = "Generate My Aurafit"
        self.ids.selfie_cover_image.source = ""
        self.ids.cloth_cover_image.source = ""
        for file in self.to_be_deleted:
            file.unlink()
        self.to_be_deleted.clear()

    def on_leave(self, *args):
        self.cleanup()

    def pop_mood_occasion_selection_sheet(self, group, title):
        sheet = MoodOccasionSelectionSheet(screen=self, group=group, title=title)
        sheet.open()
