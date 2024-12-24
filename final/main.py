from config import symbols_list
from fetch import fetch_price
from logic import process_single_price
from datetime import datetime
import asyncio
from notifications import send_discord_message_type

# State management for hedging and last actions
hedging = {}
last_actions = {}




async def initialize_symbol_state(symbol_name):
    """Initialize hedging and last action states for a symbol."""
    if symbol_name not in hedging:
        hedging[symbol_name] = {'positive_hedging': False, 'negative_hedging': False}
    if symbol_name not in last_actions:
        last_actions[symbol_name] = None

async def handle_symbol(symbol):
    symbol_name = symbol['symbol']

    # Initialize symbol state
    await initialize_symbol_state(symbol_name)

    # Fetch prices
    start_price = fetch_price(symbol, "start")
    current_price = fetch_price(symbol, "current")

    message = f"Symbol: {symbol_name}, Start Price: {start_price}, Current Price: {current_price}"
    await send_discord_message_type(message, "general", True)

    # Process and execute trading logic
    if start_price and current_price:
        hedging[symbol_name], last_actions[symbol_name] = await process_single_price(
            symbol, start_price, current_price, hedging[symbol_name], last_actions[symbol_name]
        )

async def main():
    """Main trading loop."""
    while True:
        current_time = datetime.now()

        # Trading hours check
        if 0 <= current_time.hour <= 21:
            tasks = [handle_symbol(symbol) for symbol in symbols_list]
            await asyncio.gather(*tasks)  # Process all symbols concurrently
            await asyncio.sleep(1)  # Sleep between iterations
        else:
            print(f"Outside trading hours. Current time: {current_time}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
