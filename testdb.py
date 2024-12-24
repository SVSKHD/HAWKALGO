from db import get_symbol_data, save_symbol_data, update_symbol_data


eur_update = {
    'symbol': 'EURUSD',
    'pip_value': 1.0033,
    'threshold': 16,
    'pip_size':0.01,
    'threhsold':1000
}
# data = save_symbol_data('EURUSD', eur)
# eur_data = get_symbol_data('EURUSD')
# print(eur_data)


# data = update_symbol_data('EURUSD', eur_update)
eur_data = get_symbol_data('EURUSD')
print(eur_data)