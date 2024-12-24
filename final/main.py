from config import symbols_list
from fetch import fetch_price
from logic import process_single_price
from datetime import datetime
import time
from db import get_symbol_data, clear_all_keys

hedging = {}
last_actions = {}

def execute_trading(data):
    """Executes trading logic based on the symbol data."""
    symbol_name = data['symbol']
    symbol_data = get_symbol_data(symbol_name)
    threshold_no = symbol_data['threshold_no']
    direction = symbol_data['direction']
    first_positive_threshold = symbol_data['first_positive_threshold']
    first_positive_threshold_price = symbol_data['first_positive_threshold_price']
    second_positive_threshold = symbol_data['second_positive_threshold']
    second_positive_threshold_price = symbol_data['second_positive_threshold_price']

    first_negative_threshold = symbol_data['first_negative_threshold']
    first_negative_threshold_price = symbol_data['first_negative_threshold_price']
    second_negative_threshold_price = symbol_data['second_positive_threshold_price']
    second_negative_threshold = symbol_data['second_negative_threshold']

    # hedging variables
    positive_hedging = symbol_data['positive_hedging']
    negative_hedging = symbol_data['negative_hedging']
    positive_hedging_trades_close = symbol_data['positive_hedging_trades_close']
    negative_hedging_trades_close = symbol_data['negative_hedging_trades_close']


    print("symbol_data:", symbol_data)
    if not symbol_data:
        print(f"No data found for symbol: {symbol_name}")
        return
    #up direction handling
    if first_positive_threshold and -1 >= threshold_no > -1.2:
        print(f"buy {first_positive_threshold_price}")
    if second_positive_threshold and -2 <= threshold_no <= -1.9:
        print(f"close the positive trades for {symbol_name} at {second_positive_threshold_price}")
    #down direction handling
    if first_negative_threshold and 1 < threshold_no <=1.2:
        print(f"sell at {first_negative_threshold_price}")
    if second_negative_threshold and threshold_no >= 2:
        print(f"close all the negative trades for {symbol_name} at {second_negative_threshold_price}")

    # add hedging case here.

    if positive_hedging:
        print(f"positive hedging started {symbol_name}")
    if positive_hedging_trades_close:
        print(f"positive hedging trades close {symbol_name}")


    if negative_hedging:
        print(f"negative hedging started {symbol_name}")
    if negative_hedging_trades_close:
        print(f"negative hedging trades close {symbol_name}")


def main():
    while True:

        current_time = datetime.now()  # Get the current time
        if 0 <= current_time.hour <= 18:  # Check if the current time is between 0:00 and 12:00
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
                processed_data = get_symbol_data(symbol_name)
                if processed_data:
                    execute_trading(symbol)

            time.sleep(1)
        else:
            if 13 <= current_time.hour <= 23:
                clear_all_keys()
            print(f"Outside trading hours. Current time: {current_time}")
            time.sleep(60)

if __name__ == '__main__':
    main()



