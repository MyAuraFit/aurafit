from threading import Thread

from android.runnable import run_on_ui_thread  # noqa
from kvdroid import activity
from kvdroid.tools import toast
from sjadmob.jclass import (
    MobileAds,
    AdRequest,
    FullScreenContentCallback,
    RewardedAd,
    RewardedAdLoadCallback,
)
from sjadmob.jclass.RewardItem import RewardItem
from sjadmob.jclass.ServerSideVerificationOptions import ServerSideVerificationOptions
from sjadmob.jinterface import (
    FullScreenContentListener,
    RewardedAdLoadListener,
    OnUserEarnedRewardListener,
)


class Ads:
    rewarded_ad = None
    is_loading_ad = False
    is_showing_ad = False

    @classmethod
    def initialize(cls):
        Thread(target=MobileAds.initialize, args=(activity,)).start()

    @classmethod
    @run_on_ui_thread
    def load_rewarded_ad(cls, on_user_earned_reward, on_show_ad, on_ad_error, uid=None):
        if cls.is_showing_ad:
            return

        def on_ad_loaded(ad: RewardedAd):
            cls.rewarded_ad = ad
            if uid:
                cls.rewarded_ad.setServerSideVerificationOptions(
                    ServerSideVerificationOptions.Builder().setUserId(uid).build()
                )
            cls.is_loading_ad = False
            cls._full_screen_content_listener = FullScreenContentListener(
                lambda: print("clicked")
            )
            cls.rewarded_ad.setFullScreenContentCallback(
                FullScreenContentCallback(cls._full_screen_content_listener)
            )
            on_show_ad()
            cls.show_ad(on_user_earned_reward)

        def on_ad_failed_to_load(ad):
            cls.is_loading_ad = False
            print(ad.message)
            toast("Ads failing to load due to unstable network connection", True)
            on_ad_error()

        cls._ad_load_listener = RewardedAdLoadListener(
            on_ad_loaded, on_ad_failed_to_load
        )
        RewardedAd.load(
            activity,
            "ca-app-pub-9820946188047221/1008557427",
            AdRequest.Builder().build(),
            RewardedAdLoadCallback(cls._ad_load_listener),
        )
        cls.is_loading_ad = True

    @classmethod
    def show_ad(cls, on_user_earned_reward=None):
        if cls.is_loading_ad or not cls.rewarded_ad:
            return
        cls.is_showing_ad = True
        cls._listener = OnUserEarnedRewardListener(
            lambda reward_item: cls.on_user_earned_reward(
                reward_item, on_user_earned_reward
            )
        )
        cls.rewarded_ad.show(activity, cls._listener)

    @classmethod
    def on_user_earned_reward(cls, reward_item: RewardItem, callback):
        if callback:
            callback(reward_item)
        cls.is_showing_ad = False
        cls.rewarded_ad = None
