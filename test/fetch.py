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
eur = {'symbol': 'EURUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 5.0}

start_price = fetch_price(eur, 'start')
print(f"Start price: {start_price}")
