import numpy as np
from trade_place import place_order, close_trades_by_symbol

def calculate_pip_difference(symbol, start_price, current_price):
    pip_difference = start_price - current_price
    formatted_pip_difference = pip_difference / symbol['pip_value']
    direction = "neutral"
    if formatted_pip_difference > 0:
        direction = "down"
    elif formatted_pip_difference < 0:
        direction = "up"
    data = {
        'symbol': symbol['symbol'],
        'pip_difference': float(np.float64(round(formatted_pip_difference, 2))),
        'threshold_no': float(np.float64(round(formatted_pip_difference / symbol['threshold'], 2))),
        'direction': direction
    }
    return data



async def process_single_price(symbol, start_price, current_price, hedging, last_action=None):
    result = calculate_pip_difference(symbol, start_price, current_price)
    symbol_name = symbol['symbol']
    lot_size = symbol['lot']

    # Ensure all these keys exist, even if they are not triggered
    always_present_keys = {
       'first_positive_threshold': False,
       'first_positive_threshold_price': None,
       'second_positive_threshold': False,
       'second_positive_threshold_price': None,
       'first_negative_threshold': False,
       'first_negative_threshold_price': None,
       'second_negative_threshold': False,
       'second_negative_threshold_price': None,
       'positive_hedging': False,
       'positive_hedging_price': None,
       'negative_hedging': False,
       'negative_hedging_price': None,
       'positive_hedging_trades_close': False,
       'positive_hedging_trades_close_price': None,
       'negative_hedging_trades_close': False,
       'negative_hedging_trades_close_price': None
    }

    # Merge defaults with the actual result
    for k, v in always_present_keys.items():
        result.setdefault(k, v)

    # Handle down direction logic (negative prices decreasing further)
    if result['direction'] == 'down':
        if 1.0 <= result['threshold_no'] <= 1.2 and last_action != "sell":
            print(f"Sell at {current_price}")
            await place_order(symbol, 'sell', lot_size, hedge=False)
            last_action = "sell"
            result['first_negative_threshold'] = True
            result['first_negative_threshold_price'] = current_price
        elif 2.0 <= result['threshold_no'] <= 2.2 and last_action == "sell":
            print(f"Close sell trades at {current_price}")
            await close_trades_by_symbol(symbol)
            result['second_negative_threshold'] = True
            result['second_negative_threshold_price'] = current_price
            last_action = "close sell"
        elif 0.4 <= result['threshold_no'] <= 0.5 and not hedging.get('negative_hedging', False):
            print(f"Hedging initiated at {current_price}")
            await place_order(symbol, 'buy', lot_size, hedge=True)
            hedging['negative_hedging'] = True
            result['negative_hedging'] = True
            result['negative_hedging_price'] = current_price

    # Handle up direction logic (negative prices increasing towards neutral)
    if result['direction'] == 'up':
        if -1.2 <= result['threshold_no'] <= -1.0 and last_action != "buy":
            print(f"Buy at {current_price}")
            await place_order(symbol, 'buy', lot_size, hedge=False)
            last_action = "buy"
            result['first_positive_threshold'] = True
            result['first_positive_threshold_price'] = current_price
        elif -2.2 <= result['threshold_no'] <= -2.0 and last_action == "buy":
            print(f"Close buy trades at {current_price}")
            await close_trades_by_symbol(symbol)
            result['second_positive_threshold'] = True
            result['second_positive_threshold_price'] = current_price
            last_action = "close buy trades"
        elif -0.5 <= result['threshold_no'] <= -0.4 and not hedging.get('positive_hedging', False):
            print(f"Hedging initiated at {current_price}")
            await place_order(symbol, 'sell', lot_size, hedge=True)
            hedging['positive_hedging'] = True
            result['positive_hedging'] = True
            result['positive_hedging_price'] = current_price

    # Handle hedging close logic
    if hedging.get('positive_hedging', False) and result['direction'] == 'up' and result['threshold_no'] <= -0.8:
        print(f"Hedging closed at {current_price} for positive hedging")
        await close_trades_by_symbol(symbol)
        result = reset_hedging_state(result)  # Use returned reset result
        hedging['positive_hedging'] = False
        result['positive_hedging_trades_close'] = True
        result['positive_hedging_trades_close_price'] = current_price

    if hedging.get('negative_hedging', False) and result['direction'] == 'down' and result['threshold_no'] >= 0.8:
        print(f"Hedging closed at {current_price} for negative hedging")
        await close_trades_by_symbol(symbol)
        result = reset_hedging_state(result)  # Use returned reset result
        hedging['negative_hedging'] = False
        result['negative_hedging_trades_close'] = True
        result['negative_hedging_trades_close_price'] = current_price

    # Update hedging state and last action
    return hedging, last_action


def reset_hedging_state(result):
    print("Resetting hedging state:", result)  # Log before resetting
    reset_result = result.copy()  # Create a copy of the original result

    fields_to_reset = [
        'first_positive_threshold', 'second_positive_threshold',
        'first_positive_threshold_price', 'second_positive_threshold_price',
        'first_negative_threshold', 'second_negative_threshold',
        'first_negative_threshold_price', 'second_negative_threshold_price',
        'positive_hedging', 'positive_hedging_price',
        'negative_hedging', 'negative_hedging_price',
        'positive_hedging_trades_close', 'positive_hedging_trades_close_price',
        'negative_hedging_trades_close', 'negative_hedging_trades_close_price',
    ]
    for field in fields_to_reset:
        if field.endswith('_price'):
            reset_result[field] = None  # Reset price fields to None
        else:
            reset_result[field] = False  # Reset boolean fields to False

    print("After resetting:", reset_result)  # Log after resetting
    return reset_result

