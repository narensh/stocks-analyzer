import os
import pandas as pd
import yfinance as yf
import investpy
from flask import Flask, jsonify, request
import subprocess
import numpy as np
import streamlit as st
from constants import *

from strategy import fetch_stock_data, identify_entry_point, identify_exit_point

# # Fetch BSE/NSE stock data
# def fetch_stock_data(symbol: str, exchange: str = "NSE", period: str = "1y"):
#     try:
#         if exchange.upper() == "BSE":
#             stock_symbol = f"{symbol}.BO"
#         else:
#             stock_symbol = f"{symbol}.NS"
#
#         data = yf.download(stock_symbol, period=period)
#         data.to_csv(os.path.join(DATA_DIR, f"{symbol}_{exchange}.csv"))
#         return data
#     except Exception as e:
#         print(f"Error fetching {symbol}: {e}")
#         return None

# Fetch fundamental data
def fetch_fundamental_data(symbol: str, exchange: str = "NSE"):
    try:
        stock = investpy.get_stock_company_profile(symbol, country="India")
        return stock
    except Exception as e:
        print(f"Error fetching fundamental data for {symbol}: {e}")
        return None

# Stock Selection Algorithm
def select_stocks(stock_list):
    selected_stocks = []
    for stock in stock_list:
        data = fetch_stock_data(stock)
        if data is not None:
            moving_avg = data['Close'].rolling(window=50).mean().iloc[-1]
            rsi = np.mean(data['Close'].diff().dropna() > 0) * 100
            if moving_avg and rsi > 50:
                selected_stocks.append(stock)
    return selected_stocks

# Exit Strategy
def exit_strategy(stock, threshold=10):
    data = fetch_stock_data(stock)

    if data is not None and not data.empty:
        print(data.tail())  # Debugging: Print last few rows
        print(f"Data type of 'Close' column: {type(data['Close'])}")

        # Extract the latest closing price correctly
        current_price = data["Close"].iloc[-1]
        if isinstance(current_price, pd.Series):
            current_price = current_price.values[0]  # Ensure scalar value

        # Compute the average price correctly
        avg_price = data["Close"].mean()
        if isinstance(avg_price, pd.Series):
            avg_price = avg_price.values[0]  # Ensure scalar value

        print(f"Current Price: {current_price}, Type: {type(current_price)}")
        print(f"Average Price: {avg_price}, Type: {type(avg_price)}")

        if float(current_price) > float(avg_price) * (1 + threshold / 100):  # Ensure float comparison
            return "Sell"
        elif float(current_price) < float(avg_price) * (1 - threshold / 100):
            return "Stop Loss"
        else:
            return "Hold"

    return "Data Unavailable"


# CLI Command to fetch stock data
def cli_fetch_data(symbol, exchange):
    data = fetch_stock_data(symbol, exchange)
    if data is not None:
        print(f"Fetched data for {symbol} ({exchange})")
    
# Flask Web API
tool_app = Flask(__name__)

@tool_app.route("/fetch_stock", methods=["GET"])
def api_fetch_stock():
    symbol = request.args.get("symbol")
    exchange = request.args.get("exchange", "NSE")
    data = fetch_stock_data(symbol, exchange)
    if data is not None:
        return jsonify({"message": f"Fetched {symbol} data successfully."})
    return jsonify({"error": "Failed to fetch stock data."}), 400

@tool_app.route("/select_stocks", methods=["POST"])
def api_select_stocks():
    stock_list = request.json.get("stocks", [])
    selected = select_stocks(stock_list)
    return jsonify({"selected_stocks": selected})

@tool_app.route("/exit_strategy", methods=["GET"])
def api_exit_strategy():
    stock = request.args.get("stock")
    decision = exit_strategy(stock)
    return jsonify({"stock": stock, "decision": decision})

# Streamlit Web UI
def run_streamlit_ui():
    st.title("Stock Analysis Tool")
    stock = st.text_input("Enter Stock Symbol")
    if st.button("Fetch Data"):
        data = fetch_stock_data(stock)
        st.write(data.tail())
    if st.button("Check Exit Strategy"):
        decision = exit_strategy(stock)
        st.write(f"Decision: {decision}")


def show_entry_and_exit_points_for_symbols(symbols, exchange, period=ONE_YEAR):
    entry_points_list = []
    exit_points_list = []

    for symbol in symbols:
        print(f"\nProcessing {symbol} ({exchange})")

        # Fetch Data
        data = fetch_stock_data(symbol, exchange, period)
        if data is None or data.empty:
            print(f"Failed to fetch data for {symbol}")
            continue

        # Ensure 'Date' column is included
        data.reset_index(inplace=True)

        # Identify Entry and Exit Points
        entry_points = identify_entry_point(data)
        exit_points = identify_exit_point(data)

        # Add symbol column
        entry_points['Symbol'] = symbol
        exit_points['Symbol'] = symbol

        # Append to list
        entry_points_list.append(entry_points[['Date', 'Symbol', 'Close', 'DMA50', 'DMA200', 'Action']])
        exit_points_list.append(exit_points[['Date', 'Symbol', 'Close', 'DMA50', 'DMA200', 'Action']])

    # Concatenate all results
    all_entry_points = pd.concat(entry_points_list)
    all_exit_points = pd.concat(exit_points_list)

    # Display Results
    print("\n📈 Entry Points:")
    print(all_entry_points)

    print("\n📉 Exit Points:")
    print(all_exit_points)

# Example usage
if __name__ == "__main__":
    stock_symbols = ["BEL", "RELIANCE", "TCS"]
    show_entry_and_exit_points_for_symbols(stock_symbols, NSE)