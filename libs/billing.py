import json

from kivy.clock import mainthread, triggered
from kivy.event import EventDispatcher
from kivy.properties import ListProperty, ObjectProperty

from components.behaviors import AdaptiveBehavior
from components.sheet import BaseSheet
from sjbillingclient.jclass.billing import BillingResponseCode, ProductType
from sjbillingclient.jclass.purchase import PurchaseState
from sjbillingclient.tools import BillingClient
from android.runnable import run_on_ui_thread  # noqa


class Billing:
    __billing_client: BillingClient = None
    app = None
    event_manager = None
    PRODUCT_ID_YEARLY = "yearly_with_trial"
    PRODUCT_ID_MONTHLY = "monthly_with_trial"
    sheet = None
    _on_subscribed_listener = None

    class EventManager(EventDispatcher):
        product_details_java = ObjectProperty()
        product_details = ListProperty()
        unfetched_product = ListProperty()

    @classmethod
    def initialize(cls, app):
        if not cls.__billing_client:
            cls.app = app
            cls.event_manager = cls.EventManager()
            cls.__billing_client = BillingClient(
                on_purchases_updated=cls.on_purchases_updated
            )
            cls.__billing_client.start_connection(
                on_billing_setup_finished=cls.on_billing_setup_finished,
                on_billing_service_disconnected=lambda: print("disconnected"),
            )

    @classmethod
    def on_billing_setup_finished(cls, billing_result):
        """
        Handles the completion of the billing setup process.

        This method is called when the billing client has finished setting up and
        provides the result of the setup process. Depending on the response code,
        it queries for product details asynchronously, tailored to the chosen product
        type (subscription or in-app purchase).

        :param billing_result: Result of the billing setup, containing response code
            and other relevant information.
        :type billing_result: BillingResult
        :return: None
        """

        def on_query_purchases_response(result, purchases):
            if result.getResponseCode() != BillingResponseCode.OK:
                return

            for purchase in purchases:
                print(purchase.getPurchaseState(), purchase.isAcknowledged())
                if (
                    purchase.getPurchaseState() == PurchaseState.PURCHASED
                    and purchase.isAcknowledged()
                ):
                    cls.app.is_premium = True
                    cls.app.premium_product_id = purchase.getProducts().get(0)
                else:
                    cls.on_purchases_updated(result, False, [purchase])

        cls.__billing_client.query_purchase_async(
            ProductType.SUBS, on_query_purchases_response
        )
        if billing_result.getResponseCode() == BillingResponseCode.OK:
            cls.__billing_client.query_product_details_async(
                product_type=ProductType.SUBS,
                products_ids=[cls.PRODUCT_ID_MONTHLY, cls.PRODUCT_ID_YEARLY],
                on_product_details_response=cls.on_product_details_response,
            )

    @classmethod
    def on_product_details_response(cls, billing_result, product_details_result):
        """
        Handles the response for product details fetch operation. The function processes
        the provided product details or unfetched product details as retrieved from the
        ``product_details_result`` and determines an action based on the ``billing_result``.

        If the billing response is successful (``BillingResponseCode.OK``), the method iterates
        through the available product details and unfetched product details, performing actions
        such as retrieving product details or fetching unfetched products. Ultimately, it launches
        the billing flow for valid product details. The method employs the billing client for
        performing these operations.

        :param billing_result: The result of the billing operation, containing response code
                               and status details.
        :type billing_result: Any
        :param product_details_result: The result containing a list of product details and
                                        unfetched products.
        :type product_details_result: Any
        :return: None
        """

        if billing_result.getResponseCode() == BillingResponseCode.OK:
            product_details_list = product_details_result.getProductDetailsList()
            unfetched_product_list = product_details_result.getUnfetchedProductList()
            cls.event_manager.product_details = [
                cls.__billing_client.get_product_details(
                    product_detail, ProductType.SUBS
                )
                for product_detail in product_details_list
            ]
            cls.event_manager.unfetched_product = [
                cls.__billing_client.get_unfetched_product(unfetched_product)
                for unfetched_product in unfetched_product_list
            ]
            cls.event_manager.product_details_java = product_details_list
            cls.app.is_billing_ready = True

    @classmethod
    def on_purchases_updated(cls, billing_result, null, purchases):
        """
        Handles updates to the purchase state from the billing client.

        This method is called when purchases are updated, either successfully or due to
        an error. It processes purchases based on the type of purchase (acknowledge
        or consume) and logs the response.

        :param billing_result: Result of the billing operation, providing details about
            the state of the billing process and its outcome.
        :type billing_result: Any
        :param null: Placeholder parameter indicating whether the purchase data is
            available or null. Must be evaluated for processing the purchase updates.
        :type null: bool
        :param purchases: List of purchase objects received from the billing response.
            Each object contains information about a user purchase such as tokens,
            subscription status, etc.
        :type purchases: List[Any]
        :return: None
        """
        if billing_result.getResponseCode() == BillingResponseCode.OK and not null:
            for purchase in purchases:
                cls.__billing_client.acknowledge_purchase(
                    purchase_token=purchase.getPurchaseToken(),
                    on_acknowledge_purchase_response=cls.on_acknowledge_purchase_response,
                )
                cls.app.premium_product_id = purchase.getProducts().get(0)

    @classmethod
    @mainthread
    def on_acknowledge_purchase_response(cls, billing_result):
        """
        Handles the acknowledgment of a purchase response from the billing service.

        This method checks the response code from the Billing service. If the response
        code indicates a successful acknowledgment, it displays a message to the user.

        :param billing_result: Represents the result of the purchase acknowledgment
                               process, containing the response code and debug message.
        :type billing_result: BillingResult
        :return: None
        """
        if billing_result.getResponseCode() == BillingResponseCode.OK:
            cls.sheet.dismiss()
            cls.app.is_premium = True
            if cls._on_subscribed_listener:
                cls._on_subscribed_listener()
            SubscribedSheet().open()

    @classmethod
    @run_on_ui_thread
    def launch_billing_flow(cls, product_details):
        cls.__billing_client.launch_billing_flow(product_details=product_details)

    @classmethod
    def pop_premium_purchase_sheet(cls, on_subscribed=None):
        cls._on_subscribed_listener = on_subscribed
        cls.sheet = PremiumPurchaseSheet(screen=cls)
        cls.sheet.open()


class PremiumPurchaseSheet(BaseSheet):
    product_details = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.modalview = type(
            "DummyModalView",
            (),
            {
                "open": lambda *_, **__: None,
                "close": lambda *_, **__: None,
                "dismiss": lambda *_, **__: None,
            },
        )
        if self.screen.event_manager.product_details:
            self.product_details = self.screen.event_manager.product_details
        else:
            self.ids.spinner1.active = True
            self.ids.spinner2.active = True
            self.screen.event_manager.bind(
                product_details=self.setter("product_details")
            )

    def on_product_details(self, _, value):
        if not value:
            return
        self.ids.spinner1.active = False
        self.ids.spinner2.active = False
        for i, data in enumerate(value):
            if data.product_id == self.screen.PRODUCT_ID_YEARLY:
                self.ids.yearly.price = (
                    data.offer_details[0].pricing_phases[-1].formatted_price
                )
                self.ids.yearly.index = i
            else:
                self.ids.monthly.price = (
                    data.offer_details[0].pricing_phases[-1].formatted_price
                )
                self.ids.monthly.index = i

    def launch_billing_flow(self, index):
        product_details = self.screen.event_manager.product_details_java.get(index)
        self.screen.launch_billing_flow([product_details])

    @triggered(0.5)
    def on_open(self, *args):
        self.ids.image.source = "assets/images/premium.jpg"
        self.animate_button()

    @triggered(5, True)
    def animate_button(self):
        self.ids.btn.grow()

    def on_dismiss(self, *args):
        self.animate_button.cancel()


class SubscribedSheet(BaseSheet, AdaptiveBehavior):
    @triggered(5)
    def on_open(self, *args):
        self.dismiss()
