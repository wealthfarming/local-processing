from .base import DataSource
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import requests
import subprocess
import os
import json

account = 5033013189  # Replace with your demo account number
password = "8-WwAaIk"  # Replace with your demo account password
server = "MetaQuotes-Demo"  # Replace with your broker's server name


# # Get account info
# account = os.getenv("MT5_ID")
# password = os.getenv("MT5_PASSWORD")
# server = os.getenv("MT5_SERVER")


def format_time(timestamp):
    if timestamp and isinstance(timestamp, (int, float)):
        if timestamp > 10000000000:
            timestamp /= 1000
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
    else:
        return None


class MT5DataSource(DataSource):
    def connect(self):
        subprocess.run(["taskkill", "/IM", "terminal64.exe", "/F"])

        mt5.initialize()
        mt5.login(account, password, server)

        print("Connecting to MT5 server...")

    def pull_data(self):
        # Fetch account information
        account_info = mt5.account_info()
        print("....", account_info._asdict())
        account_info_dict = account_info._asdict()

        from_date = datetime(2015, 1, 1)
        to_date = datetime.now() + timedelta(days=1)

        history_orders = mt5.history_orders_get(from_date, to_date)

        if history_orders:
            orders_dict_list = [order._asdict() for order in history_orders]
        else:
            orders_dict_list = []

        account_info_dict["history_orders"] = orders_dict_list

        # # Fetch open positions
        # positions = mt5.positions_get()
        # positions_list = []
        # if positions:
        #     for pos in positions:
        #         positions_list.append(pos._asdict())

        # # Fetch pending orders
        # orders = mt5.orders_get()
        # orders_list = []
        # if orders:
        #     for order in orders:
        #         orders_list.append(order._asdict())

        # account_info_dict["Positions"] = positions_list
        # account_info_dict["PendingOrders"] = orders_list

        print("account_info_dict", account_info_dict)
        return account_info_dict

    def clean_data(self, account_info_dict):
        print("Cleaning MT5 data...")

        cleaned_data = account_info_dict.copy()

        # for pos in cleaned_data.get("Positions", []):
        #     for key in ["time", "time_update", "time_msc", "time_update_msc"]:
        #         if key in pos and pos[key]:
        #             pos[key] = format_time(pos[key])

        # for order in cleaned_data.get("PendingOrders", []):
        #     for key in ["time", "time_update", "time_msc", "time_update_msc"]:
        #         if key in order and order[key]:
        #             order[key] = format_time(order[key])

        cleaned_data = {
            key: value for key, value in cleaned_data.items() if value is not None
        }

        # with open("output.json", "w") as json_file:
        #     json.dump(cleaned_data, json_file, indent=4)

        print(cleaned_data)

        return {"data": cleaned_data}

    def close_connection(self):
        mt5.shutdown()
        print("Closing connection to MT5 server.")
