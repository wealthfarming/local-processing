from flask import Blueprint, jsonify, request

from crawlers import MT5DataSource

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

@api_blueprint.route('/crawlers/mt5', methods=['GET'])
def crawlers_mt5():
    return jsonify(MT5DataSource().sync_raw_data_platform())

@api_blueprint.route('/crawlers/daily-logs', methods=['GET'])
def crawlers_data():
    return jsonify(MT5DataSource().fetch_data())

@api_blueprint.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    return jsonify({"received_data": data})
