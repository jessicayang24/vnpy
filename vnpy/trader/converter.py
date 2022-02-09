""""""
from copy import copy
from typing import Dict, List, DefaultDict
from collections import defaultdict

from .engine import MainEngine
from .object import (
    ContractData,
    OrderData,
    TradeData,
    PositionData,
    OrderRequest,
    Status,
    TickData,
    BarData
)
from .constant import Direction, Offset, Exchange
from vnpy.event import Event
from .event import EVENT_TRADE_UPDATE, EVENT_ORDER_UPDATE


class OffsetConverter:
    """"""

    def __init__(self, main_engine: MainEngine):
        """"""
        self.main_engine: MainEngine = main_engine
        self.holdings: Dict[str, "PositionHolding"] = {}

    def before_handle_bar(self, bar: BarData) -> None:
        """"""
        if not self.is_convert_required(bar.vt_symbol):
            return

        holding = self.get_position_holding(bar.vt_symbol)
        holding.before_handle_bar(bar)

    def before_handle_tick(self, tick: TickData) -> None:
        """"""
        if not self.is_convert_required(tick.vt_symbol):
            return

        holding = self.get_position_holding(tick.vt_symbol)
        holding.before_handle_tick(tick)

    def update_position(self, position: PositionData) -> None:
        """"""
        if not self.is_convert_required(position.vt_symbol):
            return

        holding = self.get_position_holding(position.vt_symbol)
        holding.update_position(position)

    def update_trade(self, trade: TradeData) -> None:
        """"""
        if not self.is_convert_required(trade.vt_symbol):
            return

        holding = self.get_position_holding(trade.vt_symbol)
        holding.update_trade(trade)

    def update_order(self, order: OrderData) -> None:
        """"""
        if not self.is_convert_required(order.vt_symbol):
            return

        holding = self.get_position_holding(order.vt_symbol)
        holding.update_order(order)

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return

        holding = self.get_position_holding(req.vt_symbol)
        holding.update_order_request(req, vt_orderid)

    def get_position_holding(self, vt_symbol: str) -> "PositionHolding":
        """"""
        holding = self.holdings.get(vt_symbol, None)
        if not holding:
            contract = self.main_engine.get_contract(vt_symbol)
            holding = PositionHolding(contract, self.main_engine)
            self.holdings[vt_symbol] = holding
        return holding

    def convert_order_request(
        self,
        req: OrderRequest,
        lock: bool,
        net: bool = False
    ) -> List[OrderRequest]:
        """"""
        if not self.is_convert_required(req.vt_symbol):
            return [req]

        holding = self.get_position_holding(req.vt_symbol)

        if lock:
            return holding.convert_order_request_lock(req)
        elif net:
            return holding.convert_order_request_net(req)
        elif req.exchange in [Exchange.SHFE, Exchange.INE]:
            return holding.convert_order_request_shfe(req)
        else:
            return [req]

    def is_convert_required(self, vt_symbol: str) -> bool:
        """
        Check if the contract needs offset convert.
        """
        contract = self.main_engine.get_contract(vt_symbol)

        # Only contracts with long-short position mode requires convert
        if not contract:
            return False
        elif contract.net_position:
            return False
        else:
            return True


class PositionHolding:
    """"""

    def __init__(self, contract: ContractData, main_engin: MainEngine):
        """"""
        self.vt_symbol: str = contract.vt_symbol
        self.main_engine = main_engin
        self.exchange: Exchange = contract.exchange

        self.active_orders: Dict[str, OrderData] = {}
        self.orders: Dict[str, OrderData] = {}
        self.next_price_orders: List[OrderData] = []     # 未填写理论成交价的订单，为了计算实盘和模拟盘之间的误差

        self.trades: DefaultDict[str, List[TradeData]] = defaultdict(list)

        self.long_pos: float = 0
        self.long_yd: float = 0
        self.long_td: float = 0

        self.short_pos: float = 0
        self.short_yd: float = 0
        self.short_td: float = 0

        self.long_pos_frozen: float = 0
        self.long_yd_frozen: float = 0
        self.long_td_frozen: float = 0

        self.short_pos_frozen: float = 0
        self.short_yd_frozen: float = 0
        self.short_td_frozen: float = 0

    def update_position(self, position: PositionData) -> None:
        """"""
        if position.direction == Direction.LONG:
            self.long_pos = position.volume
            self.long_yd = position.yd_volume
            self.long_td = self.long_pos - self.long_yd
        else:
            self.short_pos = position.volume
            self.short_yd = position.yd_volume
            self.short_td = self.short_pos - self.short_yd

    def update_order(self, order: OrderData) -> None:
        """"""
        if order.vt_orderid not in self.orders:
            self.orders[order.vt_orderid] = order
            self.next_price_orders.append(order)
        else:
            old_order = self.orders.get(order.vt_orderid)
            old_order.status = order.status
            old_order.traded = order.traded
            old_order.datetime = order.datetime
            old_order.offset = order.offset

        if order.is_active():
            self.active_orders[order.vt_orderid] = order
        else:
            if order.vt_orderid in self.active_orders:
                self.active_orders.pop(order.vt_orderid)

        self.calculate_frozen()

    def put_order_update(self, order):
        evt = Event(EVENT_ORDER_UPDATE, order)
        self.main_engine.event_engine.put(evt)

    def put_trade_update(self, trade):
        evt = Event(EVENT_TRADE_UPDATE, trade)
        self.main_engine.event_engine.put(evt)

    def before_handle_bar(self, bar: BarData):
        """
        更新backtest_price
        :param bar:
        :return:
        """

        for order in self.next_price_orders:
            if order.direction == Direction.LONG:
                # 参照回测
                trade_price = min(order.price, bar.open_price)
            else:
                trade_price = max(order.price, bar.open_price)
            order.backtest_price = trade_price
            self.put_order_update(order)
            self.update_order_relation_trade(order)

    def before_handle_tick(self, tick: TickData):
        """
        更新backtest_price
        :param tick:
        :return:
        """
        for order in self.next_price_orders:
            if order.direction == Direction.LONG:
                # 参照回测
                trade_price = min(order.price, tick.ask_price_1)
            else:
                trade_price = max(order.price, tick.bid_price_1)
            order.backtest_price = trade_price
            self.put_order_update(order)
            self.update_order_relation_trade(order)
        self.next_price_orders.clear()

    def update_order_relation_trade(self, order: OrderData):
        """
        更新order对应trade的backtest_price
        :param order:
        :return:
        """
        order_trades = self.trades.get(order.vt_orderid, [])
        for trade in order_trades:
            trade.backtest_price = order.backtest_price
            trade.__post_init__()
            self.put_trade_update(trade)

    def update_order_request(self, req: OrderRequest, vt_orderid: str) -> None:
        """"""
        gateway_name, orderid = vt_orderid.split(".", 1)

        order = req.create_order_data(orderid, gateway_name)
        self.update_order(order)

    def update_trade(self, trade: TradeData) -> None:
        """
        批次成交
        :param trade:
        :return:
        """
        self.trades[trade.vt_orderid].append(trade)
        if trade.direction == Direction.LONG:
            if trade.offset == Offset.OPEN:
                self.long_td += trade.volume
            elif trade.offset == Offset.CLOSETODAY:
                self.short_td -= trade.volume
            elif trade.offset == Offset.CLOSEYESTERDAY:
                self.short_yd -= trade.volume
            elif trade.offset == Offset.CLOSE:
                if trade.exchange in [Exchange.SHFE, Exchange.INE]:
                    self.short_yd -= trade.volume
                else:
                    self.short_td -= trade.volume

                    if self.short_td < 0:
                        self.short_yd += self.short_td
                        self.short_td = 0
        else:
            if trade.offset == Offset.OPEN:
                self.short_td += trade.volume
            elif trade.offset == Offset.CLOSETODAY:
                self.long_td -= trade.volume
            elif trade.offset == Offset.CLOSEYESTERDAY:
                self.long_yd -= trade.volume
            elif trade.offset == Offset.CLOSE:
                if trade.exchange in [Exchange.SHFE, Exchange.INE]:
                    self.long_yd -= trade.volume
                else:
                    self.long_td -= trade.volume

                    if self.long_td < 0:
                        self.long_yd += self.long_td
                        self.long_td = 0

        order = self.get_trade_order(trade)
        if order:
            trade.signal_price = order.signal_price
            trade.limit_price = order.price
            trade.backtest_price = order.backtest_price
            # 重新计算post_init
            trade.__post_init__()

        self.long_pos = self.long_td + self.long_yd
        self.short_pos = self.short_td + self.short_yd

    def get_trade_order(self, trade: TradeData):

        return self.orders.get(trade.vt_orderid)

    def calculate_frozen(self) -> None:
        """
        计算冻结持仓
        :return:
        """
        self.long_pos_frozen = 0
        self.long_yd_frozen = 0
        self.long_td_frozen = 0

        self.short_pos_frozen = 0
        self.short_yd_frozen = 0
        self.short_td_frozen = 0

        for order in self.active_orders.values():
            # Ignore position open orders
            if order.offset == Offset.OPEN:
                continue

            # 每个订单的未成交部分
            frozen = order.volume - order.traded

            if order.direction == Direction.LONG:
                if order.offset == Offset.CLOSETODAY:
                    self.short_td_frozen += frozen
                elif order.offset == Offset.CLOSEYESTERDAY:
                    self.short_yd_frozen += frozen
                elif order.offset == Offset.CLOSE:
                    self.short_td_frozen += frozen

                    if self.short_td_frozen > self.short_td:
                        self.short_yd_frozen += (self.short_td_frozen
                                                 - self.short_td)
                        self.short_td_frozen = self.short_td
            elif order.direction == Direction.SHORT:
                if order.offset == Offset.CLOSETODAY:
                    self.long_td_frozen += frozen
                elif order.offset == Offset.CLOSEYESTERDAY:
                    self.long_yd_frozen += frozen
                elif order.offset == Offset.CLOSE:
                    self.long_td_frozen += frozen

                    if self.long_td_frozen > self.long_td:
                        self.long_yd_frozen += (self.long_td_frozen
                                                - self.long_td)
                        self.long_td_frozen = self.long_td

            self.long_pos_frozen = self.long_td_frozen + self.long_yd_frozen
            self.short_pos_frozen = self.short_td_frozen + self.short_yd_frozen

    def convert_order_request_shfe(self, req: OrderRequest) -> List[OrderRequest]:
        """"""
        if req.offset == Offset.OPEN:
            return [req]

        if req.direction == Direction.LONG:
            pos_available = self.short_pos - self.short_pos_frozen
            td_available = self.short_td - self.short_td_frozen
        else:
            pos_available = self.long_pos - self.long_pos_frozen
            td_available = self.long_td - self.long_td_frozen

        if req.volume > pos_available:
            return []
        elif req.volume <= td_available:
            req_td = copy(req)
            req_td.offset = Offset.CLOSETODAY
            return [req_td]
        else:
            req_list = []

            if td_available > 0:
                req_td = copy(req)
                req_td.offset = Offset.CLOSETODAY
                req_td.volume = td_available
                req_list.append(req_td)

            req_yd = copy(req)
            req_yd.offset = Offset.CLOSEYESTERDAY
            req_yd.volume = req.volume - td_available
            req_list.append(req_yd)

            return req_list

    def convert_order_request_lock(self, req: OrderRequest) -> List[OrderRequest]:
        """"""
        if req.direction == Direction.LONG:
            td_volume = self.short_td
            yd_available = self.short_yd - self.short_yd_frozen
        else:
            td_volume = self.long_td
            yd_available = self.long_yd - self.long_yd_frozen

        # If there is td_volume, we can only lock position
        if td_volume:
            req_open = copy(req)
            req_open.offset = Offset.OPEN
            return [req_open]
        # If no td_volume, we close opposite yd position first
        # then open new position
        else:
            close_volume = min(req.volume, yd_available)
            open_volume = max(0, req.volume - yd_available)
            req_list = []

            if yd_available:
                req_yd = copy(req)
                if self.exchange in [Exchange.SHFE, Exchange.INE]:
                    req_yd.offset = Offset.CLOSEYESTERDAY
                else:
                    req_yd.offset = Offset.CLOSE
                req_yd.volume = close_volume
                req_list.append(req_yd)

            if open_volume:
                req_open = copy(req)
                req_open.offset = Offset.OPEN
                req_open.volume = open_volume
                req_list.append(req_open)

            return req_list

    def convert_order_request_net(self, req: OrderRequest) -> List[OrderRequest]:
        """"""
        if req.direction == Direction.LONG:
            pos_available = self.short_pos - self.short_pos_frozen
            td_available = self.short_td - self.short_td_frozen
            yd_available = self.short_yd - self.short_yd_frozen
        else:
            pos_available = self.long_pos - self.long_pos_frozen
            td_available = self.long_td - self.long_td_frozen
            yd_available = self.long_yd - self.long_yd_frozen

        # Split close order to close today/yesterday for SHFE/INE exchange
        if req.exchange in {Exchange.SHFE, Exchange.INE}:
            reqs = []
            volume_left = req.volume

            if td_available:
                td_volume = min(td_available, volume_left)
                volume_left -= td_volume

                td_req = copy(req)
                td_req.offset = Offset.CLOSETODAY
                td_req.volume = td_volume
                reqs.append(td_req)

            if volume_left and yd_available:
                yd_volume = min(yd_available, volume_left)
                volume_left -= yd_volume

                yd_req = copy(req)
                yd_req.offset = Offset.CLOSEYESTERDAY
                yd_req.volume = yd_volume
                reqs.append(yd_req)

            if volume_left > 0:
                open_volume = volume_left

                open_req = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs
        # Just use close for other exchanges
        else:
            reqs = []
            volume_left = req.volume

            if pos_available:
                close_volume = min(pos_available, volume_left)
                volume_left -= pos_available

                close_req = copy(req)
                close_req.offset = Offset.CLOSE
                close_req.volume = close_volume
                reqs.append(close_req)

            if volume_left > 0:
                open_volume = volume_left

                open_req = copy(req)
                open_req.offset = Offset.OPEN
                open_req.volume = open_volume
                reqs.append(open_req)

            return reqs
