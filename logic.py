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


def check_hedging(data, threshold):
    positive_hedging = False
    negative_hedging = False
    if threshold < 0.5:
        negative_hedging = True
    elif threshold > -0.5:
        positive_hedging: True

    data['positive_hedging'] = positive_hedging
    data['negative_hedging'] = negative_hedging
    return data


def combine_logic(symbol, start_price, current_price):
    pip_data = calculate_pip_difference(symbol, start_price, current_price)
    trades_placed = False
    if trades_placed and pip_data['threshold_no'] < 0.5:
        print("positive_hedging")
    elif trades_placed and pip_data['threshold_no'] > -0.5:
        print("negative_hedging")
    return pip_data


prices = [
    1.0030,
    1.0020,
    1.0010,
    1.0000,
]

positive_prices = [
    1.0030,
    1.0045,
    1.0060,
    1.0075,
]

hedging_prices = [
    1.0030,
    1.0045,
    1.0037,
    1.0030,
    1.0020,
    1.0016
]
eur = {
    'symbol': 'EURUSD',
    'pip_value': 0.0001,
    'threshold': 15
}

# for price in prices:
#     result = check_hedging_and_thresholds(eur, 1.0030, price)
#     print(result)
#
# print("==positive==")
#
# for price in positive_prices:
#     result = check_hedging_and_thresholds(eur, 1.0030, price)
#     print(result)

print("==hedging==")

for price in hedging_prices:
    result = combine_logic(eur, 1.0030, price)
    print(result)
