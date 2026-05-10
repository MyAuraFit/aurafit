package org.kivy.admob;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.LoadAdError;

public class RewardedAdLoadCallback extends com.google.android.gms.ads.rewarded.RewardedAdLoadCallback {

    // 🔹 Define a public interface
    public interface RewardedAdLoadListener {
        void onAdLoaded(RewardedAd ad);
        void onAdFailedToLoad(LoadAdError error);
    }

    private RewardedAdLoadListener listener;

    // 🔹 Constructor to inject listener
    public RewardedAdLoadCallback(RewardedAdLoadListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdLoaded(RewardedAd ad) {
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
