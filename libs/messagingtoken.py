from kivy.storage.jsonstore import JsonStore
from sjfirebasemessaging.jclass.FirebaseMessaging import FirebaseMessaging
from sjfirebasemessaging.jinterface.OnCompleteListener import OnCompleteListener

from sjfirebase.tools.mixin import FirestoreMixin, UserMixin

__all__ = ("generate_firebase_messaging_token",)


_listener = None


def generate_firebase_messaging_token():
    global _listener
    store = JsonStore("firebase-messaging-token.json")
    if store.exists("token"):
        return store.get("token")
    task = FirebaseMessaging.getInstance().getToken()

    def on_complete(t):
        if t.isSuccessful():
            token = t.getResult()
            uid = UserMixin().get_uid()
            FirestoreMixin().set_document(f"users/{uid}", {"token": token}, merge=True)
            store.put("token", token=token)

    _listener = OnCompleteListener(on_complete)
    task.addOnCompleteListener(_listener)
    return None
