package org.kivy.admob;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.LoadAdError;

public class InterstitialAdLoadCallback extends com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback {

    // 🔹 Define a public interface
    public interface InterstitialAdLoadListener {
        void onAdLoaded(InterstitialAd ad);
        void onAdFailedToLoad(LoadAdError error);
    }

    private InterstitialAdLoadListener listener;

    // 🔹 Constructor to inject listener
    public InterstitialAdLoadCallback(InterstitialAdLoadListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdLoaded(InterstitialAd ad) {
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
