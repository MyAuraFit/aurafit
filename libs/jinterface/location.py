from jnius import PythonJavaClass, java_method


class FusedLocationCallback(PythonJavaClass):
    __javacontext__ = "app"
    __javainterfaces__ = ["org/kivy/location/FusedLocationCallback"]

    def __init__(self, on_location_result, on_location_availability):
        self.on_location_result = on_location_result
        self.on_location_availability = on_location_availability

    @java_method("(Lcom/google/android/gms/location/LocationResult;)V")
    def onLocationResult(self, location_result):
        self.on_location_result(location_result.getLocations())

    @java_method("(Lcom/google/android/gms/location/LocationAvailability;)V")
    def onLocationAvailability(self, availability):
        self.on_location_availability(availability.isLocationAvailable())


class FusedLocationListener(PythonJavaClass):
    __javacontext__ = "app"
    __javainterfaces__ = ["com/google/android/gms/location/LocationListener"]

    def __init__(self, on_location_changed):
        self.on_location_changed = on_location_changed

    @java_method("(Landroid/location/Location;)V")
    def onLocationChanged(self, location):
        self.on_location_changed(location)
