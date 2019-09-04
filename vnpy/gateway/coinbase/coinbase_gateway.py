import hashlib
import hmac
import json
import sys
import time
from copy import copy
from datetime import datetime, timedelta
from threading import Lock
import base64
import uuid

from typing import List, Sequence

from requests import ConnectionError

from vnpy.event import Event
from vnpy.api.rest import Request, RestClient
from vnpy.api.websocket import WebsocketClient
from vnpy.trader.event import EVENT_TIMER
from vnpy.trader.constant import (
    Direction,
    Exchange,
    OrderType,
    Product,
    Status,
    Interval
)
from vnpy.trader.gateway import BaseGateway
from vnpy.trader.object import (
    TickData,
    OrderData,
    TradeData,
    AccountData,
    ContractData,
    BarData,
    OrderRequest,
    CancelRequest,
    SubscribeRequest,
    HistoryRequest
)

REST_HOST = "https://api.pro.coinbase.com"
WEBSOCKET_HOST = "wss://ws-feed.pro.coinbase.com"
SANDBOX_REST_HOST = "https://api-public.sandbox.pro.coinbase.com"
SANDBOX_WEBSOCKET_HOST = "wss://ws-feed-public.sandbox.pro.coinbase.com"

DIRECTION_VT2COINBASE = {Direction.LONG: "buy", Direction.SHORT: "sell"}
DIRECTION_COINBASE2VT = {v: k for k, v in DIRECTION_VT2COINBASE.items()}

ORDERTYPE_VT2COINBASE = {
    OrderType.LIMIT: "limit",
    OrderType.MARKET: "market",
}
ORDERTYPE_COINBASE2VT = {v: k for k, v in ORDERTYPE_VT2COINBASE.items()}

INTERVAL_VT2COINBASE = {
    Interval.MINUTE: "1m",
    Interval.HOUR: "1h",
    Interval.DAILY: "1d",
}

TIMEDELTA_MAP = {
    Interval.MINUTE: timedelta(minutes=1),
    Interval.HOUR: timedelta(hours=1),
    Interval.DAILY: timedelta(days=1),
}

cancelDict = {}  # orderid:cancelreq
orderDict = {}  # sysid:order
orderSysDict = {}  # orderid:sysid


class CoinbaseGateway(BaseGateway):
    """
    VN Trader Gateway for coinbase connection
    """

    default_setting = {
        "ID": "",
        "Secret": "",
        "passphrase": "",
        "会话数": 3,
        "server": ["REAL", "SANDBOX"],
        "proxy_host": "",
        "proxy_port": "",
    }
    exchanges = [Exchange.COINBASE]

    def __init__(self, event_engine):
        """Constructor"""
        super(CoinbaseGateway, self).__init__(event_engine, "COINBASE")
        self.rest_api = CoinbaseRestApi(self)
        self.ws_api = CoinbaseWebsocketApi(self)

    def connect(self, setting: dict):
        """"""
        key = setting["ID"]
        secret = setting["Secret"]
        session_number = setting["会话数"]
        proxy_host = setting["proxy_host"]
        proxy_port = setting["proxy_port"]
        server = setting['server']
        passphrase = setting['passphrase']

        if proxy_port.isdigit():
            proxy_port = int(proxy_port)
        else:
            proxy_port = 0

        self.rest_api.connect(key, secret, passphrase, session_number, server,
                              proxy_host, proxy_port)

        self.ws_api.connect(
            key,
            secret,
            passphrase,
            server,
            proxy_host,
            proxy_port)

    def subscribe(self, req: SubscribeRequest):
        """"""
        self.ws_api.subscribe(req)

    def send_order(self, req: OrderRequest):
        """"""
        return self.rest_api.send_order(req)

    def cancel_order(self, req: CancelRequest):
        """"""
        self.rest_api.cancel_order(req)

    def query_account(self):
        """"""
        return self.rest_api.query_account()

    def query_position(self):
        """
        Query holding positions.
        """
        pass

    def query_history(self, req: HistoryRequest):
        """
        Query bar history data.
        """
        pass

    def close(self):
        """"""
        self.rest_api.stop()
        self.ws_api.stop()

    def process_timer_event(self, event: Event):
        """"""
        self.rest_api.reset_rate_limit()
        self.init_query()

    def init_query(self):
        """"""
        self.rest_api.query_account()


class CoinbaseWebsocketApi(WebsocketClient):
    """
    Coinbase WEBSOCKET API
    """

    def __init__(self, gateway: BaseGateway):
        """"""
        super(CoinbaseWebsocketApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""
        self.passphrase = ""

        self.callbacks = {
            "ticker": self.on_orderbook,
            "l2update": self.on_orderbook,
            "snapshot": self.on_orderbook,
            "received": self.on_order_received,
            "open": self.on_order_open,
            "done": self.on_order_done,
            "match": self.on_order_match,
        }
        self.ticks = {}

        self.accounts = {}
        self.orderbooks = {}

    def connect(
            self,
            key: str,
            secret: str,
            passphrase: str,
            server: str,
            proxy_host: str,
            proxy_port: int):
        """"""
        self.gateway.write_log("开始连接ws接口")
        self.key = key
        self.secret = secret.encode()
        self.passphrase = passphrase

        if server == "REAL":
            self.init(WEBSOCKET_HOST, proxy_host, proxy_port)
        else:
            self.init(SANDBOX_WEBSOCKET_HOST, proxy_host, proxy_port)
        self.start()

        self.gateway.event_engine.register(EVENT_TIMER, self.gateway.process_timer_event)

    def subscribe(self, req: SubscribeRequest):
        """"""
        symbol = req.symbol
        exchange = req.exchange

        orderbook = OrderBook(symbol, exchange, self.gateway)
        self.orderbooks[symbol] = orderbook

        sub_req = {
            "type": "subscribe",
            "product_ids": [symbol],
            "channels": ["user", "level2", "ticker"],
        }

        timestamp = str(time.time())
        message = timestamp + 'GET' + '/users/self/verify'
        auth_headers = get_auth_header(
            timestamp,
            message,
            self.key,
            self.secret,
            self.passphrase)
        sub_req['signature'] = auth_headers['CB-ACCESS-SIGN']
        sub_req['key'] = auth_headers['CB-ACCESS-KEY']
        sub_req['passphrase'] = auth_headers['CB-ACCESS-PASSPHRASE']
        sub_req['timestamp'] = auth_headers['CB-ACCESS-TIMESTAMP']

        self.send_packet(sub_req)

    def on_connected(self):
        """
        callback when connection is established
        """
        self.gateway.write_log("Websocket API连接成功")

    def on_disconnected(self):
        """"""
        self.gateway.write_log("Websocket API连接断开")

    def on_packet(self, packet: dict):
        """
        callback when data is received and  unpacked
        """
        if packet['type'] == 'error':
            self.gateway.write_log(
                "Websocket API报错： %s" % packet['message'])
            self.gateway.write_log(
                "Websocket API报错原因是： %s" % packet['reason'])
            self.active = False

        else:
            callback = self.callbacks.get(packet['type'], None)
            if callback:
                if packet['type'] not in ['ticker', 'snapshot', 'l2update']:
                    callback(packet)
                else:
                    product_id = packet['product_id']
                    callback(packet, product_id)

    def on_orderbook(self, packet: dict, product_id: str):
        """
        Call back when data is used to update orderbook
        """
        orderbook = self.orderbooks[product_id]
        orderbook.on_message(packet)

    def on_order_received(self, packet: dict):
        """
        Call back when order is received by Coinbase
        """
        client_oid = packet['client_oid']
        sysid = packet['order_id']

        order = OrderData(
            symbol=packet['product_id'],
            exchange=Exchange.COINBASE,
            type=ORDERTYPE_COINBASE2VT[packet['order_type']],
            orderid=sysid,
            direction=DIRECTION_COINBASE2VT[packet['side']],
            price=float(packet['price']),
            volume=float(packet['size']),
            time=packet['time'],
            gateway_name=self.gateway_name,
        )

        order.traded = 0
        order.status = Status.NOTTRADED

        orderSysDict[client_oid] = sysid
        orderDict[sysid] = order

        if client_oid in cancelDict:
            req = cancelDict[client_oid]
            self.gateway.cancel_order(req)

        self.gateway.on_order(copy(order))

    def on_order_open(self, packet: dict):
        """
        Call back when the order is on the orderbook
        """
        orderid = packet['order_id']
        order = orderDict.get(orderid)
        order.traded = float(order.volume) - float(packet['remaining_size'])
        if order.traded:
            order.status = Status.PARTTRADED

        self.gateway.on_order(copy(order))

    def on_order_done(self, packet: dict):
        """
        Call back when the order is done
        """
        order = orderDict.get(packet['order_id'], None)
        if not order:
            return
        order.traded = order.volume - float(packet['remaining_size'])
        if packet['reason'] == 'filled':
            order.status = Status.ALLTRADED
        else:
            order.status = Status.CANCELLED
        self.gateway.on_order(copy(order))

    def on_order_match(self, packet: dict):
        """"""
        if packet['maker_order_id'] in orderDict:
            order = orderDict[packet['maker_order_id']]
        else:
            order = orderDict[packet['taker_order_id']]

        trade = TradeData(
            symbol=packet['product_id'],
            exchange=Exchange.COINBASE,
            orderid=order.orderid,
            tradeid=packet['trade_id'],
            direction=DIRECTION_COINBASE2VT[packet['side']],
            price=packet['price'],
            volume=packet['size'],
            time=datetime.strptime(
                packet['time'], "%Y-%m-%dT%H:%M:%S.%fZ"),
            gateway_name=self.gateway_name,
        )
        self.gateway.on_trade(trade)


class OrderBook():
    """
    Used to maintain orderbook of coinbase data
    """

    def __init__(self, symbol: str, exchange: Exchange, gateway: BaseGateway):
        """
        one symbol per orderbook
        """

        self.asks = dict()
        self.bids = dict()
        self.gateway = gateway
        self.newest_tick = TickData(
            "COINBASE", symbol, exchange, datetime.now())
        self.first_update = False

    def on_message(self, d: dict):
        """
        callback by websocket when server send orderbook data
        """
        if d['type'] == 'l2update':
            dt = datetime.strptime(
                d["time"][:-4] + d['time'][-1], "%Y-%m-%dT%H:%M:%S.%fZ")
            self.on_update(d['changes'][0], dt)
        elif d['type'] == 'snapshot':
            self.on_snapshot(d['asks'], d['bids'])
        else:
            self.on_ticker(d)

    def on_update(self, d: list, dt):
        """
        call back  when type is 12update
        """
        size = d[2]
        price = d[1]
        side = d[0]

        if side == 'buy':
            if float(price) in self.bids:
                if size == 0:
                    del self.bids[float(price)]
                else:
                    self.bids[float(price)] = float(size)
            else:
                self.bids[float(price)] = float(size)
        else:
            if float(price) in self.asks:
                if size == 0:
                    del self.asks[float(price)]
                else:
                    self.asks[float(price)] = float(size)
            else:
                self.asks[float(price)] = float(size)

        self.generate_tick(dt)


    def on_ticker(self, d: dict):
        """
        call back when type is ticker
        """
        tick = self.newest_tick

        tick.open_price = float(d['open_24h'])
        tick.high_price = float(d['high_24h'])
        tick.low_price = float(d['low_24h'])
        tick.last_price = float(d['price'])
        tick.volume = float(d['volume_24h'])

        self.gateway.on_tick(copy(tick))

    def on_snapshot(self, asks: Sequence[List], bids: Sequence[List]):
        """
        call back when type is snapshot
        """
        for price, size in asks:
            self.asks[float(price)] = float(size)

        for price, size in bids:
            self.bids[float(price)] = float(size)

    def generate_tick(self, dt: datetime):
        """"""
        tick = self.newest_tick

        bids_keys = self.bids.keys()
        bids_keys = sorted(bids_keys, reverse=True)

        tick.bid_price_1 = bids_keys[0]
        tick.bid_price_2 = bids_keys[1]
        tick.bid_price_3 = bids_keys[2]
        tick.bid_price_4 = bids_keys[3]
        tick.bid_price_5 = bids_keys[4]

        tick.bid_volume_1 = self.bids[bids_keys[0]]
        tick.bid_volume_2 = self.bids[bids_keys[1]]
        tick.bid_volume_3 = self.bids[bids_keys[2]]
        tick.bid_volume_4 = self.bids[bids_keys[3]]
        tick.bid_volume_5 = self.bids[bids_keys[4]]

        asks_keys = self.asks.keys()
        asks_keys = sorted(asks_keys)

        tick.ask_price_1 = asks_keys[0]
        tick.ask_price_2 = asks_keys[1]
        tick.ask_price_3 = asks_keys[2]
        tick.ask_price_4 = asks_keys[3]
        tick.ask_price_5 = asks_keys[4]

        tick.ask_volume_1 = self.asks[asks_keys[0]]
        tick.ask_volume_2 = self.asks[asks_keys[1]]
        tick.ask_volume_3 = self.asks[asks_keys[2]]
        tick.ask_volume_4 = self.asks[asks_keys[3]]
        tick.ask_volume_5 = self.asks[asks_keys[4]]

        tick.datetime = dt
        self.gateway.on_tick(copy(tick))


class CoinbaseRestApi(RestClient):
    """
    Coinbase REST API
    """

    def __init__(self, gateway: BaseGateway):
        """"""
        super(CoinbaseRestApi, self).__init__()

        self.gateway = gateway
        self.gateway_name = gateway.gateway_name

        self.key = ""
        self.secret = ""
        self.passphrase = ""

        self.order_count = 1_000_000
        self.order_count_lock = Lock()

        self.connect_time = 0

        self.accounts = {}

        self.rate_limit = 5
        self.rate_limit_remaining = 5

    def sign(self, request):
        """
        Generate Coinbase signature
        """
        timestamp = str(time.time())
        message = ''.join([timestamp, request.method,
                           request.path, request.data or ""])
        request.headers = (get_auth_header(timestamp, message,
                                           self.key,
                                           self.secret,
                                           self.passphrase))
        return request

    def connect(
        self,
        key: str,
        secret: str,
        passphrase: str,
        session_number: int,
        server: str,
        proxy_host: str,
        proxy_port: int,
    ):
        """
        Initialize connection to REST server
        """
        self.key = key
        self.secret = secret.encode()
        self.passphrase = passphrase

        self.connect_time = (
            int(datetime.now().strftime("%y%m%d%H%M%S")) * self.order_count
        )
        if server == "REAL":
            self.init(REST_HOST, proxy_host, proxy_port)
        else:
            self.init(SANDBOX_REST_HOST, proxy_host, proxy_port)

        self.start(session_number)
        self.query_instrument()
        self.query_orders()

        self.gateway.write_log("REST API启动成功")

    def query_instrument(self):
        """
        Get the instrument of Coinbase
        """
        self.add_request(
            "GET",
            "/products",
            callback=self.on_query_instrument,
            params={},
            on_error=self.on_query_instrument_error,
        )

    def query_orders(self):
        """"""
        self.add_request(
            "GET",
            "/orders?status=all",
            callback=self.on_query_orders,
            params={},
            on_error=self.on_query_orders_error,
        )

    def query_account(self):
        """"""
        self.add_request(
            "GET",
            "/accounts",
            callback=self.on_query_account,
            params={},
            on_error=self.on_query_account_error,
        )

    def on_query_account(self, data, request):
        """"""
        for acc in data:
            account_id = str(acc['id'])
            account = self.accounts.get(account_id, None)
            if not account:
                account = AccountData(accountid=account_id,
                                      gateway_name=self.gateway_name)
                self.accounts[account_id] = account

            account.balance = acc.get("balance", account.balance)
            account.available = acc.get("available", account.available)
            account.frozen = acc.get("hold", account.frozen)

            self.gateway.on_account(copy(account))

    def on_query_account_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request):
        """"""
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_query_orders_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request):
        """"""
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_query_orders(self, data, request):
        """"""
        for d in data:
            date, time = d['created_at'].split('T')
            if d['status'] == 'open':
                if not float(d['filled_size']):
                    status = Status.NOTTRADED
                else:
                    status = Status.PARTTRADED
            else:
                if d['size'] == d['filled_size']:
                    status = Status.ALLTRADED
                else:
                    status = Status.CANCELLED
            order = OrderData(
                symbol=d['product_id'],
                gateway_name=self.gateway_name,
                exchange=Exchange.COINBASE,
                orderid=d['id'],
                direction=DIRECTION_COINBASE2VT[d['side']],
                price=float(d['price']),
                volume=float(d['size']),
                traded=float(d['filled_size']),
                time=time.replace('Z', ""),
                status=status,
            )
            self.gateway.on_order(copy(order))

            orderDict[order.orderid] = order
            orderSysDict[order.orderid] = order.orderid

        self.gateway.write_log(u'委托信息查询成功')

    def on_query_instrument_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Request):
        """
        Callback when sending order caused exception.
        """
        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_query_instrument(self, data, request):
        """"""
        for d in data:
            contract = ContractData(
                symbol=d['id'],
                exchange=Exchange.COINBASE,
                name=d['display_name'],
                product=Product.SPOT,
                pricetick=d['quote_increment'],
                size=d['base_min_size'],
                stop_supported=False,
                net_position=True,
                history_data=False,
                gateway_name=self.gateway_name,
            )

            self.gateway.on_contract(contract)

            self.gateway.write_log("")

    def send_order(self, req: OrderRequest):
        """"""
        if not self.check_rate_limit():
            return

        orderid = str(uuid.uuid1())

        data = {
            "size": req.volume,
            "product_id": req.symbol,
            "side": DIRECTION_VT2COINBASE[req.direction],
            "type": ORDERTYPE_VT2COINBASE[req.type],
            "client_oid": orderid,
        }

        if req.type == OrderType.LIMIT:
            data['price'] = req.price


        order = req.create_order_data(orderid, self.gateway_name)
        self.add_request(
            "POST",
            "/orders",
            callback=self.on_send_order,
            data=json.dumps(data),
            params={},
            extra=order,
            on_failed=self.on_send_order_failed,
            on_error=self.on_send_order_error,
        )

        return order.vt_orderid

    def on_send_order_failed(self, status_code: str, request: Request):
        """
        Callback when sending order failed on server.
        """
        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        if request.response.text:
            data = request.response.json()
            error = data["message"]
            msg = f"委托失败，状态码：{status_code}，信息：{error}"
        else:
            msg = f"委托失败，状态码：{status_code}"

        self.gateway.write_log(msg)

    def on_send_order_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Request):
        """
        Callback when sending order caused exception.
        """

        order = request.extra
        order.status = Status.REJECTED
        self.gateway.on_order(order)

        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_send_order(self, data, request):
        """"""
        pass

    def cancel_order(self, req: CancelRequest):
        """"""
        if not self.check_rate_limit():
            return

        orderid = req.orderid

        if orderid not in orderSysDict:
            cancelDict[orderid] = req

        self.add_request(
            "DELETE",
            "/orders/" + orderid,
            callback=self.on_cancel_order,
            params={},
            on_error=self.on_cancel_order_error,
            on_failed=self.on_cancel_order_failed,
        )

    def on_cancel_order_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Request):
        """
        Callback when cancelling order failed on server.
        """
        # Record exception if not ConnectionError
        if not issubclass(exception_type, ConnectionError):
            self.on_error(exception_type, exception_value, tb, request)

    def on_cancel_order(self, data, request):
        """Websocket will push a new order status"""
        pass

    def on_cancel_order_failed(self, status_code: str, request: Request):
        """
        Callback when sending order failed on server.
        """
        if request.response.text:
            data = request.response.json()
            error = data["message"]
            msg = f"委托失败，状态码：{status_code}，信息：{error}"
        else:
            msg = f"委托失败，状态码：{status_code}"

        self.gateway.write_log(msg)

    def on_failed(self, status_code: int, request: Request):
        """
        Callback to handle request failed.
        """
        data = request.response.json()
        error = data['message']
        msg = f"请求失败，状态码：{status_code},信息：{error}"
        self.gateway.write_log(msg)

    def on_error(
            self,
            exception_type: type,
            exception_value: Exception,
            tb,
            request: Request):
        """
        Callback to handler request exception.
        """
        msg = f"触发异常，状态码：{exception_type}，信息：{exception_value}"
        self.gateway.write_log(msg)

        sys.stderr.write(
            self.exception_detail(exception_type, exception_value, tb, request)
        )

    def reset_rate_limit(self):
        """
        reset the rate limit every 1 sec
        """
        self.rate_limit_remaining = 5

    def check_rate_limit(self):
        """
        Called before send requests
        """
        if self.rate_limit_remaining:
            self.rate_limit_remaining -= 1
            return True
        else:
            self.gateway.write_log("已超出请求速率上限，请稍后重试")
            return False


def get_auth_header(
        timestamp,
        message,
        api_key,
        secret_key,
        passphrase):
    """"""
    message = message.encode("ascii")
    hmac_key = base64.b64decode(secret_key)
    signature = hmac.new(hmac_key, message, hashlib.sha256)
    signature_b64 = base64.b64encode(signature.digest()).decode('utf-8')
    return{
        'Content-Type': 'Application/JSON',
        'CB-ACCESS-SIGN': signature_b64,
        'CB-ACCESS-TIMESTAMP': timestamp,
        'CB-ACCESS-KEY': api_key,
        'CB-ACCESS-PASSPHRASE': passphrase
    }
