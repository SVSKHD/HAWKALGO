from db import get_symbol_data, save_symbol_data, clear_all_keys, update_symbol_data, save_or_update_symbol_data


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
        'pip_difference': round(formatted_pip_difference, 2),
        'threshold_no': round(formatted_pip_difference / symbol['threshold'], 2),
        'direction': direction
    }
    return data


def process_single_price(symbol, start_price, current_price, hedging, last_action=None):
    result = calculate_pip_difference(symbol, start_price, current_price)
    symbol_name = symbol['symbol']

    # Placeholder for fetching stored data
    symbol_stored_data = {}  # Replace with DB logic if needed

    # Merge stored data with current result
    if symbol_stored_data:
        result = {**symbol_stored_data, **result}

    print("Stored Data:", symbol_stored_data)

    # Handle down direction logic (negative prices decreasing further)
    if result['direction'] == 'down':
        if result['threshold_no'] > 1 and last_action != "sell":
            print(f"Sell at {current_price}")
            last_action = "sell"
            result['first_negative_threshold'] = True
            result['first_negative_threshold_price'] = current_price
        elif result['threshold_no'] >= 2 and last_action == "sell":
            print(f"Close sell trades {current_price}")
            result['second_negative_threshold'] = True
            result['second_negative_threshold_price'] = current_price
            last_action = "close sell"
        elif 0.5 >= result['threshold_no'] >= 0.45 and not hedging.get('negative_hedging', False):
            print(f"Hedging initiated at {current_price}")
            hedging['negative_hedging'] = True
            result['negative_hedging'] = True
            result['negative_hedging_price'] = current_price

    # Handle up direction logic (negative prices increasing towards neutral)
    if result['direction'] == 'up':
        if result['threshold_no'] < -1 and last_action != "buy":
            print(f"Buy at {current_price}")
            last_action = "buy"
            result['first_positive_threshold'] = True
            result['first_positive_threshold_price'] = current_price
        elif result['threshold_no'] <= -2 and last_action == "buy":
            print(f"Close buy trades {current_price}")
            result['second_positive_threshold'] = True
            result['second_positive_threshold_price'] = current_price
            last_action = "close buy trades"
        elif -0.5 <= result['threshold_no'] <= -0.45 and not hedging.get('positive_hedging', False):
            print(f"Hedging initiated at {current_price}")
            hedging['positive_hedging'] = True
            result['positive_hedging'] = True
            result['positive_hedging_price'] = current_price

    # Handle hedging close logic
    if hedging.get('positive_hedging', False) and result['direction'] == 'up' and result['threshold_no'] <= -0.8:
        print(f"Hedging closed at {current_price} for positive hedging")
        result = reset_hedging_state(result)  # Use returned reset result
        hedging['positive_hedging'] = False
        result['positive_hedging_trades_close'] = True
        result['positive_hedging_trades_close_price'] = current_price

    if hedging.get('negative_hedging', False) and result['direction'] == 'down' and result['threshold_no'] >= 0.8:
        print(f"Hedging closed at {current_price} for negative hedging")
        result = reset_hedging_state(result)  # Use returned reset result
        hedging['negative_hedging'] = False
        result['negative_hedging_trades_close'] = True
        result['negative_hedging_trades_close_price'] = current_price

    print("Result:", result)
    save_or_update_symbol_data(symbol_name, result)
    # Placeholder for saving the result (DB or in-memory storage)
    # save_or_update_symbol_data(symbol_name, result)  # Replace with actual DB operation

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


# Data
eur = {
    'symbol': 'EURUSD',
    'pip_value': 0.0001,
    'threshold': 15
}

eur_negative_hedging = [
    1.0000,
    0.9985,
    0.9970,
    0.9969,
    0.99925,
    0.9995,
    0.99975,# hedging
    1.0000,
    1.0005,
    1.00075,
    1.0009,
    1.0010,
    1.0015  # hedging finished.
]

pur_positive_hedging = [
    1.0000,
    1.0015,
    1.0030,
    1.0045,
    1.0060,
    1.0007,  # hedging
    1.0005,
    1.0003,
    1.0001,
    0.9999,
    0.9997,
    0.9995,
    0.9993,
    0.9991,
    0.9989,
    0.9987,  # hedging finished.
]

start_price = 1.0000
hedging = {'hedging': False, 'positive_hedging': False, 'negative_hedging': False}
last_action = None

# Process each price individually (manual calls)
for price in pur_positive_hedging:
    hedging, last_action = process_single_price(eur, start_price, price, hedging, last_action)


# clear_all_keys()