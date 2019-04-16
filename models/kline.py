import faust
from models.model import Model

class Kline(faust.Record, serializer='json'):
    Id: str = None
    feature_id: str = None
    exchange: str = None
    event_time: int = None
    start_time: int = None
    end_time: int = None
    symbol: str = None
    base_asset: str = None
    quote_asset: str = None
    interval: str = None
    o: float = None
    h: float = None
    l: float = None
    c: float = None
    volume: float = None
    trades: int = None
    quote_asset_volume: float = None
    taker_buy_base_asset_volume: float = None
    taker_buy_quote_asset_volume: float = None
    is_final: bool = None
    event_time_ms: int = None
