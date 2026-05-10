package org.kivy.admob;

import com.google.android.gms.ads.LoadAdError;

public class AdCallback extends com.google.android.gms.ads.AdListener {

    // Define the interface for callbacks
    public interface AdListener {
        void onAdClicked();
        void onAdClosed();
        void onAdFailedToLoad(LoadAdError adError);
        void onAdImpression();
        void onAdLoaded();
        void onAdOpened();
        void onAdSwipeGestureClicked();
    }

    private AdListener listener;

    // Constructor to inject the listener
    public AdCallback(AdListener listener) {
        this.listener = listener;
    }

    @Override
    public void onAdClicked() {
        if (listener != null) {
            listener.onAdClicked();
        }
    }

    @Override
    public void onAdClosed() {
        if (listener != null) {
            listener.onAdClosed();
        }
    }

    @Override
    public void onAdFailedToLoad(LoadAdError adError) {
        if (listener != null) {
            listener.onAdFailedToLoad(adError);
        }
    }

    @Override
    public void onAdImpression() {
        if (listener != null) {
            listener.onAdImpression();
        }
    }

    @Override
    public void onAdLoaded() {
        super.onAdLoaded();
        if (listener != null) {
            listener.onAdLoaded();
        }
    }

    @Override
    public void onAdOpened() {
        if (listener != null) {
            listener.onAdOpened();
        }
    }

    @Override
    public void onAdSwipeGestureClicked() {
        if (listener != null) {
            listener.onAdSwipeGestureClicked();
        }
    }
}
