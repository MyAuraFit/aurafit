from kivy.clock import mainthread, Clock

from kvdroid import activity
from sjcredentials import (
    create_credential_manager,
    get_credential_request,
    get_credential_async,
)
from sjfirebase.tools.mixin import AuthMixin, UserMixin, FirestoreMixin
from sjgoogleid import get_google_id_option, get_signin_with_google_option
from sjgoogleid.jclass import GoogleIdTokenCredential


class GoogleAuthMixin(AuthMixin, UserMixin, FirestoreMixin):
    def signup_with_google(self):
        google_option = get_signin_with_google_option()
        self.launch_credential_manager(google_option)
        self.app.open_dialog()

    def launch_credential_manager(self):
        self.app.open_dialog()
        request = get_credential_request(get_google_id_option())
        credential_manager = create_credential_manager(activity)
        get_credential_async(
            credential_manager,
            activity,
            request,
            on_result=self.handle_sign_in,
            on_error=lambda _: {
                self.app.dismiss_dialog(),
                print(_),
                Clock.schedule_once(lambda _: self.app.pop_disconnect_sheet()),
            },
        )

    @mainthread
    def handle_sign_in(self, credential):
        if (
            credential.getType()
            == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
        ):
            google_id_token_credential = GoogleIdTokenCredential.createFrom(
                credential.getData()
            )
            id_token = google_id_token_credential.getIdToken()
            auth_credential = self.get_google_auth_provider_credential(id_token)
            self.sign_in_with_credential(auth_credential, self.on_sign_in_complete)

    @mainthread
    def on_sign_in_complete(self, is_success, message):
        if is_success:
            self.manager.current = "home screen"
        else:
            self.toast(message)
        self.app.dismiss_dialog()
