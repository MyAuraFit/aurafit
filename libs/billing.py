from typing import Literal

from kivy.clock import triggered
from kivy.event import EventDispatcher

from android.runnable import run_on_ui_thread  # noqa
from components.behaviors import AdaptiveBehavior
from components.sheet import BaseSheet
from sjbillingclient import QueryDict
from sjbillingclient.jclass.billing import BillingResponseCode
from sjbillingclient.tools import BillingClient


class Billing(EventDispatcher):
    __events__ = (
        "on_billing_setup_finished",
        "on_billing_service_disconnected",
        "on_query_purchases_response",
        "on_product_details_response",
        "on_purchases_updated",
        "on_acknowledge_purchase_response",
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__billing_client = None

    def start_connection(self):
        self.__billing_client = BillingClient(
            on_purchases_updated=self.__on_purchases_updated
        )
        self.__billing_client.start_connection(
            on_billing_setup_finished=self.__on_billing_setup_finished,
            on_billing_service_disconnected=self.__on_billing_service_disconnected,
        )

    def end_connection(self):
        self.__billing_client.end_connection()
        self.__billing_client = None

    def is_ready(self) -> bool:
        return self.__billing_client.is_ready()

    def get_product_details(
        self, product_type: Literal["subs", "inapp"], product_detail
    ) -> QueryDict:
        return self.__billing_client.get_product_details(
            product_detail=product_detail,
            product_type=product_type,
        )

    def query_product_details(
        self, product_type: Literal["subs", "inapp"], product_ids: list[str]
    ):
        self.__billing_client.query_product_details_async(
            product_type=product_type,
            products_ids=product_ids,
            on_product_details_response=self.__on_product_details_response,
        )

    def query_purchases(self, product_type: Literal["subs", "inapp"]):
        self.__billing_client.query_purchases_async(
            product_type=product_type,
            on_query_purchases_response=self.__on_query_purchases_response,
        )

    def acknowledge_purchase(self, purchase_token: str):
        self.__billing_client.acknowledge_purchase(
            purchase_token=purchase_token,
            on_acknowledge_purchase_response=self.__on_acknowledge_purchase_response,
        )

    @run_on_ui_thread
    def launch_billing_flow(
        self,
        product_details,
        offer_token=None,
        obfuscated_account_id=None,
        obfuscated_profile_id=None,
    ):
        self.__billing_client.launch_billing_flow(
            product_details=product_details,
            offer_token=offer_token,
            obfuscated_account_id=obfuscated_account_id,
            obfuscated_profile_id=obfuscated_profile_id,
        )

    def __on_billing_service_disconnected(self):
        self.dispatch("on_billing_service_disconnected")

    def on_billing_service_disconnected(self):
        pass

    def __on_billing_setup_finished(self, billing_result):
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
        self.dispatch(
            "on_billing_setup_finished",
            billing_result.getResponseCode() == BillingResponseCode.OK,
        )

    def on_billing_setup_finished(self, is_response_ok):
        pass

    def __on_query_purchases_response(self, result, purchases):
        self.dispatch(
            "on_query_purchases_response",
            result.getResponseCode() == BillingResponseCode.OK,
            purchases,
        )

    def on_query_purchases_response(self, is_response_ok, purchases):
        pass

    def __on_product_details_response(self, billing_result, product_details_result):
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
        self.dispatch(
            "on_product_details_response",
            billing_result.getResponseCode() == BillingResponseCode.OK,
            product_details_result.getProductDetailsList(),
            product_details_result.getUnfetchedProductList(),
        )

    def on_product_details_response(
        self, is_response_ok, product_details_list, unfetched_product_list
    ):
        pass

    def __on_purchases_updated(self, billing_result, null, purchases):
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

        self.dispatch(
            "on_purchases_updated",
            billing_result.getResponseCode() == BillingResponseCode.OK and not null,
            purchases,
        )

    def on_purchases_updated(self, is_response_ok, purchases):
        pass

    def __on_acknowledge_purchase_response(self, billing_result):
        """
        Handles the acknowledgment of a purchase response from the billing service.

        This method checks the response code from the Billing service. If the response
        code indicates a successful acknowledgment, it displays a message to the user.

        :param billing_result: Represents the result of the purchase acknowledgment
                               process, containing the response code and debug message.
        :type billing_result: BillingResult
        :return: None
        """
        self.dispatch(
            "on_acknowledge_purchase_response",
            billing_result.getResponseCode() == BillingResponseCode.OK,
        )

    def on_acknowledge_purchase_response(self, is_response_ok):
        pass


class PurchasedSheet(BaseSheet, AdaptiveBehavior):
    @triggered(5)
    def on_open(self, *args):
        self.dismiss()
