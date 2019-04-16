import faust
from models.model import Model

class Feature(faust.Record):
    Id: str
    created_at:int
    window_start:int
    window_end: int
    o: float
    h: float
    l: float
    c: float
    volume: float
    trades: int
    quote_asset_volume: float
    taker_buy_base_asset_volume: float
    taker_buy_quote_asset_volume: float
    bid_price_0: float
    bid_quantity_0: float
    ask_price_0: float
    ask_quantity_0: float
    bid_price_1: float
    bid_quantity_1: float
    ask_price_1: float
    ask_quantity_1: float
    bid_price_2: float
    bid_quantity_2: float
    ask_price_2: float
    ask_quantity_2: float
    bid_price_3: float
    bid_quantity_3: float
    ask_price_3: float
    ask_quantity_3: float
    bid_price_4: float
    bid_quantity_4: float
    ask_price_4: float
    ask_quantity_4: float