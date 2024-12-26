from trade_place import trade_place, close_trades_by_symbol
from utils import get_open_positions_count
import asyncio
# Define global dictionary to store hedging information for multiple symbols, including positive and negative hedges
hedging_states = {}

# TO-DO
# get open positions for a symbol and hedge don't hedge.
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
        'pip_difference': round(pip_difference,2),
        'format_pips': round(format_pips,2),
        'threshold_no': threshold_no,
        'direction': direction,
    }


async def assemble_logic(symbol, start_price, current_price):
    global hedging_states
    symbol_name = symbol['symbol']

    # Initialize hedging state for the symbol if not already present
    if symbol_name not in hedging_states:
        print(f"Initializing hedging state for {symbol_name}")
        hedging_states[symbol_name] = {
            'positive_hedge': False,
            'negative_hedge': False,
            'hedge_direction': None,
            'hedge_price': None,
        }

    # Fetch the number of open positions for the symbol
    print(f"Fetching open positions for {symbol_name}")
    # Fetch the number of open positions for the symbol
    print(f"Fetching open positions for {symbol_name}")
    positions = await asyncio.to_thread(get_open_positions_count, symbol)
    if positions is None:
        print(f"No open positions found for {symbol_name}")
        positions = 0  # Handle case where positions are None
    else:
        print(f"Open positions for {symbol_name}: {positions}")

    # Calculate thresholds and direction
    print(f"Calculating thresholds and direction for {symbol_name}")
    data = calculate_everything(symbol, start_price, current_price)
    threshold_no = data['threshold_no']
    direction = data['direction']
    messages = []

    # Debugging current state
    print(f"Debug: {symbol_name}, Threshold No: {threshold_no}, Direction: {direction}, Positions: {positions}")

    # Handle profit hedging close logic
    if hedging_states[symbol_name]['negative_hedge']:
        print(f"Checking negative hedge close logic for {symbol_name}")
        if direction == 'Down' and threshold_no <= 0.87:
            print(f"Profit hedging closed for {symbol_name}")
            await close_trades_by_symbol(symbol)
            hedging_states[symbol_name]['negative_hedge'] = False
            messages.append(f"Close all negative hedge trades for {symbol_name}")

    # Handle positive hedge close logic
    if hedging_states[symbol_name]['positive_hedge']:
        print(f"Checking positive hedge close logic for {symbol_name}")
        if direction == 'Up' and threshold_no >= -0.87:
            print(f"Profit positive hedging closed for {symbol_name}")
            await close_trades_by_symbol(symbol)
            hedging_states[symbol_name]['positive_hedge'] = False
            messages.append(f"Close all positive hedge trades for {symbol_name}")

    # Handle trade actions based on normalized thresholds
    print(f"Evaluating trade actions for {symbol_name}")
    if threshold_no == 1:
        print(f"Placing sell trade for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        await trade_place(symbol, "sell", symbol['lot'], hedge=False)
        messages.append(f"Place sell trades at {current_price} (1st threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == 2:
        print(f"Closing sell trades for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        await close_trades_by_symbol(symbol)
        messages.append(f"Close sell trades at {current_price} (2nd threshold: {threshold_no}, direction: {direction})")
    elif 0.05 <= threshold_no <= 0.67 and positions == 2:  # Expanded positive hedge range
        print(f"Placing positive hedge for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        hedging_states[symbol_name]['positive_hedge'] = True
        hedging_states[symbol_name]['hedge_direction'] = 'sell'
        hedging_states[symbol_name]['hedge_price'] = current_price
        await trade_place(symbol, "sell", symbol['lot'], hedge=True)
        messages.append(
            f"Positive Hedge: Place sell trades at {current_price} (Hedge threshold: {threshold_no}, direction: {direction})")
    elif -0.5 <= threshold_no <= -0.4 and positions == 2:
        print(f"Placing negative hedge for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        hedging_states[symbol_name]['negative_hedge'] = True
        hedging_states[symbol_name]['hedge_direction'] = 'buy'
        hedging_states[symbol_name]['hedge_price'] = current_price
        await trade_place(symbol, "buy", symbol['lot'], hedge=True)
        messages.append(
            f"Negative Hedge: Place buy trades at {current_price} (Hedge threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == -1:
        print(f"Placing buy trade for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        await trade_place(symbol, "buy", symbol['lot'], hedge=False)
        messages.append(f"Place buy trades at {current_price} (1st threshold: {threshold_no}, direction: {direction})")
    elif threshold_no == -2:
        print(f"Closing buy trades for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        await close_trades_by_symbol(symbol)
        messages.append(f"Close buy trades at {current_price} (2nd threshold: {threshold_no}, direction: {direction})")
    else:
        print(f"No action for {symbol_name} at {current_price} (threshold_no: {threshold_no})")
        messages.append(f"No action at {current_price} (outside thresholds)")

    return data, messages





# # Test cases for multiple symbols
# symbols = [
#     {'symbol': 'EURUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 5.0},
#     {'symbol': 'GBPUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 3.0},
# ]

# Define test prices for each symbol
# test_prices1 = {
#     'EURUSD': [1.1015, 1.10000, 1.10075, 1.0050, 1.1000, 1.0995, 1.0990],
#     'GBPUSD': [1.3015, 1.30000, 1.30075],
# }
# test_prices2={
#     'EURUSD': [1.1000, 1.0985, 1.099925, 1.10025, 1.1005, 1.1010, 1.1015],
#     'GBPUSD': [1.3000, 1.2985, 1.299925, 1.30025, 1.3005, 1.3010, 1.3015],
# }
# # test_prices = {
# #     'EURUSD': [1.1015, 1.10000, 1.10075, 1.10050, 1.1010, 1.1000, 1.0995, 1.0990, 1.0985, 1.0980, 1.0975],
# #     'GBPUSD': [1.3015, 1.30000, 1.30075, 1.3050, 1.3025],
# # }
#
# start_prices = {
#     'EURUSD': 1.1000,
#     'GBPUSD': 1.3000,
# }
#
# # Run tests for multiple symbols
# for symbol in symbols:
#     print(f"\n--- Testing {symbol['symbol']} ---")
#     for price in test_prices2[symbol['symbol']]:
#         result, messages = assemble_logic(symbol, start_prices[symbol['symbol']], price)
#         print(result)
#         print(messages)
#
# # Display hedging states for all symbols
# print("\n--- Hedging States ---")
# for symbol_name, state in hedging_states.items():
#     print(f"{symbol_name}: {state}")
#     print(50 * '=')
