from config import symbols_list
from fetch import fetch_price
from logic import assemble_logic
from datetime import datetime
from utils import connect_mt5
import asyncio


async def process_symbol(symbol):
    """
    Process a single symbol: fetch start/current prices and execute trading logic.
    """
    try:
        print(f"Processing symbol: {symbol['symbol']}")
        # Fetch start and current prices
        start_price = fetch_price(symbol, "start")
        current_price = fetch_price(symbol, "current")

        if start_price is None or current_price is None:
            print(f"Skipping symbol {symbol['symbol']} due to missing price data.")
            return

        # Execute logic
        await assemble_logic(symbol, start_price, current_price)

    except Exception as e:
        print(f"Error processing symbol {symbol['symbol']}: {e}")


async def main():
    # Connect to MetaTrader 5
    connected = await connect_mt5()
    if not connected:
        print("Failed to connect to MetaTrader 5.")
        return

    while True:  # Infinite loop for continuous checks
        today = datetime.now()

        # Check if trading is allowed (between 0 and 21 hours)
        if 0 <= today.hour <= 21:
            print(f"Trading session active at {today.strftime('%Y-%m-%d %H:%M:%S')}.")

            # Process all symbols concurrently
            await asyncio.gather(*[process_symbol(symbol) for symbol in symbols_list])
        else:
            print(f"Trades are not allowed outside active hours. Time: {today.strftime('%Y-%m-%d %H:%M:%S')}")

        # Wait for 1 second before the next check
        await asyncio.sleep(1)


# Run the main function
asyncio.run(main())
