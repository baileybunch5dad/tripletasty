# from tastytrade_api.authentication import TastytradeAuth
import os
import requests
import json
import json
import threading
import websocket
from enum import Enum
import time
from dotenv import load_dotenv

# from d10h882

if not os.path.exists(".env"):
    print("Please create a file named .env with two properties to access your TastyTrade account for reading data")
    print("TT_USERNAME=<Your-AccountId>")
    print("TT_PASSWORD=<Your-Password>")
    exit
    
# Load the .env file
load_dotenv()

if os.getenv('TT_USERNAME') is None or os.getenv('TT_PASSWORD') is None:
    print("Please set environment variables TT_USERNAME and TT_PASSWORD")
    exit
    
class TTOrderType(Enum):
  LIMIT = 'Limit'
  MARKET = 'Market'

class TTPriceEffect(Enum):
  CREDIT = 'Credit'
  DEBIT = 'Debit'

class TTOrderStats(Enum):
  RECEIVED = 'Received'
  CANCELLED = 'Cancelled'
  FILLED = 'Filled'
  EXPIRED = 'Expired'
  LIVE = 'Live'
  REJECTED = 'Rejected'

class TTTimeInForce(Enum):
  DAY = 'Day'
  GTC = 'GTC'
  GTD = 'GTD'

class TTInstrumentType(Enum):
  EQUITY = 'Equity'
  EQUITY_OPTION = 'Equity Option'
  FUTURE = 'Future'
  FUTURE_OPTION = 'Future Option'
  NOTIONAL_MARKET = 'Notional Market'

class TTLegAction(Enum):
  STO = 'Sell to Open'
  STC = 'Sell to Close'
  BTO = 'Buy to Open'
  BTC = 'Buy to Close'

class TTOptionSide(Enum):
  PUT = 'P'
  CALL = 'C'

class TTOption:
  symbol: str = None

  def __init__(self, symbol: str = None, date: str = None,
                side: TTOptionSide = None, strike: float = None) -> None:
    symbol = symbol.ljust(6, ' ')
    strike = str(int(strike * 100)).replace('.', '').zfill(6)
    self.symbol = symbol + date + side.value + '0' + strike + '0'

class TTOrder:
  order_type: TTOrderType = TTOrderType.LIMIT
  tif: TTTimeInForce = TTTimeInForce.GTC
  price: str = "0.00"
  price_effect: TTPriceEffect = TTPriceEffect.CREDIT
  legs: list = []
  body: dict = {}

  def __init__(self, tif: TTTimeInForce = None, price: float = None,
                price_effect: TTPriceEffect = None, order_type: TTOrderType = None) -> None:
    self.tif = tif
    self.order_type = order_type
    self.price = '{:2f}'.format(price)
    self.price_effect = price_effect

  def add_leg(self, instrument_type: TTInstrumentType = None,
              symbol: str = None, quantity: int = 0,
              action: TTLegAction = None) -> list:
    if len(self.legs) >= 4:
      print(f'Error: cannot have more than 4 legs per order.')
      return
    if instrument_type is None or symbol == None or quantity == 0 or action is None:
      print(f'Invalid parameters')
      print(f'instrument_type: {instrument_type}')
      print(f'symbol: {symbol}')
      print(f'quantity')
    
    self.legs.append({
      'instrument-type': instrument_type.value,
      'symbol': symbol,
      'quantity': quantity,
      'action': action.value
    })

  def build_order(self) -> dict:
    self.body = {
      'time-in-force': self.tif.value,
      'price': self.price,
      'price-effect': self.price_effect.value,
      'order-type': self.order_type.value,
      'legs': self.legs
    }
    print(json.dumps(self.body))
    return self.body

class TTConfig:
    # [Config]
    # determines if we use the TastyTrade production endpoint or the certification endpoint
    use_prod=True

    # Enable/Disable asking for Multi-Factor authentication
    use_mfa=False

    # [Credentials]
    # if your password has a % in it, you need to double it up.
    # for example, if your password is 12345%54321 then you should
    # enter it as 12345%%54321
    username=os.getenv("TT_USERNAME")
    password=os.getenv("TT_PASSWORD")

    # URI and WSS should not need to be changed unless tastytrade changes them
    # [URI]
    cert_uri="https://api.cert.tastyworks.com"
    prod_uri="https://api.tastyworks.com"

    # [WSS]
    cert_wss="wss://streamer.cert.tastyworks.com"
    prod_wss="wss://streamer.tastyworks.com"


class TTApi:
    session_token: str = None
    remember_token: str = None
    streamer_token: str = None
    streamer_uri: str = None
    streamer_websocket_uri: str = None
    streamer_level: str = None
    tt_uri: str = None
    wss_uri: str = None
    headers: dict = {}
    user_data: dict = {}
    use_prod: bool = False
    use_mfa: bool = False

    def __init__(self, tt_config: TTConfig = TTConfig()) -> None:
        self.headers["Content-Type"] = "application/json"
        self.headers["Accept"] = "application/json"
        self.tt_config = tt_config

        if self.tt_config.use_prod:
            self.tt_uri = self.tt_config.prod_uri
            self.tt_wss = self.tt_config.prod_wss
        else:
            self.tt_uri = self.tt_config.cert_uri
            self.tt_wss = self.tt_config.prod_wss

    def __post(
        self, endpoint: str = None, body: dict = {}, headers: dict = None
    ) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.post(
            self.tt_uri + endpoint, data=json.dumps(body), headers=headers
        )
        if response.status_code == 201:
            return response.json()
        print(f"Error {response.status_code}")
        print(f"Endpoint: {endpoint}")
        print(f"Body: {body}")
        print(f"Headers: {headers}")
        print(f"Response: {response.text}")
        return None

    def __get(
        self, endpoint, body: dict = {}, headers: dict = None, params: dict = {}
    ) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.get(
            self.tt_uri + endpoint,
            data=json.dumps(body),
            headers=headers,
            params=params,
        )
        if response.status_code == 200:
            return response.json()
        print(f"Error {response.status_code}")
        print(f"Endpoint: {endpoint}")
        print(f"Body: {body}")
        print(f"Headers: {headers}")
        print(f"Response: {response.text}")
        return None

    def __delete(
        self, endpoint: str = None, body: dict = {}, headers: dict = None
    ) -> requests.Response:
        if headers is None:
            headers = self.headers
        response = requests.delete(
            self.tt_uri + endpoint, data=json.dumps(body), headers=headers
        )
        if response.status_code == 204:
            return response
        print(f"Error {response.status_code}")
        print(f"Endpoint: {endpoint}")
        print(f"Body: {body}")
        print(f"Headers: {headers}")
        print(f"Response: {response.text}")
        return None

    def login(self) -> bool:
        body = {
            "login": self.tt_config.username,
            "password": self.tt_config.password,
            "remember-me": True,
        }

        if self.tt_config.use_mfa is True:
            mfa = input("MFA: ")
            self.headers["X-Tastyworks-OTP"] = mfa

        response = self.__post("/sessions", body=body)
        if response is None:
            return False

        self.user_data = response["data"]["user"]
        self.session_token = response["data"]["session-token"]
        self.headers["Authorization"] = self.session_token

        if self.tt_config.use_mfa is True:
            del self.headers["X-Tastyworks-OTP"]

        return True

    def fetch_dxfeed_token(self) -> bool:
        response = self.__get("/quote-streamer-tokens")

        if response is None:
            return False

        self.streamer_token = response["data"]["token"]
        self.streamer_uri = response["data"]["streamer-url"]
        self.streamer_websocket_uri = f'{response["data"]["websocket-url"]}/cometd'
        self.streamer_level = response["data"]["level"]

        print(self.streamer_uri)

        return True

    def get_quote_tokens(self) -> bool:
        response = self.__get("/api-quote-tokens")

        if response is None:
            return False

        self.streamer_token = response["data"]["token"]
        self.streamer_websocket_uri = f'{response["data"]["dxlink-url"]}'

        print(self.streamer_websocket_uri)

        return True

    def logout(self) -> bool:
        self.__delete("/sessions")
        return True

    def validate(self) -> bool:
        response = self.__post("/sessions/validate")

        if response is None:
            return False

        self.user_data["external-id"] = response["data"]["external-id"]
        self.user_data["id"] = response["data"]["id"]

        return True

    def fetch_accounts(self) -> bool:
        response = self.__get("/customers/me/accounts")

        if response is None:
            return False

        self.user_data["accounts"] = []
        for account in response["data"]["items"]:
            self.user_data["accounts"].append(account["account"])

        return True

    def fetch_positions(self, account: str = "") -> bool:
        if account == "":
            return False

        response = self.__get(f"/accounts/{account}/positions")

        if response is None:
            return False

        if "account_positions" not in self.user_data:
            self.user_data["account_positions"] = []

        for position in response["data"]["items"]:
            self.user_data["account_positions"].append(position["symbol"].split()[0])

        return True

    def market_metrics(self, symbols: list[str] = []) -> any:
        symbols = ",".join(str(x) for x in symbols)
        query = {"symbols": symbols}
        response = self.__get(f"/market-metrics", params=query)
        return response

    def option_chains(self, symbol: str = "") -> any:
        response = self.__get(f"/option-chains/{symbol}/nested")
        if response is None:
            return False
        return response

    def symbol_search(self, symbol) -> any:
        response = self.__get(f"/symbols/search/{symbol}")
        return response

    def get_instrument_equities(self, symbol) -> any:
        response = self.__get(f"/instruments/equities/{symbol}")
        return response

    def get_instrument_options(self, symbol) -> any:
        response = self.__get(f"/instruments/equity-options/{symbol}")
        return response

    def get_equity_options(self, symbol) -> any:
        response = self.__get(f"/option-chains/{symbol}/nested")
        return response

    def get_public_watchlists(self) -> any:
        response = self.__get(f"/public-watchlists")
        return response

    def get_watchlists(self, watchlist: str = None) -> any:
        if watchlist is None:
            response = self.__get(f"/watchlists")
        else:
            response = self.__get(f"/watchlists/{watchlist}")
        return response

    def simple_order(self, order: TTOrder = None) -> bool:
        if order is None:
            print(f"You need to supply an order.")
            return False

        response = self.__post(
            f'/accounts/{self.user_data["accounts"][0]["account"]["account-number"]}/orders/dry-run',
            body=order.build_order(),
        )

        if response is None:
            return False

        print(json.dumps(response))
        return True
    

ttapi = TTApi()

print("Login")
if not ttapi.login():
    exit()


print("Validate")
if not ttapi.validate():
    exit()

print("Fetch accounts")
if not ttapi.fetch_accounts():
    exit()

print("Fetch dxFeed token")
if not ttapi.fetch_dxfeed_token():
    exit()

exit()
