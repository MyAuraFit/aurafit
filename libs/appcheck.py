from kvdroid import activity

from sjfirebase.jclass.appcheck import (
    FirebaseAppCheck,
    PlayIntegrityAppCheckProviderFactory,
)
from sjfirebase.jclass.firebaseapp import FirebaseApp


def initialize_appcheck():
    FirebaseApp.initializeApp(activity)
    firebase_appcheck = FirebaseAppCheck.getInstance()
    firebase_appcheck.installAppCheckProviderFactory(
        PlayIntegrityAppCheckProviderFactory.getInstance()
    )
