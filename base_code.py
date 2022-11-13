import pandas as pd
import numpy as np
import requests
from time import sleep
import signal

class ApiException(Exception):
    pass

def signal_handler(signum, frame):
    global shutdown
    signal.signal(signum.SIGINT, signal.SIG_DFL)
    shutdown = True

API_KEY = {'KEY': '$$$$$'}
shutdown = False

#Helper functions
# Returns current 'tick' of the running case
def get_tick(session):
    resp = session.get("http://localhost:9999/v1/case")
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('Authorization error. Check if API key is correct')

# Returns the bid price and the ask price for a given security
def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:9999/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('Authorization error. Check if API key is correct')

# Where the algorithm is executed
def main():
    with requests.Session() as s:
        s.headers.update(API_KEY)
        tick = get_tick(s)
        while tick > 5 and tick < 295 and not shutdown:
            crzy_m_bid, crzy_m_ask = ticker_bid_ask(s, 'CRZY_M')
            crzy_a_bid, crzy_a_ask = ticker_bid_ask(s, 'CRZY_A')

            if crzy_m_bid > crzy_a_ask:
                s.post('http://localhost:9999/v1/orders',
                       params={'ticker': 'CRZY_A','Type': 'MARKET', 'quantity': 1000, 'action': 'BUY'})
                s.post('http://localhost:9999/v1/orders',
                       params={'ticker': 'CRZY_M', 'Type': 'MARKET', 'quantity': 1000, 'action': 'SELL'})
                sleep(1)

            if crzy_a_bid > crzy_m_ask:
                s.post('http://localhost:9999/v1/orders',
                       params={'ticker': 'CRZY_M', 'Type': 'MARKET', 'quantity': 1000, 'action': 'BUY'})
                s.post('http://localhost:9999/v1/orders',
                       params={'ticker': 'CRZY_A', 'Type': 'MARKET', 'quantity': 1000, 'action': 'SELL'})
                sleep(1)

                #Updates ticks at the end of loop in order to enusre that the algorithm should still run
                tick = get_tick(s)

if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal_handler)
    main()