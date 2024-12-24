from db import get_symbol_data

eur_symbol_data = get_symbol_data('EURUSD')
print("eur", eur_symbol_data)