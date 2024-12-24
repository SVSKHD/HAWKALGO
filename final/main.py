from config import symbols_list
from fetch import fetch_price
hedging = {}
last_actions = {}


def main():
    for symbol in symbols_list:
        symbol_name = symbol['symbol']

        # Initialize hedging and last_action for the symbol if not already set
        if symbol_name not in hedging:
            hedging[symbol_name] = {'positive_hedging': False, 'negative_hedging': False}
        if symbol_name not in last_actions:
            last_actions[symbol_name] = None

        start_price = fetch_price(symbol, "start")
        current_price = fetch_price(symbol, "current")
        print("start", start_price, "current", current_price)

