import MetaTrader5 as mt5
import asyncio


async def connect_mt5():
    """Asynchronously initialize and log in to MetaTrader 5."""
    initialized = await asyncio.to_thread(mt5.initialize)
    if not initialized:
        print("Failed to initialize MetaTrader5")
        return False

    login = 213171528  # Replace with actual login
    password = "AHe@Yps3"  # Replace with actual password
    server = "OctaFX-Demo"  # Replace with actual server

    authorized = await asyncio.to_thread(mt5.login, login, password, server)
    if authorized:
        account = await asyncio.to_thread(mt5.account_info)
        balance = account.balance
        print(f"Successfully logged into account {login} on server {server}")
        print(f"balance {balance}")
    if not authorized:
        print(f"Login failed for account {login}")
        return False


    return True


def get_open_positions_count(symbol):
    if not mt5.initialize():
        print("Failed to initialize MetaTrader5.")
        return 0
    try:
        symbol_name = symbol.get('symbol')
        if not symbol_name:
            print("Symbol name is missing in the input.")
            return 0
        positions = mt5.positions_get(symbol_name)
        return len(positions) if positions else 0
    finally:
        mt5.shutdown()
