def calculate_pip_diff(symbol, start_price, current_price):
    pip_difference = start_price - current_price
    formatted_pip_difference = pip_difference / symbol['pip_value']
    thresholds = formatted_pip_difference / symbol['threshold']
    if formatted_pip_difference > 1:
        direction = 'down'
    elif formatted_pip_difference < -1:
        direction = 'up'
    else:
        direction = 'neutral'

    data = {
        'symbol': symbol['symbol'],
        'pip_difference': formatted_pip_difference,
        'direction': direction,
        'threshold_no': round(thresholds, 2)
    }
    return data


eur = {
    'symbol': 'EURUSD',
    'pip_value': 0.0001,
    'threshold': 15
}

eur_negative_hedging = [
    1.0000,
    0.9985,
    0.99925,
    0.9995,
    0.99975,
    1.0000,
    1.0005,
    1.00075,
    1.0009,
    1.0010,
    1.0015,
    1.0018
]

start_price = 1.0000

hedging = {'hedging': False, 'positive_hedging': False, 'negative_hedging': False}

for price in eur_negative_hedging:
    result = calculate_pip_diff(eur, start_price, price)
    print(result)

    # Handling Down Direction
    if result['direction'] == 'down':
        if result['threshold_no'] > 1:
            print("sell")
        if result['threshold_no'] >= 2:
            print("close sell trades")
        if 0.5 >= result['threshold_no'] >= 0.45:
            print(f"hedging {price}")
            hedging['negative_hedging'] = True

    # Handling Up Direction
    if hedging['negative_hedging'] and result['direction'] == 'up' and result['threshold_no'] <= -0.80:
        print(f"hedging {price} close trades")
        hedging['negative_hedging'] = False

    # Handling Positive Hedging for Up Direction
    if result['direction'] == 'up':
        if result['threshold_no'] < -1:
            print("buy")
        if result['threshold_no'] <= -2:
            print("close buy trades")
        if -0.5 <= result['threshold_no'] <= -0.45:
            print(f"hedging {price}")
            hedging['positive_hedging'] = True

    # Handling Positive Hedging Reset for Down Direction
    if hedging['positive_hedging'] and result['direction'] == 'down' and result['threshold_no'] >= 0.80:
        print(f"hedging {price} close trades")
        hedging['positive_hedging'] = False