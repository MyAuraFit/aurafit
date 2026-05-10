package org.kivy.admob;

import com.google.android.gms.ads.AdError;

public class FullScreenContentCallback extends com.google.android.gms.ads.FullScreenContentCallback {

    // 🔹 Define an interface for Python to hook into
    public interface FullScreenContentListener {
        void onAdClicked();
        void onAdDismissedFullScreenContent();
        void onAdFailedToShowFullScreenContent(AdError adError);
        void onAdImpression();
        void onAdShowedFullScreenContent();
    }

    private FullScreenContentListener listener;

    // 🔹 Constructor
    public FullScreenContentCallback(FullScreenContentListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdClicked() {
        if (listener != null) {
            listener.onAdClicked();
        }
    }

    @Override
    public void onAdDismissedFullScreenContent() {
        if (listener != null) {
            listener.onAdDismissedFullScreenContent();
        }
    }

    @Override
    public void onAdFailedToShowFullScreenContent(AdError adError) {
        if (listener != null) {
            listener.onAdFailedToShowFullScreenContent(adError);
        }
    }

    @Override
    public void onAdImpression() {
        if (listener != null) {
            listener.onAdImpression();
        }
    }

    @Override
    public void onAdShowedFullScreenContent() {
        if (listener != null) {
            listener.onAdShowedFullScreenContent();
        }
    }
}
