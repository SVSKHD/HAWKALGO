from config import symbols_list
from fetch import fetch_price
from logic import assemble_logic
from datetime import datetime
from utils import connect_mt5
import asyncio


async def main():
    # Connect to MetaTrader 5
    connected = await connect_mt5()
    if not connected:
        print("Failed to connect to MetaTrader 5.")
        return

    today = datetime.now()

    if connected:
        while True:
            if 0 <= today.hour <= 21:
                print("Trading session active.")
                for symbol in symbols_list:
                    try:
                        print(f"Processing symbol: {symbol['symbol']}")
                        # Fetch start and current prices
                        start_price = fetch_price(symbol, "start")
                        current_price = fetch_price(symbol, "current")

                        if start_price is None or current_price is None:
                            print(f"Skipping symbol {symbol['symbol']} due to missing price data.")
                            continue

                        # Execute logic
                        await assemble_logic(symbol, start_price, current_price)

                        # Introduce a delay between symbol processing (optional)
                        await asyncio.sleep(1)

                    except Exception as e:
                        print(f"Error processing symbol {symbol['symbol']}: {e}")
            else:
                print("Trades are not allowed outside active hours.")


# Run the main function
asyncio.run(main())
