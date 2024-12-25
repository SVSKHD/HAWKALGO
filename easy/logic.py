def calculate_and_calibrate(symbol, start_price, current_price):
    pip_value = symbol['pip_value']
    formatted_pips = (start_price - current_price) / pip_value
    raw_thresholds = (start_price - current_price) / (symbol['threshold'] * pip_value)

    # Enforce correct thresholds based on direction
    if current_price > start_price:  # Upward price movement (buying scenario)
        raw_thresholds = -abs(raw_thresholds)  # Make thresholds negative for upward movement
        direction = "up"
    else:  # Downward price movement (selling scenario)
        raw_thresholds = abs(raw_thresholds)  # Keep thresholds positive for downward movement
        direction = "down"

    # Normalize thresholds to integers
    if abs(raw_thresholds) >= 2.0:  # For 2nd threshold or beyond
        normalized_threshold = 2 if raw_thresholds > 0 else -2
    elif 1.0 <= abs(raw_thresholds) < 2.0:  # For 1st threshold
        normalized_threshold = 1 if raw_thresholds > 0 else -1
    else:
        normalized_threshold = None  # Outside defined thresholds

    return formatted_pips, normalized_threshold, direction


def assemble_logic(symbol, start_price, current_price):
    formatted_pips, threshold_no, direction = calculate_and_calibrate(symbol, start_price, current_price)
    print(f"Debug: formatted_pips={formatted_pips}, threshold_no={threshold_no}, direction={direction}")
    messages = []

    # Handle trade actions based on normalized thresholds
    if threshold_no == 1:
        messages.append(f"Place sell trades at {current_price} (1st threshold: {threshold_no})")
    elif threshold_no == 2:
        messages.append(f"Close sell trades at {current_price} (2nd threshold: {threshold_no})")
    elif threshold_no == -1:
        messages.append(f"Place buy trades at {current_price} (1st threshold: {threshold_no})")
    elif threshold_no == -2:
        messages.append(f"Close buy trades at {current_price} (2nd threshold: {threshold_no})")
    else:
        messages.append(f"No action at {current_price} (outside thresholds)")

    for msg in messages:
        print(msg)
    return messages


# Variables
eur = {
    'symbol': 'EURUSD',
    'pip_value': 0.0001,
    'threshold': 15,  # Using the threshold here
    'lot': 5.0
}

eurp = [1.1015, 1.10000, 1.10075, 1.1050, 1.1025]  # Positive thresholds for selling
eurn = [0.9985, 0.9970, 0.99925, 0.9955]  # Negative thresholds for buying

# Execute updated logic

# Test for sell prices (positive thresholds)
print("\n--- Testing Sell Prices (Positive Thresholds) ---")
sell_results = []
for price in eurp:
    result = assemble_logic(eur, 1.10000, price)
    sell_results.append(result)

# Test for buy prices (negative thresholds)
print("\n--- Testing Buy Prices (Negative Thresholds) ---")
buy_results = []
for price in eurn:
    result = assemble_logic(eur, 1.0000, price)
    buy_results.append(result)

sell_results, buy_results