import faust
from models.model import Model


class Depth(faust.Record, serializer='json'):
    Id: str
    feature_id: str
    exchange: str
    symbol: str
    quote_asset: str
    base_asset: str
    levels: int
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