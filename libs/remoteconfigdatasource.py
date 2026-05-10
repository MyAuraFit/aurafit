import json

from kvdroid.tools import get_resource_identifier
from sjfirebase.jclass.firebaseremoteconfig import FirebaseRemoteConfig
from sjfirebase.jclass.firebaseremoteconfigsettings import FirebaseRemoteConfigSettings


class RemoteConfigDataSource:
    __remote_config: FirebaseRemoteConfig = FirebaseRemoteConfig.getInstance()
    __remote_config.setConfigSettingsAsync(
        FirebaseRemoteConfigSettings.Builder()
        .setMinimumFetchIntervalInSeconds(3600)
        .build()
    )
    __remote_config.setDefaultsAsync(
        get_resource_identifier("remote_config_defaults", "xml")
    )
    __remote_config.fetchAndActivate()

    @classmethod
    def subscriptions(cls):
        return json.loads(cls.__remote_config.getString("subscriptions"))

    @classmethod
    def one_time_products(cls):
        return json.loads(cls.__remote_config.getString("one_time_products"))

    @classmethod
    def weekly(cls):
        return cls.__remote_config.getString("weekly")

    @classmethod
    def monthly(cls):
        return cls.__remote_config.getString("monthly")

    @classmethod
    def yearly(cls):
        return cls.__remote_config.getString("yearly")

    @classmethod
    def single_shot(cls):
        return cls.__remote_config.getString("single_shot")

    @classmethod
    def quick_pack(cls):
        return cls.__remote_config.getString("quick_pack")

    @classmethod
    def stylist_pack(cls):
        return cls.__remote_config.getString("stylist_pack")

    @classmethod
    def fashion_pack(cls):
        return cls.__remote_config.getString("fashion_pack")
