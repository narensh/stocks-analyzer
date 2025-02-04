import pandas as pd
import numpy as np
import yfinance as yf
import os

# Configuration
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

# def fetch_stock_data(symbol, start_date, end_date):
#     """
#     Fetch historical stock data from Yahoo Finance.
#     """
#     print("Fetch historical stock data from Yahoo Finance.")
#     data = yf.download(symbol, start=start_date, end=end_date)
#     print("Success in historical stock data fetch from Yahoo Finance.")
#     return data

# Fetch BSE/NSE stock data
def fetch_stock_data(symbol: str, exchange: str = "NSE", period: str = "1y"):
    try:
        if exchange.upper() == "BSE":
            stock_symbol = f"{symbol}.BO"
        else:
            stock_symbol = f"{symbol}.NS"

        data = yf.download(stock_symbol, period=period)
        data.to_csv(os.path.join(DATA_DIR, f"{symbol}_{exchange}.csv"))
        return data
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return None

def calculate_dma(data, window=50, displacement=10):
    """
    Calculate Displaced Moving Average (DMA).
    DMA is an SMA shifted forward by a certain number of periods.
    """
    sma = data['Close'].rolling(window=window).mean()
    dma = sma.shift(displacement)  # Shift forward by 'displacement' days
    return dma

def identify_entry_point(data, dma_short_window=50, dma_long_window=200, displacement=10):
    data['DMA50'] = calculate_dma(data, window=dma_short_window, displacement=displacement)
    data['DMA200'] = calculate_dma(data, window=dma_long_window, displacement=displacement)

    data['Signal'] = 0
    data.iloc[dma_short_window:, data.columns.get_loc('Signal')] = np.where(data['DMA50'].iloc[dma_short_window:] > data['DMA200'].iloc[dma_short_window:], 1, 0)
    data['Entry'] = data['Signal'].diff()

    entry_points = data[data['Entry'] == 1]
    entry_points['Action'] = 'BUY'
    return entry_points

def identify_exit_point(data, dma_short_window=50, dma_long_window=200, displacement=10):
    data['DMA50'] = calculate_dma(data, window=dma_short_window, displacement=displacement)
    data['DMA200'] = calculate_dma(data, window=dma_long_window, displacement=displacement)

    data['Signal'] = 0
    data.iloc[dma_short_window:, data.columns.get_loc('Signal')] = np.where(data['DMA50'].iloc[dma_short_window:] < data['DMA200'].iloc[dma_short_window:], 1, 0)
    data['Exit'] = data['Signal'].diff()

    exit_points = data[data['Exit'] == 1]
    exit_points['Action'] = 'SELL'
    return exit_points