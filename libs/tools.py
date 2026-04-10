import secrets
import time
from os.path import basename
from pathlib import Path

from jnius import autoclass, cast, JavaException

from android.activity import bind as activity_bind  # noqa
from android.runnable import run_on_ui_thread  # noqa
from kvdroid import activity
from kvdroid.jclass.android import WindowManagerLayoutParams, BitmapFactory
from libs.jinterface.location import FusedLocationCallback


def distance_between_locations(point_1, point_2, unit="km"):
    Location = autoclass("android.location.Location")
    location_1 = Location("location1")
    location_1.setLatitude(point_1[0])
    location_1.setLongitude(point_1[1])

    location_2 = Location("location2")
    location_2.setLatitude(point_2[0])
    location_2.setLongitude(point_2[1])
    if unit == "km":
        return location_1.distanceTo(location_2) / 1000
    return location_1.distanceTo(location_2)


def is_jnull(obj):
    Objects = autoclass("java.util.Objects")
    return Objects.isNull(obj)


def compress_image(path_or_bitmap, quality=100, compress_format="jpeg"):
    from kvdroid.jclass.android import BitmapCompressFormat
    from kvdroid.jclass.java import ByteArrayOutputStream

    if isinstance(path_or_bitmap, str):
        bitmap = get_bitmap(path_or_bitmap)
    else:
        bitmap = path_or_bitmap
    baos = ByteArrayOutputStream(instantiate=True)
    if compress_format == "jpeg":
        bitmap.compress(BitmapCompressFormat().JPEG, quality, baos)
    else:
        bitmap.compress(BitmapCompressFormat().PNG, quality, baos)
    byte_array = baos.toByteArray()
    return byte_array, BitmapFactory().decodeByteArray(byte_array, 0, len(byte_array))


def create_scaled_bitmap(path_or_bitmap, target_size):
    from kvdroid.jclass.android import Bitmap

    if isinstance(path_or_bitmap, str):
        bitmap = get_bitmap(path_or_bitmap)
    else:
        bitmap = path_or_bitmap

    width = bitmap.getWidth()
    height = bitmap.getHeight()

    if width <= target_size >= height:
        return bitmap

    scale = target_size / (width if width > height else height)
    new_width = width * scale
    new_height = height * scale

    return Bitmap().createScaledBitmap(bitmap, new_width, new_height, True)


def get_bitmap(image_path):
    from kvdroid.jclass.android import BitmapFactory

    return BitmapFactory().decodeFile(image_path)


class _GPS_ConfigureException(Exception):
    pass


class gps:
    def __init__(self, on_location, on_enabled, on_disabled):
        self._recursive = True
        self._REQUEST_CHECK_SETTINGS = 0x2A
        self.on_enabled = on_enabled
        self.on_disabled = on_disabled
        self.fused_location = autoclass("org.kivy.location.FusedLocation")
        self._fused_location_callback = FusedLocationCallback(
            on_location, self._on_location_availability
        )
        from sjfirebase.jinterface.task import OnCompleteListener

        self._on_complete_listener = OnCompleteListener(self._check_gps)

        Priority = autoclass("com.google.android.gms.location.Priority")
        self.location_request = (
            autoclass("com.google.android.gms.location.LocationRequest$Builder")(
                Priority.PRIORITY_HIGH_ACCURACY, 5000
            )
            .setGranularity(2)
            .setMinUpdateIntervalMillis(2500)
            .setWaitForAccurateLocation(False)
            .build()
        )

        activity_bind(on_activity_result=self._on_activity_result)

    def _on_location_availability(self, available):
        if available:
            self.on_enabled()
        else:
            self.on_disabled()
        pass

    def start(self):
        self.fused_location.startLocationUpdates(
            self.location_request, self._fused_location_callback
        )

    def stop(self):
        self.fused_location.stopLocationUpdates()

    def turn_on_gps(self, recursive=True):
        self._recursive = recursive
        location_settings_request = (
            autoclass(
                "com.google.android.gms.location.LocationSettingsRequest$Builder"
            )()
            .addLocationRequest(self.location_request)
            .setAlwaysShow(True)
            .build()
        )
        (
            autoclass("com.google.android.gms.location.LocationServices")
            .getSettingsClient(activity)
            .checkLocationSettings(location_settings_request)
            .addOnCompleteListener(self._on_complete_listener)
        )

    def _on_activity_result(self, request_code, result_code, _):
        if (
            request_code == self._REQUEST_CHECK_SETTINGS
            and result_code == activity.RESULT_OK
        ):
            self.on_enabled()
        else:
            if self._recursive:
                self.turn_on_gps()
            else:
                if self.on_disabled:
                    self.on_disabled()

    def _check_gps(self, task):
        if task.isSuccessful():
            self.on_enabled()
        else:
            RAE = autoclass("com.google.android.gms.common.api.ResolvableApiException")
            if not RAE._class.isInstance(task.getException()):
                return
            try:
                resolvable = cast(
                    "com.google.android.gms.common.api.ResolvableApiException",
                    task.getException(),
                )
                resolvable.startResolutionForResult(
                    activity, self._REQUEST_CHECK_SETTINGS
                )
            except JavaException:
                pass


@run_on_ui_thread
def set_soft_input_adjust_nothing():
    window = activity.getWindow()
    window.setSoftInputMode(WindowManagerLayoutParams().SOFT_INPUT_ADJUST_NOTHING)


def get_filename(filename=None):
    from kvdroid import activity

    cache_path = activity.getExternalCacheDir().getAbsolutePath()
    if not filename:
        t = time.gmtime()
        timestamp = time.strftime("%b-%d-%Y_%H:%M:%S", t)
        return Path(cache_path, f"aurafit-{secrets.token_urlsafe(4)}-{timestamp}.png")
    return Path(cache_path, basename(filename))
