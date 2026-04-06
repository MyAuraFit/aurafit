from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen

# from kvdroid import activity

# from libs.ads import Ads
# from libs.billing import Billing

# from android.runnable import run_on_ui_thread  # noqa
from kivy.utils import QueryDict


class ScreenData(QueryDict):
    pass


class BaseScreen(Screen):
    app = ObjectProperty(None)
    watched_ads = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        self._screen_data = ScreenData()

    def get_screen_data(self):
        return self._screen_data

    def set_screen_data(self, screen_data: ScreenData):
        self._screen_data = ScreenData(screen_data)

    @staticmethod
    def toast(text, length_long=True):
        from kvdroid.tools import toast

        toast(text, length_long)

    # def pop_purchase_notice_sheet(self):
    #     sheet = PurchaseNoticeSheet(screen=self)
    #     sheet.open()
    #
    # @triggered(300, True)
    # def watch_ads_interval(self):
    #     Ads.load_rewarded_ad(None)


# class PurchaseNoticeSheet(BaseSheet, AdaptiveBehavior):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def subscribe(self):
#         Billing.pop_premium_purchase_sheet(on_subscribed=self.dismiss)
#
#     def watch_ads(self):
#         self.ids.spinner.active = True
#         Ads.load_rewarded_ad(
#             on_user_earned_reward=lambda _: self.trigger_watch_ads_interval()
#         )
#
#     def go_back_home(self):
#         self.dismiss()
#         self.screen.manager.current = "home screen"
#
#     def trigger_watch_ads_interval(self):
#         self.screen.watched_ads = True
#         self.ids.spinner.active = False
#         self.screen.watch_ads_interval()
#         self.screen.bind(on_leave=lambda *_: self.screen.watch_ads_interval.cancel())
#         self.screen.bind(on_enter=lambda *_: self.screen.watch_ads_interval())
#         self.dismiss()
#
#
# class GoogleAuthMixin(AuthMixin, UserMixin, FirestoreMixin):
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#         google_id_option = get_google_id_option()
#         self.launch_credential_manager(google_id_option)
#         self.app.dialog.open()
#
#     def signup_with_google(self):
#         google_option = get_signin_with_google_option()
#         self.launch_credential_manager(google_option)
#         self.app.dialog.open()
#
#     def launch_credential_manager(self, option):
#         request = get_credential_request(option)
#         credential_manager = create_credential_manager(activity)
#         get_credential_async(
#             credential_manager,
#             activity,
#             request,
#             on_result=self.handle_sign_in,
#             on_error=lambda _: (self.app.dialog.dismiss(), print(_)),
#         )
#
#     @mainthread
#     def handle_sign_in(self, credential):
#         if (
#             credential.getType()
#             == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
#         ):
#             google_id_token_credential = GoogleIdTokenCredential.createFrom(
#                 credential.getData()
#             )
#             id_token = google_id_token_credential.getIdToken()
#             auth_credential = self.get_google_auth_provider_credential(id_token)
#             self.sign_in_with_credential(auth_credential, self.on_sign_in_complete)
#
#     @mainthread
#     def on_sign_in_complete(self, is_success, message):
#         if is_success:
#             name = self.get_display_name().split(" ")
#             if len(name) > 1:
#                 first_name, last_name = name
#             else:
#                 first_name = name[0]
#                 last_name = "Farmi"
#             data = dict(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=self.get_email(),
#             )
#             self.set_document(f"users/{self.get_uid()}", data, merge=True)
#             self.manager.current = "home screen"
#         else:
#             self.toast(message)
#         self.app.dialog.dismiss()
