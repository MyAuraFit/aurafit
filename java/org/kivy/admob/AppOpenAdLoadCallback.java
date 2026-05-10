package org.kivy.admob;

import com.google.android.gms.ads.appopen.AppOpenAd;
import com.google.android.gms.ads.LoadAdError;

public class AppOpenAdLoadCallback extends AppOpenAd.AppOpenAdLoadCallback {

    // 🔹 Define a public interface
    public interface AppOpenAdLoadListener {
        void onAdLoaded(AppOpenAd ad);
        void onAdFailedToLoad(LoadAdError error);
    }

    private AppOpenAdLoadListener listener;

    // 🔹 Constructor to inject listener
    public AppOpenAdLoadCallback(AppOpenAdLoadListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdLoaded(AppOpenAd ad) {
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
