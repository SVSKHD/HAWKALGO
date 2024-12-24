def calculate_and_calibrate(symbol, start_price, current_price):
    pip_value = symbol['pip_value']
    formatted_pips = (start_price - current_price) / pip_value
    thresholds = (start_price - current_price) / (symbol['threshold'] * pip_value)  # Adjusted threshold calculation
    direction = "neutral"
    if formatted_pips > symbol['threshold']:
        direction = "down"
    elif formatted_pips < -symbol['threshold']:
        direction = "up"
    return formatted_pips, round(thresholds, 2), direction


def assemble_logic(symbol, start_price, current_price):
    formatted_pips, thresholds, direction = calculate_and_calibrate(symbol, start_price, current_price)
    print(f"Debug: formatted_pips={formatted_pips}, thresholds={thresholds}, direction={direction}")
    messages = []
    if thresholds >= 1.0 and thresholds <= 70.0:  # Adjusted range for larger thresholds
        messages.append(f"Sell at {current_price}")
    elif thresholds >= 70.0 and thresholds <= 100.0:
        messages.append(f"Close sell trades at {current_price}")
    elif thresholds <= -1.0 and thresholds >= -1.2:
        messages.append(f"Buy at {current_price}")
    elif thresholds <= -3.33 and thresholds > -5.0:  # Refined upward threshold range
        messages.append(f"Close sell trades at {current_price}")
    for msg in messages:
        print(msg)
    return messages






eur = {
    'symbol': 'EURUSD',
    'pip_value': 0.0001,
    'threshold': 15,  # Using the threshold here
    'lot': 5.0
}

eurp = [1.1015, 1.10000, 1.10075, 1.1050, 1.1025]
eurn = [0.9985, 0.9970, 0.99925 ,0.9960, 0.9950, 0.9940]
for price in eurp:
    data = assemble_logic(eur, 1.10000, price)
    print("data", data)
