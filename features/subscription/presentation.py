__all__ = ("SubscriptionScreen",)

from pathlib import Path

from kivy.clock import triggered, mainthread
from kivy.factory import Factory
from kivy.lang import Builder
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.utils import platform

from features.basescreen import BaseScreen
from libs.billing import Billing
from libs.remoteconfigdatasource import RemoteConfigDataSource
from sjfirebase.tools.mixin import UserMixin

kv_file_path = Path(__file__).with_suffix(".kv")
Builder.load_file(str(kv_file_path))


class SubscriptionScreen(BaseScreen, UserMixin):
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

    @triggered(3, True)
    def animate_button(self):
        self.ids.btn.grow()

    def on_enter(self):
        if platform == "android":
            self.app.theme_cls.set_bar_foreground_theme("white")

        self.animate_button()
        self.app.open_dialog()
        self.billing_client.start_connection()

    def on_leave(self):
        if platform == "android":
            from kvdroid.tools.darkmode import dark_mode

            self.app.theme_cls.set_bar_foreground_theme(
                "white" if dark_mode() else "black"
            )
        self.animate_button.cancel()
        self.app.dismiss_dialog()
        self.billing_client.end_connection()
        self.ids.subs.clear_widgets()
        self.product_details.clear()
        self.product_details_list = None

    def on_billing_setup_finished(self, _, is_response_ok):
        if is_response_ok:
            self.is_setup_finished = True
            self.billing_client.query_product_details(
                "subs", RemoteConfigDataSource.subscriptions()
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
                product_type="subs", product_detail=product_detail
            )
            for product_detail in product_details_list
        ]
        for detail in self.product_details:
            for offer in detail.offer_details:
                self._add_product_widget(detail.product_id, offer)
        self.app.dismiss_dialog()

    def _add_product_widget(self, product_id, offer):
        phase = offer.pricing_phases[0]
        if offer.base_plan_id == "monthly":
            self.ids.btn.amount = phase.price_amount_micros / 1_000_000
            self.ids.btn.currency = phase.price_currency_code
        self.ids.subs.add_widget(
            Factory.ProductWidget(
                title=getattr(RemoteConfigDataSource, offer.base_plan_id)(),
                amount=phase.price_amount_micros / 1_000_000,
                product_id=product_id,
                base_plan_id=offer.base_plan_id,
                currency=phase.price_currency_code,
                name=offer.base_plan_id,
                period=offer.base_plan_id,
                active=offer.base_plan_id == "monthly",
                group="subscriptions",
                on_product_selected=lambda *_: {
                    setattr(  # noqa
                        self.ids.btn, "amount", phase.price_amount_micros / 1_000_000
                    ),
                    setattr(  # noqa
                        self.ids.btn, "currency", phase.price_currency_code
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
                    self.manager.go_back()
                    Factory.PurchasedSheet().open()
                    return

    def on_acknowledge_purchase_response(self, _, is_response_ok): ...

    def launch_billing_flow(self):
        widget = next(
            (w for w in ToggleButtonBehavior.get_group("subscriptions") if w.active),
            None,
        )
        if widget is None:
            return
        for i, detail in enumerate(self.product_details):
            if detail.product_id != widget.product_id:  # type: ignore
                continue
            for offer in detail.offer_details:
                if offer.base_plan_id == widget.base_plan_id:  # type: ignore
                    self.billing_client.launch_billing_flow(
                        product_details=[self.product_details_list.get(i)],
                        offer_token=offer.offer_token,
                        obfuscated_account_id=self.get_uid(),
                    )
                    return
