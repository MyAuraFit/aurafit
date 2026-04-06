from sjfirebase.jclass.firebaseremoteconfig import FirebaseRemoteConfig
from sjfirebase.jclass.firebaseremoteconfigsettings import FirebaseRemoteConfigSettings
from kvdroid.tools import get_resource_identifier


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
    def aurafit_model(cls):
        return cls.__remote_config.getString("aurafit_model")

    @classmethod
    def aurafit_system_prompt(cls):
        return cls.__remote_config.getString("aurafit_system_prompt")
