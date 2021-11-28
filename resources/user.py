from flask_restful import Resource, reqparse
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    
)
from bson import ObjectId

from models.user import UserModel
from models.alert import AlertModel
from models.stock import StockModel
from flask_bcrypt import generate_password_hash, check_password_hash

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


class User(Resource):
    def get(self, user_id: str):
        user = UserModel.find_by_user_id(user_id).first()
        if user:
            return user.json()
        else:
            return {'message': 'Email does not exist'}

    def delete(self, user_id: str):
        user = UserModel.find_by_user_id(user_id).first()
        if user:
            user.delete()
            return {'message': 'User has been deleted'}
        else:
            return {'message': 'Email does not exist.'}

class UserRegister(Resource): 
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data["email"])
        if user:
            return {'message': 'Email is already taken.'}
        else:
            user = UserModel(first_name=data['first_name'], last_name=data['last_name'], email=data['email'].lower(), password=generate_password_hash(data['password']))
            user.save()
            access_token = create_access_token(
                identity={'user_id': str(user.id)},
                expires_delta= datetime.timedelta(days=7)
                )
            user.send_email(access_token)
            return {"message": "Data saved"}

class UserLogin(Resource):
    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data["email"].lower()).first()
        if user:
            check_password = check_password_hash(user.password, data['password'])
            if check_password:
                if not user.verification:
                    return {'message': "Your account has not been verified. Please verify your account before logging in."}
                access_token = create_access_token(
                    identity={
                        'user_id': str(user.id), 
                        'email': user.email
                        },
                    fresh=True
                    )
                refresh_token = create_refresh_token(
                    identity={
                        'user_id': str(user.id), 
                        'email': user.email
                        })
                return {
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'expiry_time': str(datetime.datetime.now() + datetime.timedelta(minutes=15))
                }
            else:
                return {"message": "You have entered an invalid password. Please try again."}
        else:
            return {"message": "You have entered an invalid email address. Please try again."}

class CheckToken(Resource):
    @jwt_required()
    def post (self):
        return {'msg': "Verification success"}

class TokenRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.

        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {
            'access_token': new_token,
            'expiry_time': str(datetime.datetime.now() + datetime.timedelta(minutes=15))
            }, 200

# class UserFavourites(Resource):
#     @jwt_required()
#     def get(self):
#         current_user = get_jwt_identity()
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         fav_list = []
#         for favourite in user.favourites_list:
#             fav_list.append(str(favourite))
#         print(fav_list)
#         return {'fav_list': fav_list}

#     @jwt_required()
#     def post(self):
#         current_user = get_jwt_identity()
#         data = _user_parser.parse_args()
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         stock = StockModel.find_by_id(data['stock_id']).first()
#         if not stock:
#             return {'msg': "Stock id does not exist."}

#         if user.favourites_list.count(ObjectId(data['stock_id'])) == 0:
#             user.favourites_list.append(ObjectId(data['stock_id']))
#             user.save()
#             return {'favourite': True}
#         else:
#             user.favourites_list.remove(ObjectId(data['stock_id']))
#             user.save()
#             return {'favourite': False}

#     @jwt_required()
#     def delete(self):
#         current_user = get_jwt_identity()
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         # user = UserModel.find_by_user_id(user_id).first()
#         # user.remove_from_fav(ticker)
#         return {}

# class UserAlerts(Resource):
#     #Don't need this API. Wanted to see if alert checking works.
#     # @jwt_required()
#     # def get(self):
#     #     current_user = get_jwt_identity()
#     #     user = UserModel.find_by_user_id(current_user['user_id']).first()
#     #     for alert in user.alerts:
#     #         print(alert.check_alert())

#     #     return{}

#     @jwt_required()
#     def get(self):
#         current_user = get_jwt_identity()
#         data = _user_parser.parse_args()
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         alert_list = []
#         if data['stock_id']:
#             for alert in user.alerts:
#                 if alert.stock_id == ObjectId(data['stock_id']):
#                     alert_list.append(alert.json())
#         else:
#             for alert in user.alerts:
#                 alert_list.append(alert.json())
#         return 


#     @jwt_required()
#     def post(self):
#         current_user = get_jwt_identity()
#         data = _user_parser.parse_args()
#         alert = AlertModel(stock_id=ObjectId(data['stock_id']), trigger_price=data['trigger_price'], operation=data['operation'], alert_type=data['alert_type'], MA_period=data['MA_period'])
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         user.alerts.append(alert)
#         user.save()
#         alert_list = []
#         for alert in user.alerts:
#             if alert.stock_id == ObjectId(data['stock_id']):
#                 alert_list.append(alert.json())
#         return {'alerts': alert_list}


#     @jwt_required()
#     def delete(self):
#         current_user = get_jwt_identity()
#         data = _user_parser.parse_args()
#         user = UserModel.find_by_user_id(current_user['user_id']).first()
#         data_obj = {'stock_id': ObjectId(data['stock_id']), 'trigger_price': data['trigger_price'], 'operation': data['operation'], 'alert_type': data['alert_type'], 'MA_period': data['MA_period']}

#         i = 0
#         for alert in user.alerts:
#             if alert.json() == data_obj:
#                 user.alerts.pop(i)
#                 break
#             i = i + 1

#         user.save()

#         return {'message': 'Alert Removed'}

class UserVerify(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        user.verification = True
        user.save()
        return {'message': "Your account has been verified."}

    def post(self):
        data = _user_parser.parse_args()
        user = UserModel.find_by_email(data['email']).first()
        if user:
            access_token = create_access_token(
                identity={'user_id': str(user.id)},
                expires_delta= datetime.timedelta(days=7)
                )
            user.send_email(access_token)
            return {'msg': "New link has been sent to your email."}
        else:
            return {'msg': "This email does not exists. Please verify your email."}


#Don't need this API. Wanted to see if alert checking works.
class UserCheckAlerts(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_user_id(current_user['user_id']).first()
        for alert in user.alerts:
            print(alert.check_alert())