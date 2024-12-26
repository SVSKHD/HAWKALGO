from datetime import timezone, datetime, timedelta
import MetaTrader5 as mt5


def fetch_price(symbol_data, fetch_type):
    # Extract the symbol name
    server_timezone = timezone.utc  # Set to UTC or your broker's timezone
    symbol_name = symbol_data.get('symbol')
    if not symbol_name:
        raise ValueError("Symbol name is missing in symbol_data.")

    # Get the current date and time
    current_date = datetime.now()
    day_of_week = current_date.strftime("%A")

    if fetch_type == 'current':
        # Ensure MT5 initialization
        if not mt5.initialize():
            print("MetaTrader5 initialization failed.")
            return None

        # Fetch current price for the symbol
        tick = mt5.symbol_info_tick(symbol_name)
        if tick:
            current_price = tick.bid
            return current_price
        else:
            print(f"Failed to fetch current price for {symbol_name}.")
            return None

    elif fetch_type == 'start':
        # Determine target timestamp
        if day_of_week in ['Sunday', 'Saturday', 'Monday']:
            # Calculate the most recent Friday
            days_since_friday = (current_date.weekday() - 4) % 7
            last_friday = current_date - timedelta(days=days_since_friday)

            # Add specific time to last Friday (23:58:59) in the server timezone
            target_time = datetime(
                last_friday.year, last_friday.month, last_friday.day,
                23, 58, 59, tzinfo=server_timezone
            )
        else:
            # Use the present day's date at 12:00 AM
            target_time = datetime(
                current_date.year, current_date.month, current_date.day,
                23, 30, 0, tzinfo=server_timezone
            )

        while True:
            formatted_date = target_time.strftime("%Y-%m-%d %H:%M:%S")
            target_timestamp = int(target_time.timestamp())

            # Ensure MT5 initialization
            if not mt5.initialize():
                print("MetaTrader5 initialization failed.")
                return None

            # Fetch price data for the target timestamp
            ticks = mt5.copy_ticks_from(symbol_name, target_timestamp, 1, mt5.COPY_TICKS_INFO)
            if ticks is not None and len(ticks) > 0:
                start_price = ticks[0]['bid']  # Accessing the 'bid' field correctly
                print(f"Fetching start price for {symbol_name} at {formatted_date}: {start_price}")
                return start_price
            elif ticks is None or len(ticks) == 0:
                # Adjust target_time to the previous day's 23:50:00
                target_time -= timedelta(days=1)
                target_time = datetime(
                    target_time.year, target_time.month, target_time.day,
                    23, 59, 59, tzinfo=server_timezone
                )
            else:
                print(f"Failed to fetch start price for {symbol_name}. Ensure sufficient tick data is available.")
                return None

    else:
        print("Invalid fetch type. Use 'current' or 'start'.")
        return None


# Test the function
# eur = {'symbol': 'EURUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 5.0}
#
# start_price = fetch_price(eur, 'start')
# print(f"Start price: {start_price}")


# from datetime import datetime, timedelta, timezone
# import MetaTrader5 as mt5
#
#
# def fetch_price(symbol_data, fetch_type):
#     """
#     Fetch the bid price of a financial instrument (current or start) using the 15-minute timeframe.
#     :param symbol_data: A dictionary with symbol details (e.g., {'symbol': 'EURUSD'}).
#     :param fetch_type: Either 'current' for the latest bid price or 'start' for a historical bid price.
#     :return: The requested bid price or None if unavailable.
#     """
#     symbol = symbol_data.get('symbol')
#     if not symbol:
#         raise ValueError("Symbol name is missing in symbol_data.")
#
#     # Initialize MT5
#     if not mt5.initialize():
#         print("MetaTrader5 initialization failed.")
#         return None
#
#     try:
#         if fetch_type == 'current':
#             # Fetch the latest 15-minute bar
#             current_time = datetime.now(timezone.utc)
#             rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, current_time, 1)
#             if rates is not None and len(rates) > 0:
#                 return rates[-1]['close']  # Assuming 'close' approximates the bid price
#             else:
#                 print(f"Failed to fetch current 15-minute bid price for {symbol}.")
#                 return None
#
#         elif fetch_type == 'start':
#             # Get the current date in UTC
#             current_date = datetime.now(tz=timezone.utc)
#             target_date = current_date
#
#             # Determine the most recent trading session end time
#             if current_date.weekday() == 0:  # Monday
#                 target_date -= timedelta(days=3)  # Go back to Friday
#             elif current_date.weekday() >= 5:  # Saturday or Sunday
#                 target_date -= timedelta(days=(current_date.weekday() - 4))  # Go back to Friday
#             else:
#                 target_date -= timedelta(days=1)  # Previous day
#
#             # Target time is 23:59:59 of the target date
#             target_time = datetime(target_date.year, target_date.month, target_date.day, 23, 59, 59, tzinfo=timezone.utc)
#
#             max_attempts = 10
#             attempts = 0
#
#             # Retry mechanism for holidays/missing data
#             while attempts < max_attempts:
#                 rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, target_time, 1)
#                 if rates is not None and len(rates) > 0:
#                     return rates[-1]['close']  # Assuming 'close' approximates the bid price
#                 else:
#                     # Move one day back
#                     target_time -= timedelta(days=1)
#                     target_time = datetime(
#                         target_time.year, target_time.month, target_time.day, 23, 59, 59, tzinfo=timezone.utc
#                     )
#                     attempts += 1
#
#             print(f"Failed to fetch start bid price for {symbol} after {max_attempts} attempts.")
#             return None
#
#         else:
#             print("Invalid fetch type. Use 'current' or 'start'.")
#             return None
#
#     finally:
#         mt5.shutdown()
#
#
# # Example Usage
# if __name__ == "__main__":
#     eur = {'symbol': 'EURUSD'}
#
#     # Fetch current bid price
#     current_price = fetch_price(eur, 'current')
#     print(f"Current 15-minute bid price for EURUSD: {current_price}")
#
#     # Fetch start bid price
#     start_price = fetch_price(eur, 'start')
#     print(f"Start 15-minute bid price for EURUSD: {start_price}")
