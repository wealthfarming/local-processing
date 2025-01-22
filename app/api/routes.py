from flask import Blueprint, jsonify, request

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/hello', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello, World!"})

@api_blueprint.route('/data', methods=['POST'])
def receive_data():
    data = request.json
    return jsonify({"received_data": data})
