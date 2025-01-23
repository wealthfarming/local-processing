from .base import DataSource
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import requests
import subprocess
import os
import json
import pytz

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
        utc_time = datetime.utcfromtimestamp(timestamp)
        utc_time = pytz.utc.localize(utc_time)
        return utc_time.strftime("%Y-%m-%d %H:%M:%S")
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
        # Fetch account history order
        history_orders = mt5.history_orders_get(from_date, to_date)

        if history_orders:
            orders_dict_list = [order._asdict() for order in history_orders]
        else:
            orders_dict_list = []

        account_info_dict["history_orders"] = orders_dict_list
        # Fetch account history deal

        history_deals = mt5.history_deals_get(from_date, to_date)

        if history_deals:
            deal_dict_list = [deal._asdict() for deal in history_deals]
        else:
            deal_dict_list = []

        account_info_dict["history_deals"] = deal_dict_list

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
        # with open("output_raw.json", "w", encoding="utf-8") as json_file:
        #     json.dump(account_info_dict, json_file, indent=4, ensure_ascii=False)
        print("account_info_dict", account_info_dict)
        return account_info_dict

    def clean_data(self, account_info_dict):
        print("Cleaning MT5 data...")

        cleaned_data = account_info_dict.copy()

        for key_group in [
            "Positions",
            "PendingOrders",
            "history_orders",
            "history_deals",
        ]:
            for item in cleaned_data.get(key_group, []):
                for key in [
                    "time",
                    "time_update",
                    "time_msc",
                    "time_update_msc",
                    "time_done_msc",
                    "time_done",
                    "time_setup",
                    "time_setup_msc",
                ]:
                    if key in item and item[key]:
                        item[key] = format_time(item[key])

        orders = cleaned_data.get("history_orders", [])
        deals = cleaned_data.get("history_deals", [])
        trade_history = []

        deal_dict = {}
        for deal in deals:
            position_id = deal.get("position_id")
            if position_id not in deal_dict:
                deal_dict[position_id] = []
            deal_dict[position_id].append(deal)

        order_fields = [
            "time_done_msc",
            "price_open",
            "volume_initial",
            "sl",
            "tp",
            "price_stoplimit",
        ]
        deal_fields = ["time_msc", "price", "volume", "profit"]

        for order in orders:
            position_id = order.get("position_id")
            symbol = order.get("symbol")
            order_type = order.get("type")

            linked_deals = deal_dict.get(position_id, [])

            for deal in linked_deals:
                if deal.get("symbol") == symbol:
                    trade_entry = {
                        "symbol": symbol,
                        "position_id": position_id,
                        "order_type": order_type,  # type = 0 : BUY, type = 1 : SELL
                    }

                    for field in order_fields:
                        trade_entry[f"order_{field}"] = order.get(field)

                    # Add fields from deal
                    for field in deal_fields:
                        trade_entry[f"deal_{field}"] = deal.get(field)

                    if (
                        trade_entry["order_time_done_msc"]
                        == trade_entry["deal_time_msc"]
                    ):
                        continue
                    trade_history.append(trade_entry)

        cleaned_data["trade_history"] = trade_history

        fields_to_exclude = ["history_orders", "history_deals"]

        cleaned_data = {
            key: value
            for key, value in cleaned_data.items()
            if key not in fields_to_exclude and value is not None
        }

        with open("output.json", "w", encoding="utf-8") as json_file:
            json.dump(cleaned_data, json_file, indent=4, ensure_ascii=False)

        print(cleaned_data)

        return {"data": cleaned_data}

    def close_connection(self):
        mt5.shutdown()
        print("Closing connection to MT5 server.")
