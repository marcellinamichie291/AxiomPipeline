from binance.client import Client
from binance.websockets import BinanceSocketManager
import copy
import rethinkdb as r
from datetime import datetime

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import constants.fields as fields
from ingress import Ingress 
from models.kline import Kline

class KlinesIngress(Ingress):
    def __init__(
        self,
        quote_asset='BTC',
        levels=20,
        interval='1m',
        topic="binance_klines",
        url="localhost:9092"
    ):
        Ingress.__init__(
            self,
            topic=topic,
            url=url
        )

        self.client = Client("", "")
        self.bm = BinanceSocketManager(self.client)

        self.quote_asset = quote_asset
        self.kline_ws_suffix = "@kline_"+str(interval)

    def _maintain(self):
        prev_kline_ws_list = copy.copy(self.kline_ws_list)
        self.set_conf()
        if set(prev_kline_ws_list) != set(self.kline_ws_list):
            self.reset()
        print("Maintainance complete")

    def _setup(self):
        self.set_conf()
        self.kline_key = self.bm.start_multiplex_socket(
            self.kline_ws_list,
            self.process_kline
        )

    def _stop(self):
        self.bm.stop_socket(self.kline_key)

    def _start(self):
        print("Starting "+ self.quote_asset)
        self.bm.start()

    # Local
    # =====================================================================>

    def set_conf(self):
        try:
            info = self.client.get_exchange_info()
            linfo = [x['symbol'] for x in info['symbols'] if self.check_quote_asset(self.quote_asset,x['symbol'])]
            if len(linfo) > 5:
                self.kline_ws_list = [y.lower()+self.kline_ws_suffix for y in linfo]
                return True
                
        except Exception as e:
            print(e)
            return False
    
    def derive_base_asset(self, quote_asset, symbol):
        return symbol.replace(quote_asset, '')

    def check_quote_asset(self, quote_asset, symbol):
        return symbol.endswith(quote_asset);

    def process_kline(self, msg):
        d = msg['data']
        k = d['k']
        try:
            # TODO check depth not empty
            base_asset = self.derive_base_asset(self.quote_asset,k['s'])            
            exchange = 'binance'
            kline = Kline(
                Id= [exchange, 'kline', d['s'], d['E']],
                partition_id= '_'.join([exchange, base_asset, self.quote_asset]),
                exchange=exchange,                
                event_time=round(d['E']/1000),      
                event_time_ms=d['E'],                
                start_time=k['t'],
                end_time=k['T'],
                symbol=k['s'],
                base_asset=base_asset,
                quote_asset=self.quote_asset,
                interval=k['i'],
                o=float(k['o']),
                c=float(k['c']),
                h=float(k['h']),
                l=float(k['l']),
                volume=float(k['v']),
                trades=int(k['n']),
                quote_asset_volume=float(k['q']),
                taker_buy_base_asset_volume=float(k['V']),
                taker_buy_quote_asset_volume=float(k['Q']),
                is_final=k['x']
            );

            self.publish(
                key=k['s'],
                value=vars(kline)
            )


        except Exception as e:
            print(e)


if __name__ == "__main__":
    worker = KlinesIngress(
        quote_asset="BTC",
        url="localhost:9092"
    )
    worker.run()