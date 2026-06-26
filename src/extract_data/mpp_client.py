import sys
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

sys.path.append(str(Path(__file__).resolve().parents[1]))

from config import Config
from cursor import CursorStore
from shared.models import Capital, CapitalTrend, InvestOrder, Position, Product, ProductTrend

SSO_URL = "https://sso.monpetitplacement.fr/realms/mpp-prod/protocol/openid-connect/token"
API_URL = "https://api.monpetitplacement.fr/v1"
LIMIT = 200

CURSOR_PRODUCT_TRENDS = 'product_trends'
CURSOR_INVEST_ORDERS = 'invest_orders'


class MPPClient:
    def __init__(
        self,
        config: Config
    ):
        self.user_kyc = None
        self.config = config
        self.session = requests.Session()
        self.timeout = 30
        self.cursor = CursorStore(config)

        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/149.0.0.0 Safari/537.36 Edg/149.0.0.0"
            )
        })

        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"],
        )

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount("https://", adapter)

    def authenticate(
        self
    ) -> None:
        if not self.user_kyc:
            tokens = self._post(SSO_URL, {
                "grant_type": "password",
                "client_id": "mpp-app",
                "username": self.config.username,
                "password": self.config.password,
            })
            self.session.headers.update({
                "Authorization": f"Bearer {tokens['access_token']}"
            })
            user = self._get(self._user_investment_accounts_url())
            self.user_kyc = user["userKyc"].split("/")[-1]


    def fetch_capital(
        self,
        run_at: str
    ) -> Capital:
        data = self._get(self._capital_url())
        return Capital.from_api(data, run_at)


    def fetch_capital_trends(
        self,
        run_at: str
    ) -> list[CapitalTrend]:
        data = self._get(self._financial_history_url())
        return [CapitalTrend.from_api(item, run_at) for item in data["financialValues"]]


    def fetch_products(
        self,
        run_at: str
    ) -> dict[str, Product]:
        data = self._get(self._products_url())
        return {
            item["id"]: Product.from_api(item["id"], item, run_at)
            for item in data["hydra:member"]
        }


    def fetch_positions(
        self,
        run_at: str
    ) -> dict[str, Position]:
        data = self._get(self._positions_url())
        return {
            position.guid: position
            for position in (
                Position.from_api(item, run_at) for item in data["hydra:member"]
            )
        }


    def fetch_product_trends(
        self,
        guid: str,
        slug: str,
        name: str,
        run_at: str,
    ) -> list[ProductTrend]:

        product_trends: list[ProductTrend] = []

        page = 1
        limit = LIMIT

        cursor = self.cursor.get_cursor(
            CURSOR_PRODUCT_TRENDS,
            guid)

        if cursor is not None:
            page = cursor.page
            limit = cursor.size

        while True:
            data = self._get(
                self._product_trends_url(guid, page, limit)
            )

            items = data["hydra:member"]

            for i in items:
                trend = ProductTrend.from_api(guid, slug, name, i, run_at)
                product_trends.append(trend)

            if len(items) == limit:
                page += 1
            else:
                break

        self.cursor.update_cursors(
            CURSOR_PRODUCT_TRENDS,
            guid,
            name,
            slug,
            page,
            limit)

        return product_trends


    def fetch_invest_orders(
        self,
        run_at: str,
        products: dict[str, Product]
    ) -> list[InvestOrder]:

        invest_orders: list[InvestOrder] = []

        page = 1
        limit = LIMIT

        cursor = self.cursor.get_cursor(
            CURSOR_INVEST_ORDERS,
            '-')

        if cursor is not None:
            page = cursor.page
            limit = cursor.size

        while True:

            data = self._get(
                self._invest_orders_url(page, limit)
            )

            items = data["hydra:member"]

            for i in items:
                for d in i["investOrderDetails"]:
                    row_guid = d["product"]["id"]
                    product = products.get(row_guid)
                    order = InvestOrder.from_api(i, d, product, run_at)
                    invest_orders.append(order)

            if len(items) == limit:
                page += 1
            else:
                break

        self.cursor.update_cursors(
            CURSOR_INVEST_ORDERS,
            '-',
            '-',
            '-',
            page,
            limit)


        return invest_orders


    def _get(
        self,
        url: str
    ) -> dict:
        r = self.session.get(url, timeout=self.timeout)
        r.raise_for_status()
        return r.json()


    def _post(
        self,
        url: str,
        data: dict
    ) -> dict:
        r = self.session.post(url, data=data, timeout=self.timeout)
        r.raise_for_status()
        return r.json()


    def _user_investment_accounts_url(
        self
    ) -> str:
        return f"{API_URL}/user_investment_accounts/{self.config.user_investment_account_id}"


    def _financial_history_url(
        self
    ) -> str:
        return f"{API_URL}/user_investment_accounts/{self.config.user_investment_account_id}/financial_history"


    def _capital_url(
        self
    ) -> str:
        return f"{API_URL}/user_investment_accounts/{self.config.user_investment_account_id}/user_financial_capital"


    def _products_url(
        self
    ) -> str:
        return f"{API_URL}/user_kycs/{self.user_kyc}/available_products?limit=200"


    def _positions_url(
        self
    ) -> str:
        return f"{API_URL}/user_investment_accounts/{self.config.user_investment_account_id}/products_current_values?order[amount]=desc"


    def _product_trends_url(
        self,
        guid: str,
        page: int,
        limit: int = 200
    ) -> str:
        return f"{API_URL}/product_values?page={page}&limit={limit}&order%5Bdate%5D=ASC&product={guid}"


    def _invest_orders_url(
        self,
        page: int,
        limit: int = 200
    ) -> str:
        return f"{API_URL}/user_investment_accounts/{self.config.user_investment_account_id}/invest_orders?status%5B%5D=completed&status%5B%5D=accepted&status%5B%5D=refused&page={page}&limit={limit}&exclude_subType%5B%5D=fees&exclude_subType%5B%5D=refund&exclude_subType%5B%5D=end-of-distribution-exchange"
