import MetaTrader5 as mt5


def get_open_positions_count(symbol):
    if not mt5.initialize():
        print("Failed to initialize MetaTrader5.")
        return 0
    try:
        symbol_name = symbol.get('symbol')
        if not symbol_name:
            print("Symbol name is missing in the input.")
            return 0
        positions = mt5.positions_get(symbol=symbol_name)
        return len(positions) if positions else 0
    finally:
        mt5.shutdown()
