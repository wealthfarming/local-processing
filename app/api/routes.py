from flask import Blueprint, jsonify, request
from datetime import datetime, time, timedelta
from crawlers import MT5DataSource

api_blueprint = Blueprint("api", __name__)


@api_blueprint.route("/hello", methods=["GET"])
def hello_world():
    return jsonify({"message": "Hello, World!"})


@api_blueprint.route("/crawlers/mt5", methods=["GET"])
def crawlers_mt5():
    return jsonify(MT5DataSource().sync_raw_data_platform())

@api_blueprint.route('/crawlers/daily-logs', methods=['GET'])
def crawlers_data():
    return jsonify(MT5DataSource().fetch_data())


@api_blueprint.route("/crawlers/mt5/sync-history-deals", methods=["GET"])
def crawlers_mt5_sync_history_deals():
    return jsonify(MT5DataSource().sync_transform_time_series("404559882"))

@api_blueprint.route("/crawlers/mt5/history-balance-series", methods=["GET"])
def crawlers_mt5_history_balance_series():
    return jsonify(MT5DataSource().fetch_transform_time_series({"tracking_account_id": "404559882"}))

@api_blueprint.route("/time-gmt-0", methods=["GET"])
def time_gmt_0():
    current_date = datetime.utcnow().date()
    time_from = datetime.combine(current_date, time(0, 0, 0)) 

    # Cuối ngày (23:59:59)
    time_to = datetime.combine(current_date, time(23, 59, 59))
    return jsonify({
        "time_from": time_from,
        "time_to": time_to,
    })
