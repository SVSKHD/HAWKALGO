from config import symbols_list
from fetch import fetch_price
from logic import process_single_price
from datetime import datetime
import time
from db import get_symbol_data

hedging = {}
last_actions = {}

def execute_trading(symbol):
    """Executes trading logic based on the symbol data."""
    symbol_name = symbol['symbol']
    symbol_data = get_symbol_data(symbol_name)
    print("symbol_data:", symbol_data)

def main():
    while True:
        current_time = datetime.now()  # Get the current time
        if 0 <= current_time.hour <= 12:  # Check if the current time is between 0:00 and 12:00
            for symbol in symbols_list:
                symbol_name = symbol['symbol']

                if symbol_name not in hedging:
                    hedging[symbol_name] = {'positive_hedging': False, 'negative_hedging': False}
                if symbol_name not in last_actions:
                    last_actions[symbol_name] = None

                # Fetch prices
                start_price = fetch_price(symbol, "start")
                current_price = fetch_price(symbol, "current")

                process_single_price(symbol, start_price, current_price, hedging[symbol_name], last_actions[symbol_name])
                execute_trading(symbol)

            time.sleep(1)
        else:
            print(f"Outside trading hours. Current time: {current_time}")
            time.sleep(60)

if __name__ == '__main__':
    main()
