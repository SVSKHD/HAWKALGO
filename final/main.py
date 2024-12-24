from config import symbols_list
from fetch import fetch_price
from logic import process_single_price
from datetime import timezone, datetime, timedelta
from db import get_symbol_data
hedging = {}
last_actions = {}


def execute_trading(symbol):
    symbol_name = symbol['symbol']
    symbol_data = get_symbol_data(symbol_name)
    print("symbol_data", symbol_data)


# def monitor_trading():

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
        process_single_price(symbol, start_price, current_price, hedging[symbol_name], last_actions[symbol_name])
        print("start", start_price, "current", current_price)
        execute_trading(symbol)


if __name__ == '__main__':
    main()