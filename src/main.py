import os
import pandas as pd
import yfinance as yf
import investpy
from flask import Flask, jsonify, request
import subprocess
import numpy as np
import streamlit as st

# Configuration
DATA_DIR = "./data"
os.makedirs(DATA_DIR, exist_ok=True)

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
    if data is not None:
        current_price = data['Close'].iloc[-1]
        avg_price = data['Close'].mean()
        if current_price > avg_price * (1 + threshold / 100):
            return "Sell"
        elif current_price < avg_price * (1 - threshold / 100):
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

# Podman Deployment Command
def deploy_podman():
    subprocess.run(["podman", "build", "-t", "stock-analysis", "."])
    subprocess.run(["podman", "run", "-p", "5000:5000", "stock-analysis"])

if __name__ == "__main__":
    print("Stock Analysis Tool CLI")
    run_streamlit_ui()
#     print("1. Fetch Stock Data (CLI)")
#     print("2. Fetch Fundamental Data")
#     print("3. Start Web API")
#     print("4. Deploy via Podman")
#     print("5. Run Web UI")
#     choice = input("Select option: ")
#
#     if choice == "1":
#         sym = input("Enter Stock Symbol: ")
#         exch = input("Enter Exchange (NSE/BSE): ")
#         cli_fetch_data(sym, exch)
#     elif choice == "2":
#         sym = input("Enter Stock Symbol: ")
#         exch = input("Enter Exchange (NSE/BSE): ")
#         print(fetch_fundamental_data(sym, exch))
#     elif choice == "3":
#         tool_app.run(host="0.0.0.0", port=5000)
#     elif choice == "4":
#         deploy_podman()
#     elif choice == "5":
#         run_streamlit_ui()

