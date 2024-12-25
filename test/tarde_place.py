import asyncio
# import MetaTrader5 as mt5

TRADE_LIMIT = 2  # Define the maximum number of trades allowed


async def get_open_positions_count(symbol):
    """
    Fetch the count of open positions for a given symbol.
    :param symbol: Trading symbol (e.g., 'EURUSD').
    :return: Count of open positions.
    """
    open_positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol['symbol'])
    return len(open_positions) if open_positions else 0


async def trade_place(symbol, trade_type, lot=None, hedge=False):
    """
    Place trades according to the defined trade limit, with optional hedging.
    :param symbol: Dictionary containing trading symbol information (e.g., 'EURUSD').
    :param trade_type: 'buy' or 'sell'.
    :param lot: Trade lot size (default is taken from symbol if not provided).
    :param hedge: Whether to place double the trades for hedging.
    :return: Updated trade count.
    """
    symbol_name = symbol['symbol']
    lot = lot if lot is not None else symbol['lot']  # Use default lot if not provided
    effective_trade_limit = TRADE_LIMIT * 2 if hedge else TRADE_LIMIT

    # Get the current number of open positions
    current_positions = await get_open_positions_count(symbol)

    # Enforce trade limit
    if current_positions >= effective_trade_limit:
        print(f"No trade placed: Trade limit of {effective_trade_limit} reached for {symbol_name}.")
        return current_positions

    # Determine order type
    order_type = "BUY" if trade_type == 'buy' else "SELL"

    # Simulate trade placement (replace with MetaTrader5 execution)
    trades_to_place = 2 if hedge else 1  # Double trades for hedging
    for i in range(trades_to_place):
        print(f"Placing {order_type} trade for {symbol_name} with lot size {lot}. Trade count: {current_positions + 1}")
        current_positions += 1
        if current_positions >= effective_trade_limit:
            print(f"Reached the effective trade limit ({effective_trade_limit}) during hedging.")
            break

    # Construct and execute trade request (if using MetaTrader5)

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_name,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if trade_type == 'buy' else mt5.ORDER_TYPE_SELL,
        "price": mt5.symbol_info_tick(symbol_name).ask if trade_type == 'buy' else mt5.symbol_info_tick(symbol_name).bid,
        "deviation": 10,
        "magic": 234000,
        "comment": "Python script open",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_FOK,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Failed to place trade: {result.comment}")
    else:
        print(f"Trade successfully placed. Result: {result}")


    return current_positions


async def close_trades_by_symbol(symbol):
    """
    Close all open positions for a given symbol.
    :param symbol: Dictionary containing trading symbol information.
    """
    symbol_name = symbol['symbol']
    open_positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol_name)

    if not open_positions:
        print(f"No open positions for {symbol_name}.")
        return

    for position in open_positions:
        ticket = position.ticket
        lot = position.volume
        trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        symbol_info = await asyncio.to_thread(mt5.symbol_info, symbol_name)

        if not symbol_info:
            print(f"Symbol {symbol_name} not found.")
            continue

        price = symbol_info.bid if trade_type == mt5.ORDER_TYPE_SELL else symbol_info.ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol_name,
            "volume": lot,
            "type": trade_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Closing trade by script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = await asyncio.to_thread(mt5.order_send, close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            message = f"Failed to close trade {ticket} for {symbol_name}, error code: {result.retcode}"
        else:
            message = f"Successfully closed trade {ticket} for {symbol_name}."

        print(message)


async def close_trades_by_symbol(symbol):
    symbol_name = symbol['symbol']
    open_positions = await asyncio.to_thread(mt5.positions_get, symbol=symbol)

    if open_positions is None or len(open_positions) == 0:
        print(f"No open positions for {symbol}.")
        return

    for position in open_positions:
        ticket = position.ticket
        lot = position.volume
        trade_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY
        symbol_info = await asyncio.to_thread(mt5.symbol_info, symbol)

        if symbol_info is None:
            print(f"Symbol {symbol} not found.")
            continue

        price = symbol_info.bid if trade_type == mt5.ORDER_TYPE_SELL else symbol_info.ask

        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot,
            "type": trade_type,
            "position": ticket,
            "price": price,
            "deviation": 20,
            "magic": 123456,
            "comment": "Closing trade by script",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = await asyncio.to_thread(mt5.order_send, close_request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            message = f"Failed to close trade {ticket} for {symbol}, error code: {result.retcode}"
        else:
            message = f"Successfully closed trade {ticket} for {symbol}."

        print(message)
        # await send_discord_message_trade_async(message)



# Symbol configuration
eur = {'symbol': 'EURUSD', 'pip_value': 0.0001, 'threshold': 15, 'lot': 5.0}

# Example usage
async def main():
    current_trades = await trade_place(eur, "sell", 0.1, hedge=False)  # Place first trade
    current_trades = await trade_place(eur, "sell", 0.1, hedge=False)  # Place second trade
    current_trades = await trade_place(eur, "sell", 0.1, hedge=False)  # Attempt third trade (should not be placed)
    # Testing hedging
    current_trades = await trade_place(eur, "buy", None, hedge=True)  # Hedge: Double trades

# Run the script
# asyncio.run(main())