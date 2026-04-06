from datetime import datetime

from kivy.clock import triggered
from kivy.storage.jsonstore import JsonStore
from kvdroid import activity

from libs.addmonths import add_months
from sjplayreview.jclass import ReviewManagerFactory, ReviewManager
from sjplayreview.jinterface import OnCompleteListener
from sjplayservicecommon.jclass import GoogleApiAvailability, ConnectionResult
from android.runnable import run_on_ui_thread  # noqa

_listener = None


@run_on_ui_thread
def launch_play_review():
    global _listener
    print("start the check")
    google_api_availability: GoogleApiAvailability = GoogleApiAvailability.getInstance()
    result = google_api_availability.isGooglePlayServicesAvailable(activity)
    print(result)
    if result == ConnectionResult.SUCCESS:
        manager = ReviewManagerFactory.create(activity)
        request = manager.requestReviewFlow()

        def on_complete(task):
            if task.isSuccessful():
                review_info = task.getResult()
                print("launch review")
                manager.launchReviewFlow(activity, review_info)

        _listener = OnCompleteListener(on_complete)
        request.addOnCompleteListener(_listener)
    elif google_api_availability.isUserResolvableError(result):
        google_api_availability.showErrorDialogFragment(activity, result, 0)


@triggered(300)
def check_for_review():
    store = JsonStore("exact_monthly_data.json")
    now = datetime.now()
    print(now)
    if store.exists("last_run_timestamp"):
        last_run_str = store.get("last_run_timestamp")["timestamp"]
        last_run_time = datetime.strptime(last_run_str, "%Y-%m-%d %H:%M:%S.%f")
        target_next_run_time = add_months(last_run_time, 1)
        if now >= target_next_run_time:
            print("next run")
            launch_play_review()
            store.put("last_run_timestamp", timestamp=str(now))
    else:
        print("first run")
        launch_play_review()
        store.put("last_run_timestamp", timestamp=str(now))
