from typing import List, Mapping
import faust
import asyncio
from datetime import timedelta
import json
from binance.client import Client
from binance.websockets import BinanceSocketManager
import pandas as pd

from models.kline import Kline
from models.depth import Depth
from models.feature import Feature

app = faust.App(
    'pipeline', 
    broker='kafka://localhost:9092',
    topic_partitions=8,
)

klines_topic = app.topic('binance_klines', value_type=Kline)
depths_topic = app.topic('binance_depth', value_type=Depth)

kline_table = app.Table(
    'kline_table',
    default=Kline,
).tumbling(
    size=timedelta(seconds=10), 
    expires=timedelta(minutes=90),
    key_index=True
).relative_to_field(Kline.event_time)

# Remove duplicates

@app.agent(klines_topic)
async def process_kline(klines):
    async for kline in klines.group_by(Kline.feature_id):
       kline_table[kline.feature_id] = kline

@app.timer(interval=10.0)
async def process_kline(klines):
    ls = list(kline_table[['binance_ETH_BTC', 'binance_XRP_BTC']].items())

    lmob = [(fid,sid,eid,vars(l)) for ((fid,(sid,eid)),l) in ls]
    print(lmob[0])

    # f = pd.DataFrame.from_records()

    # index_names = ["base_asset", "event_time"]

    # f.set_index(index_names, inplace=True)
    # f.sort_index(inplace=True, ascending=False)
    # f = f[['o','h','l','c','volume', 'trades']]
    # print(f.head(n=100))



    # for l in ls:
    #     print(l)
    #     print(90*"=")

if __name__ == '__main__':
    app.main()
