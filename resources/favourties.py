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

class Favourites(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        fav_list = []
        for favourite in user.favourites_list:
            fav_list.append(str(favourite))
        print(fav_list)
        return {'fav_list': fav_list}

    @jwt_required()
    def post(self):
        current_user = get_jwt_identity()
        data = _user_parser.parse_args()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        stock = StockModel.find_by_id(data['stock_id']).first()
        if not stock:
            return {'msg': "Stock id does not exist."}

        if user.favourites_list.count(ObjectId(data['stock_id'])) == 0:
            user.favourites_list.append(ObjectId(data['stock_id']))
            user.save()
            return {'favourite': True}
        else:
            user.favourites_list.remove(ObjectId(data['stock_id']))
            user.save()
            return {'favourite': False}

class FavouritesList(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        fav_list = []
        for favourite in user.favourites_list:
            stock = StockModel.find_by_id(favourite).first()
            stock_data = {
                '_id': str(stock.id), 
                'ticker': stock.ticker, 
                'full_name': stock.full_name, 
                'hist_data': [stock.hist_data[-2], stock.hist_data[-1]]
                }
            fav_list.append(stock_data)
        return {'fav_list': fav_list}