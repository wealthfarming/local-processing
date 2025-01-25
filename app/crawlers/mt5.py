from .base import DataSource
import MetaTrader5 as mt5
from MetaTrader5 import DEAL_TYPE_BUY, DEAL_TYPE_SELL, DEAL_TYPE_BALANCE
import pandas as pd
from datetime import datetime, timedelta, timezone
import subprocess
import os
import json
import pytz
from database import TrackingDaily, engine, HistoryDealsSeries
from sqlalchemy.orm import sessionmaker
from sqlalchemy import and_
from dotenv import load_dotenv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP

class MT5DataSource(DataSource):
    def __init__(self):
        Session = sessionmaker(bind=engine)
        session = Session()
        self._db_session = session
        pass

    def connect(self):
        load_dotenv(override=True)
        subprocess.run(["taskkill", "/IM", "terminal64.exe", "/F"])

        account = os.environ.get("MT5_EXNESS_ACCOUNT_ID")
        password = os.environ.get("MT5_EXNESS_PASSWORD")
        server = os.environ.get("MT5_EXNESS_SERVER")
        terminal_path = os.environ.get("MT5_TERMINAL_EXNESS_PATH")

        mt5.initialize(path=terminal_path)
        result = mt5.login(account, password, server)

        print("Connecting to MT5 server...", result)

    def pull_data(self):
        # Fetch account information
        account_info = mt5.account_info()
        account_info_dict = account_info._asdict()

        print('.. ... account_info', account_info)
        print('.. ... account_info_dict', account_info_dict)

        history_orders_dict = []
        history_deals_dict  = []

        from_date = datetime(2015, 1, 1)
        to_date = datetime.now() + timedelta(days=1)
        
        history_orders = mt5.history_orders_get(from_date, to_date)
        if history_orders:
            history_orders_dict = [order._asdict() for order in history_orders]
            
        history_deals = mt5.history_deals_get(from_date, to_date)
        if history_deals:
            history_deals_dict = [deal._asdict() for deal in history_deals]

        # Fetch open positions
        positions = mt5.positions_get()
        positions_list = []
        if positions:
            for pos in positions:
                positions_list.append(pos._asdict())

        # Fetch pending orders
        orders = mt5.orders_get()
        orders_list = []
        if orders:
            for order in orders:
                orders_list.append(order._asdict())

        return {
            "account": account_info_dict,
            "positions": positions_list,
            "orders": orders_list,
            "history_orders" : history_orders_dict,
            "history_deals": history_deals_dict
        }

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
                        item[key] = self.format_time(item[key])

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

        # with open("output.json", "w", encoding="utf-8") as json_file:
        #     json.dump(cleaned_data, json_file, indent=4, ensure_ascii=False)

        print(cleaned_data)

        return {"data": json.dumps(cleaned_data)}

    def close_connection(self):
        mt5.shutdown()
        print("Closing connection to MT5 server.")

    def get_data(self):
        self.connect()
        raw_data = self.pull_data()
        cleaned_data = self.clean_data(raw_data)
        return cleaned_data

    def sync_raw_data_platform(self):

        self.connect()
        raw_data = self.pull_data()        
        new_log = TrackingDaily(
            account_logs = raw_data,  # Dữ liệu JSON
            broker_name = raw_data['account']['company'],
            platform_name = "MetaTrader5",
            account_id = raw_data['account']['login']
        )

        self._db_session.add(new_log)
        self._db_session.commit()

        return {
            "status": True,
            "msg" : "Update Success"
        }
    
    def fetch_data(self, where= {}):
        if len(where) > 0:

            logs = self._db_session.query(TrackingDaily).filter_by(**where).all()
            logs_dict = [row.to_dict() for row in logs]
            return {
                "status": True,
                "data": logs_dict,
                "where": where
            }
        

        logs = self._db_session.query(TrackingDaily).all()
        logs_dict = [row.to_dict() for row in logs]

        return {
            "status": True,
            "data": logs_dict,
        }
    
    def find_first(self, where = {}):
        if len(where) > 0:
            item = self._db_session.query(TrackingDaily).filter_by(**where).first()
            if(item):
                item_dict = item.to_dict()
                return {
                    "status": True,
                    "data": item_dict,
                    "where": where
                }

        return {
            "status": False,
            "data": {},
        }

    def format_time(self, timestamp):
        if timestamp and isinstance(timestamp, (int, float)):
            if timestamp > 10000000000:
                timestamp /= 1000
            utc_time = datetime.utcfromtimestamp(timestamp)
            utc_time = pytz.utc.localize(utc_time)
            return utc_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return None
        
    def calculate_balance_at(self, start_time, end_time, initial_balance):
        deals = mt5.history_deals_get(start_time, end_time)
        if deals is None:
            print(f"No deals found, error code: {mt5.last_error()}")
            return initial_balance

        
        balance = initial_balance
        for deal in deals:
            if deal.type in [DEAL_TYPE_BUY, DEAL_TYPE_SELL]:
                balance += deal.profit
            elif deal.type == DEAL_TYPE_BALANCE:
                balance += deal.profit

        return balance
    
    def sync_transform_time_series(self, mt5_login_id):
        log = self.find_first({"account_id": mt5_login_id})
        if log['status'] == False:
            return {
                "status": False
            }

        history_deals = log['data']['account_logs']['history_deals']
        tracking_id = log['data']['id']
        daily_profit = defaultdict(float)
        count_by_date = defaultdict(int)  
        for deal in history_deals:
            deal_date = self.timestamp_to_date(deal["time"])
            daily_profit[deal_date.isoformat()] += deal["profit"]
            count_by_date[deal_date.isoformat()] += 1

        current_balance = 0
        balance_by_date = {}
        for day, profit in sorted(daily_profit.items()):
            current_balance += profit
            number = Decimal(current_balance)
            balance_by_date[day] = float(number.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            
            # insert to history series
            new_time_series = HistoryDealsSeries(
                time_iso = day,
                balance_amount = balance_by_date[day],
                tracking_daily_id = tracking_id,
                tracking_account_id = mt5_login_id
            )

            self._db_session.add(new_time_series)
            self._db_session.commit()

        return {
            "status": True,
            'balance_by_date': balance_by_date,
            'count_by_date': count_by_date,
        }

    def fetch_transform_time_series(self, where = {}):
        if len(where) > 0:

            logs = self._db_session.query(HistoryDealsSeries).filter_by(**where).all()
            logs_dict = [row.to_dict() for row in logs]
            return {
                "status": True,
                "data": logs_dict,
                "where": where
            }
        

        logs = self._db_session.query(HistoryDealsSeries).all()
        logs_dict = [row.to_dict() for row in logs]

        return {
            "status": True,
            "data": logs_dict,
            "where": where
        }

    def timestamp_to_date(self, unix_time):
        return datetime.fromtimestamp(unix_time, tz=timezone.utc).date()
        


