package org.kivy.admob;
import com.google.android.gms.ads.rewardedinterstitial.RewardedInterstitialAd;
import com.google.android.gms.ads.LoadAdError;

public class RewardedInterstitialAdLoadCallback extends com.google.android.gms.ads.rewardedinterstitial.RewardedInterstitialAdLoadCallback {

    // 🔹 Define a public interface
    public interface RewardedInterstitialAdLoadListener {
        void onAdLoaded(RewardedInterstitialAd ad);
        void onAdFailedToLoad(LoadAdError error);
    }

    private RewardedInterstitialAdLoadListener listener;

    // 🔹 Constructor to inject listener
    public RewardedInterstitialAdLoadCallback(RewardedInterstitialAdLoadListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdLoaded(RewardedInterstitialAd ad) {
        if (listener != null) {
            listener.onAdLoaded(ad);
        }
    }

    @Override
    public void onAdFailedToLoad(LoadAdError error) {
        if (listener != null) {
            listener.onAdFailedToLoad(error);
        }
    }
}
