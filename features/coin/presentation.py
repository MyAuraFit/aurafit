__all__ = ("CoinScreen",)

from pathlib import Path

from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.behaviors import ToggleButtonBehavior

from features.basescreen import BaseScreen
from libs.ads import Ads
from libs.billing import Billing
from libs.remoteconfigdatasource import RemoteConfigDataSource
from sjfirebase.tools.mixin import UserMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class CoinScreen(BaseScreen, UserMixin):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.product_details = []
        self.product_details_list = None
        self.billing_client = Billing()
        self.billing_client.bind(
            on_billing_setup_finished=self.on_billing_setup_finished,
            on_billing_service_disconnected=self.on_billing_service_disconnected,
            on_product_details_response=self.on_product_details_response,
            on_purchases_updated=self.on_purchases_updated,
            on_acknowledge_purchase_response=self.on_acknowledge_purchase_response,
        )
        self.is_setup_finished = False

    def on_enter(self):
        self.billing_client.start_connection()

    def on_leave(self):
        self.billing_client.end_connection()
        self.ids.inapp.clear_widgets()
        self.product_details.clear()
        self.product_details_list = None

    def on_billing_setup_finished(self, _, is_response_ok):
        if is_response_ok:
            self.is_setup_finished = True
            self.billing_client.query_product_details(
                "inapp", RemoteConfigDataSource.one_time_products()
            )

    def on_billing_service_disconnected(self, _):
        print("Billing service disconnected")

    @mainthread
    def on_product_details_response(self, _, is_response_ok, product_details_list, __):
        if not is_response_ok:
            return
        self.product_details_list = product_details_list
        self.product_details = [
            self.billing_client.get_product_details(
                product_type="inapp", product_detail=product_detail
            )
            for product_detail in product_details_list
        ]
        for product_detail in self.product_details:
            self._add_product_widget(product_detail)
        self.app.dismiss_dialog()

    def _add_product_widget(self, product_detail):
        offer_detail = product_detail.offer_details[0]
        if product_detail.product_id == "stylist_pack":
            self.ids.btn.amount = offer_detail.price_amount_micros / 1_000_000
            self.ids.btn.currency = offer_detail.price_currency_code
        self.ids.inapp.add_widget(
            Factory.ProductWidget(
                title=product_detail.name,
                amount=offer_detail.price_amount_micros / 1_000_000,
                product_id=product_detail.product_id,
                currency=offer_detail.price_currency_code,
                name=getattr(RemoteConfigDataSource, product_detail.product_id)(),
                active=product_detail.product_id == "stylist_pack",
                group="one_time_products",
                slash="",
                on_product_selected=lambda *_: {
                    setattr(  # noqa
                        self.ids.btn,
                        "amount",
                        offer_detail.price_amount_micros / 1_000_000,
                    ),
                    setattr(  # noqa
                        self.ids.btn, "currency", offer_detail.price_currency_code
                    ),
                },
            )
        )

    @mainthread
    def on_purchases_updated(self, _, is_response_ok, purchases):
        if is_response_ok:
            for purchase in purchases:
                from sjbillingclient.jclass.purchase import PurchaseState

                if purchase.getPurchaseState() == PurchaseState.PURCHASED:
                    Factory.PurchasedSheet().open()
                    return

    def on_acknowledge_purchase_response(self, _, is_response_ok): ...

    def launch_billing_flow(self):
        widget = next(
            (
                w
                for w in ToggleButtonBehavior.get_group("one_time_products")
                if w.active
            ),
            None,
        )
        if widget is None:
            return
        for i, product_detail in enumerate(self.product_details):
            if product_detail.product_id == widget.product_id:  # type: ignore
                offer_detail = product_detail.offer_details[0]
                self.billing_client.launch_billing_flow(
                    product_details=[self.product_details_list.get(i)],
                    offer_token=offer_detail.offer_token,
                    obfuscated_account_id=self.get_uid(),
                )
                return

    def show_ads(self):
        def award_coins(reward_item):
            self.ids.balance.coins += reward_item.getAmount() / 2
            self.toast("Coins awarded: " + str(reward_item.getAmount() / 2))

        self.app.open_dialog()
        Ads.load_rewarded_ad(
            on_user_earned_reward=award_coins,
            on_show_ad=self.app.dismiss_dialog,
            on_ad_error=self.app.dismiss_dialog,
            uid=self.get_uid(),
        )
