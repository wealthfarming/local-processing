from flask import Blueprint, jsonify, request
from datetime import datetime, time, timedelta
from crawlers import MT5DataSource
from pathlib import Path

from dotenv import load_dotenv
import os
import pandas as pd
from utilities import get_exness_mt5_accounts, get_vantage_mt5_accounts

api_blueprint = Blueprint("api", __name__)
load_dotenv(override=True)

# ----------CRON JOB
@api_blueprint.route("/cron/sync-realtime-equity", methods=["GET"])
def sync_realtime_equity():
    exness_accounts = get_exness_mt5_accounts()
    vantage_accounts = get_vantage_mt5_accounts()
    
    exness_terminal_path = os.environ.get("MT5_TERMINAL_EXNESS_PATH")
    vantage_terminal_path = os.environ.get("MT5_TERMINAL_VANTAGE_PATH")    

    MT5DataSource().sync_realtime_equity(exness_accounts, exness_terminal_path)
    MT5DataSource().sync_realtime_equity(vantage_accounts, vantage_terminal_path)
    return jsonify({
        "status": True,
        "msg": "Success"
    })
# ----------------- DAPP
@api_blueprint.route("/dapp/equity", methods=["GET"])
def dapp_equity():
    pass
