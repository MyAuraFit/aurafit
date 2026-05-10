from jnius import PythonJavaClass, java_method


class DarkModeListener(PythonJavaClass):
    __javacontext__ = "app"
    __javainterfaces__ = ["org/kivy/android/PythonActivity$DarkModeListener"]

    def __init__(self, on_dark_mode_changed):
        self.on_dark_mode_changed = on_dark_mode_changed

    @java_method("(Z)V")
    def onDarkModeChanged(self, is_dark_mode):
        self.on_dark_mode_changed(is_dark_mode)
