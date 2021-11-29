from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
    
)

from bson import ObjectId

from models.user import UserModel
from models.alert import AlertModel
from models.stock import StockModel

from flask import jsonify

import datetime

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('first_name', type=str)
_user_parser.add_argument('last_name', type=str)
_user_parser.add_argument('email', type=str)
_user_parser.add_argument('password', type=str)
_user_parser.add_argument('email', type=str)
_user_parser.add_argument('password', type=str)
_user_parser.add_argument('stock_id', type=str)
_user_parser.add_argument('trigger_price', type=float)
_user_parser.add_argument('operation', type=str)
_user_parser.add_argument('alert_type', type=str)
_user_parser.add_argument('MA_period', type=int)

class Alerts(Resource):
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = _user_parser.parse_args()
        alert = AlertModel(stock_id=ObjectId(data['stock_id']), trigger_price=data['trigger_price'], operation=data['operation'], alert_type=data['alert_type'], MA_period=data['MA_period'])
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        user.alerts.append(alert)
        user.save()
        alert_list = []
        for alert in user.alerts:
            if alert.stock_id == ObjectId(data['stock_id']) and alert.triggered == False:
                alert_list.append(alert.json())
        return {'alerts': alert_list}


    @jwt_required()
    def delete(self):
        current_user = get_jwt_identity()
        data = _user_parser.parse_args()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        data_obj = {'stock_id': data['stock_id'], 'trigger_price': data['trigger_price'], 'operation': data['operation'], 'alert_type': data['alert_type'], 'MA_period': data['MA_period']}

        i = 0
        for alert in user.alerts:
            if alert.json() == data_obj:
                user.alerts.pop(i)
                break
            i = i + 1

        user.save()

        return {'message': 'Alert Removed'}

class AlertsList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        alert_list = []
        for alert in user.alerts:
            if alert.triggered == True:
                continue
            stock = StockModel.find_by_id(alert.stock_id).first()
            alert_obj = alert.json()
            alert_obj["ticker"] = stock.ticker
            alert_list.append(alert_obj)
        return {'alerts': alert_list}
    
    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = _user_parser.parse_args()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        alert_list = []
        if data['stock_id']:
            for alert in user.alerts:
                if alert.stock_id == ObjectId(data['stock_id']) and alert.triggered == False:
                    alert_list.append(alert.json())
        else:
            for alert in user.alerts:
                alert_list.append(alert.json())
        return {'alerts': alert_list}

class AlertsCheck(Resource):
    def get(self):
        UserModel.check_all_alerts()
        return {'message': "All alerts have been checked."}