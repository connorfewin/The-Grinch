"""
This will allocate the budget into each market (Stock or Crypto)
"""
import Market

def TotalCash():
    total_cash = Market.TotalCash('Stock') + Market.TotalCash('Crypto')
    return total_cash

def AvailableCash():
    available_cash = Market.AvailableCash('Stock') + Market.AvailableCash('Crypto')
    return available_cash

