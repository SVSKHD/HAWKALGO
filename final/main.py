from config import symbols_list

hedging={}
last_actions ={}


def main():
    for symbol in symbols_list:
        symbol_name = symbol['symbol']

        # Initialize hedging and last_action for the symbol if not already set
        if symbol_name not in hedging:
            hedging[symbol_name] = {'positive_hedging': False, 'negative_hedging': False}
        if symbol_name not in last_actions:
            last_actions[symbol_name] = None