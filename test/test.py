# Define global dictionary to store hedging information for multiple symbols, including positive and negative hedges
hedging_states = {}


def calculate_everything(symbol, start_price, current_price):
    pip_value = symbol['pip_value']
    pip_difference = start_price - current_price  # Using start_price - current_price
    format_pips = pip_difference / pip_value

    raw_threshold_no = format_pips / symbol['threshold']

    # Ensure threshold_no is never None
    threshold_no = round(raw_threshold_no, 2)

    print("check", 50 * '=')
    print("check", "start_price", start_price, "current_price", current_price, "pip_value", pip_difference,
          "format_pips", format_pips, "raw_threshold_no", raw_threshold_no, "threshold_no", threshold_no)
    print("check", 50 * '=')
    # Determine direction
    if raw_threshold_no > 0:
        direction = "Down"  # Price decreased; for selling logic
    elif raw_threshold_no < 0:
        direction = "Up"  # Price increased; for buying logic
    else:
        direction = "Neutral"

    return {
        'symbol': symbol['symbol'],
        'start_price': start_price,
        'current_price': current_price,
        'pip_value': pip_value,
        'threshold': symbol['threshold'],
        'pip_difference': pip_difference,
        'format_pips': format_pips,
        'threshold_no': threshold_no,
        'direction': direction,
    }


def assemble_logic(symbol, start_price, current_price):
    global hedging_states
    symbol_name = symbol['symbol']

    # Initialize hedging state for the symbol if not already present
    if symbol_name not in hedging_states:
        hedging_states[symbol_name] = {
            'positive_hedge': False,
            'negative_hedge': False,
            'hedge_direction': None,
            'hedge_price': None,
        }

    data = calculate_everything(symbol, start_price, current_price)
    threshold_no = data['threshold_no']
    direction = data['direction']
    messages = []

    # Handle trade actions based on normalized thresholds
    if threshold_no == 1:
        messages.append(f"Place sell trades at {current_price} (1st threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == 2:
        messages.append(f"Close sell trades at {current_price} (2nd threshold: {threshold_no}, direction: {direction})")
    if 0.4 <= threshold_no <= 0.5:
        hedging_states[symbol_name]['positive_hedge'] = True
        hedging_states[symbol_name]['hedge_direction'] = 'sell'
        hedging_states[symbol_name]['hedge_price'] = current_price
        messages.append(
            f"Positive Hedge: Place sell trades at {current_price} (Hedge threshold: {threshold_no}, direction: {direction})")
    elif -0.5 <= threshold_no <= -0.4:
        hedging_states[symbol_name]['negative_hedge'] = True
        hedging_states[symbol_name]['hedge_direction'] = 'buy'
        hedging_states[symbol_name]['hedge_price'] = current_price
        messages.append(
            f"Negative Hedge: Place buy trades at {current_price} (Hedge threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == -1:
        messages.append(f"Place buy trades at {current_price} (1st threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == -2:
        messages.append(f"Close buy trades at {current_price} (2nd threshold: {threshold_no}, direction: {direction})")
    else:
        messages.append(f"No action at {current_price} (outside thresholds)")

    return data, messages


# Test cases for multiple symbols
symbols = [
    {'symbol': 'EURUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 5.0},
    {'symbol': 'GBPUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 3.0},
]

# Define test prices for each symbol
test_prices = {
    'EURUSD': [1.1015, 1.10000, 1.10075, 1.1050, 1.1025],
    'GBPUSD': [1.3015, 1.30000, 1.30075, 1.3050, 1.3025],
}

start_prices = {
    'EURUSD': 1.1000,
    'GBPUSD': 1.3000,
}

# Run tests for multiple symbols
for symbol in symbols:
    print(f"\n--- Testing {symbol['symbol']} ---")
    for price in test_prices[symbol['symbol']]:
        result, messages = assemble_logic(symbol, start_prices[symbol['symbol']], price)
        print(result)
        print(messages)

# Display hedging states for all symbols
print("\n--- Hedging States ---")
for symbol_name, state in hedging_states.items():
    print(f"{symbol_name}: {state}")
    print(50 * '=')