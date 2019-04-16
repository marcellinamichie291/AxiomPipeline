from binance.client import Client
from binance.websockets import BinanceSocketManager
import copy
import rethinkdb as r

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

import constants.fields as fields
import constants.db as db_const
from ingress.core import Ingress 

class DepthIngress(Ingress):
    def __init__(
        self,
        quote_asset='BTC',
        levels=20,
        interval='1m'
    ):
        Ingress.__init__(
            self
        )

        self.client = Client("", "")
        self.bm = BinanceSocketManager(self.client)

        self.quote_asset = quote_asset
        self.depth_ws_suffix = "@depth"+str(levels)

    def _maintain(self):
        prev_depth_ws_list = copy.copy(self.depth_ws_list)
        self.set_conf()
        if set(prev_depth_ws_list) != set(self.depth_ws_list):
            self.reset()
        print("Maintainance complete")

    def _setup(self):
        self.set_conf()
        self.depth_key = self.bm.start_multiplex_socket(
            self.depth_ws_list,
            self.process_depth_flat
        )

    def _stop(self):
        self.bm.stop_socket(self.depth_key)

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
                self.depth_ws_list = [y.lower()+self.depth_ws_suffix for y in linfo]
                return True
                
        except Exception as e:
            print(e)
            return False

    def process_depth(self, msg):
        try:
            symbol = msg['stream'].replace(self.depth_ws_suffix, '').upper()
            bids, asks = self.derive_depth(msg['data'])
            self.ASKS[symbol] = asks
            self.BIDS[symbol] = bids
        except Exception as e:
            print(e)

    def process_depth_flat(self, msg):
        try:
            symbol = msg['stream'].replace(self.depth_ws_suffix, '').upper()
            flat_depth = self.derive_flat_depth(msg['data'])
            self.publish(
                key=k['s'],
                value=flat_depth
            )
        except Exception as e:
            print(e)
    
    def derive_base_asset(self, quote_asset, symbol):
        return symbol.replace(quote_asset, '')

    def check_quote_asset(self, quote_asset, symbol):
        return symbol.endswith(quote_asset);

    def derive_flat_depth(self, data):
        flat_depth = {}
        bids = [{'bid_price_'+str(i):float(d[0]), 'bid_quantity_'+str(i):(float(d[1])*float(d[0]))} for (i, d) in enumerate(data['bids'])]
        asks = [{'ask_price_'+str(i):float(d[0]), 'ask_quantity_'+str(i):(float(d[1])*float(d[0]))} for (i, d) in enumerate(data['asks'])]
        for bid, ask in zip(bids, asks):
            flat_depth.update(bid)
            flat_depth.update(ask)
        return flat_depth
