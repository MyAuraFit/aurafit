from android.runnable import run_on_ui_thread  # noqa
from sjappupdate.jclass import (
    AppUpdateManagerFactory,
    AppUpdateManager,
    AppUpdateInfo,
    UpdateAvailability,
    AppUpdateType,
    AppUpdateOptions,
)
from sjappupdate.jinterface import OnSuccessListener, OnCompleteListener
from sjplayservicecommon.jclass import GoogleApiAvailability, ConnectionResult

from kvdroid import activity


class AppUpdate:
    __app_update_manager: AppUpdateManager = None
    __on_success_listener = None
    __on_complete_listener = None

    @classmethod
    def _initialize(cls, callback):
        cls.__app_update_manager = AppUpdateManagerFactory.create(activity)
        app_update_info_task = cls.__app_update_manager.getAppUpdateInfo()
        cls.__on_success_listener = OnSuccessListener(callback)
        app_update_info_task.addOnSuccessListener(cls.__on_success_listener)

    @classmethod
    @run_on_ui_thread
    def check_for_update(cls):
        google_api_availability: GoogleApiAvailability = (
            GoogleApiAvailability.getInstance()
        )
        result = google_api_availability.isGooglePlayServicesAvailable(activity)
        print(result)
        if result == ConnectionResult.SUCCESS:
            cls._initialize(cls._is_update_allowed)
        elif google_api_availability.isUserResolvableError(result):
            print("not available")
            done = google_api_availability.showErrorDialogFragment(activity, result, 0)
            print(done)

    @classmethod
    @run_on_ui_thread
    def continue_update(cls):
        google_api_availability: GoogleApiAvailability = (
            GoogleApiAvailability.getInstance()
        )
        result = google_api_availability.isGooglePlayServicesAvailable(activity)
        print(result)
        if result == ConnectionResult.SUCCESS:
            cls._initialize(cls._is_already_running)
        elif google_api_availability.isUserResolvableError(result):
            print("not available")
            done = google_api_availability.showErrorDialogFragment(activity, result, 0)
            print(done)

    @classmethod
    def _is_already_running(cls, app_update_info: AppUpdateInfo):
        if (
            app_update_info.updateAvailability()
            == UpdateAvailability.DEVELOPER_TRIGGERED_UPDATE_IN_PROGRESS
        ):
            cls._start_update_flow(app_update_info)
        else:
            cls.check_for_update()

    @classmethod
    def _is_update_allowed(cls, app_update_info: AppUpdateInfo):
        if (
            app_update_info.updateAvailability() == UpdateAvailability.UPDATE_AVAILABLE
            and app_update_info.isUpdateTypeAllowed(AppUpdateType.IMMEDIATE)
        ):
            cls._start_update_flow(app_update_info)

    @classmethod
    @run_on_ui_thread
    def _start_update_flow(cls, app_update_info: AppUpdateInfo):
        task = cls.__app_update_manager.startUpdateFlow(
            app_update_info,
            activity,
            AppUpdateOptions.newBuilder(AppUpdateType.IMMEDIATE).build(),
        )
        cls.on_complete_listener = OnCompleteListener(cls._restart_if_failed)
        task.addOnCompleteListener(cls.__on_complete_listener)

    @classmethod
    def _restart_if_failed(cls, task):
        if task.isSuccessful() and task.getResult() != activity.RESULT_OK:
            print("failed", task.getResult())
            cls.check_for_update()
