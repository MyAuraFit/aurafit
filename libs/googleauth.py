from sjfirebase.tools.mixin import AuthMixin, UserMixin, FirestoreMixin
from kivy.clock import mainthread
from sjcredentials import (
    create_credential_manager,
    get_credential_request,
    get_credential_async,
)
from sjgoogleid import get_google_id_option, get_signin_with_google_option
from sjgoogleid.jclass import GoogleIdTokenCredential
from kvdroid import activity


class GoogleAuthMixin(AuthMixin, UserMixin, FirestoreMixin):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        google_id_option = get_google_id_option()
        self.launch_credential_manager(google_id_option)
        self.app.open_dialog()

    def signup_with_google(self):
        google_option = get_signin_with_google_option()
        self.launch_credential_manager(google_option)
        self.app.open_dialog()

    def launch_credential_manager(self, option):
        request = get_credential_request(option)
        credential_manager = create_credential_manager(activity)
        get_credential_async(
            credential_manager,
            activity,
            request,
            on_result=self.handle_sign_in,
            on_error=lambda _: (self.app.dismiss_dialog(), print(_)),
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
            name = self.get_display_name().split(" ")
            if len(name) > 1:
                first_name, last_name = name
            else:
                first_name = name[0]
                last_name = ""
            data = dict(
                first_name=first_name,
                last_name=last_name,
                email=self.get_email(),
            )
            self.set_document(f"users/{self.get_uid()}", data, merge=True)
            self.manager.current = "home screen"
        else:
            self.toast(message)
        self.app.dismiss_dialog()
