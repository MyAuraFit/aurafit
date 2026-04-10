from os import remove

import android
import android.activity
from jnius import autoclass, cast

from plyer.facades import Camera
from plyer.platforms.android import activity

Intent = autoclass("android.content.Intent")
MediaStore = autoclass("android.provider.MediaStore")
FileProvider = autoclass("androidx.core.content.FileProvider")
File = autoclass("java.io.File")


class AndroidCamera(Camera):

    def _take_picture(self, on_complete, filename=None):
        assert on_complete is not None
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self._on_activity_result)
        android.activity.bind(on_activity_result=self._on_activity_result)
        intent = Intent(MediaStore.ACTION_IMAGE_CAPTURE)
        file_path = File(filename)
        uri = FileProvider.getUriForFile(
            activity, f"{activity.getPackageName()}.fileprovider", file_path
        )
        parcelable = cast("android.os.Parcelable", uri)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)
        intent.addFlags(
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        )
        activity.startActivityForResult(intent, 0x123)

    def _take_video(self, on_complete, filename=None):
        assert on_complete is not None
        self.on_complete = on_complete
        self.filename = filename
        android.activity.unbind(on_activity_result=self._on_activity_result)
        android.activity.bind(on_activity_result=self._on_activity_result)
        intent = Intent(MediaStore.ACTION_VIDEO_CAPTURE)
        uri = FileProvider.getUriForFile(
            activity, f"{activity.getPackageName()}.provider", File(filename)
        )
        parcelable = cast("android.os.Parcelable", uri)
        intent.putExtra(MediaStore.EXTRA_OUTPUT, parcelable)

        # 0 = low quality, suitable for MMS messages,
        # 1 = high quality
        intent.putExtra(MediaStore.EXTRA_VIDEO_QUALITY, 1)
        intent.addFlags(
            Intent.FLAG_GRANT_READ_URI_PERMISSION
            | Intent.FLAG_GRANT_WRITE_URI_PERMISSION
        )
        activity.startActivityForResult(intent, 0x123)

    def _on_activity_result(self, requestCode, resultCode, intent):
        if requestCode != 0x123:
            return
        android.activity.unbind(on_activity_result=self._on_activity_result)
        if self.on_complete(self.filename):
            self._remove(self.filename)

    def _remove(self, fn):
        try:
            remove(fn)
        except OSError:
            pass


def instance():
    return AndroidCamera()
